from typing import Any, cast

import pytest

pytest.importorskip("airflow")

from airflow.models.dag import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow_pydantic import Dag, Task

from airflow_config import Configuration


class GeneratesControlDags(EmptyOperator):
    generates_dags = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        control = DAG(dag_id=f"{self.task_id}-control", schedule=None)
        EmptyOperator(task_id="control", dag=control)
        cast(Any, self.dag)._generated_dags = {control.dag_id: control}


def configuration():
    return Configuration(dags={"main": Dag(dag_id="main", tasks={"service": Task(task_id="service", operator=GeneratesControlDags)})})


def test_in_memory_generation_registers_control_dags(tmp_path):
    namespace = {"config": configuration(), "directory": tmp_path}
    exec("config.generate_in_mem(directory)", namespace)  # noqa: S102
    assert namespace["service-control"].get_task("control")
    assert namespace["main"].get_task("service")


@pytest.mark.parametrize("airflow_major_version", [2, 3])
def test_file_generation_registers_control_dags(tmp_path, airflow_major_version):
    configuration().generate(tmp_path, airflow_major_version=airflow_major_version)
    source = (tmp_path / "main.py").read_text()
    namespace = {}
    exec(compile(source, "main.py", "exec"), namespace)  # noqa: S102
    assert namespace["service-control"].get_task("control")
    assert namespace["dag"].get_task("service")


@pytest.mark.parametrize("generation", ["memory", "file"])
def test_generated_control_id_cannot_replace_configured_dag(tmp_path, generation):
    config = configuration()
    config.dags["service-control"] = Dag(dag_id="service-control", tasks={"main": Task(task_id="main", operator=EmptyOperator)})
    with pytest.raises(ValueError, match="service-control"):
        if generation == "memory":
            exec("config.generate_in_mem(directory)", {"config": config, "directory": tmp_path})  # noqa: S102
        else:
            config.generate(tmp_path, airflow_major_version=2)
            exec((tmp_path / "main.py").read_text(), {})  # noqa: S102


@pytest.mark.parametrize("generation", ["memory", "file"])
def test_generated_control_id_cannot_replace_module_global(tmp_path, generation):
    config = configuration()
    existing = object()
    namespace = {"config": config, "directory": tmp_path, "service-control": existing}
    with pytest.raises(ValueError, match="service-control"):
        if generation == "memory":
            exec("config.generate_in_mem(directory)", namespace)  # noqa: S102
        else:
            config.generate(tmp_path, airflow_major_version=2)
            exec((tmp_path / "main.py").read_text(), namespace)  # noqa: S102
    assert namespace["service-control"] is existing
