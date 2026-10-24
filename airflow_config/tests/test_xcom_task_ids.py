from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from airflow_pydantic.migration import _airflow_3
from omegaconf import OmegaConf

from airflow_config import load_config


@pytest.mark.parametrize("separator", ["_", "-"])
@pytest.mark.parametrize("construction", ["rendered", "instantiated"])
@pytest.mark.parametrize("context_name", ["ti", "task_instance"])
def test_xcom_templates_preserve_configured_task_ids(tmp_path: Path, has_airflow, separator, construction, context_name):
    producer = f"produce{separator}value"
    consumer = f"consume{separator}value"
    command = "echo {{ " + context_name + ".xcom_pull(task_ids='" + producer + "') }}"
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    data = {
        "_target_": "airflow_config.Configuration",
        "dags": {
            "xcom-check": {
                "schedule": None,
                "start_date": "2025-01-01",
                "tasks": {
                    producer: {"_target_": "airflow_pydantic.BashTask", "bash_command": "echo payload"},
                    consumer: {"_target_": "airflow_pydantic.BashTask", "bash_command": command, "dependencies": [producer]},
                },
            }
        },
    }
    (config_dir / "config.yaml").write_text("# @package _global_\n" + OmegaConf.to_yaml(OmegaConf.create(data)))
    config = load_config("config", "config", basepath=str(tmp_path / "entry.py"))
    model = config.dags["xcom-check"]
    if construction == "rendered":
        namespace = {}
        exec(model.render(airflow_major_version=3 if _airflow_3() else 2), namespace)  # noqa: S102
        dag = namespace["dag"]
    else:
        dag = model.instantiate()

    assert set(dag.task_ids) == {producer, consumer}
    task = dag.get_task(consumer)
    assert task.upstream_task_ids == {producer}
    ti = SimpleNamespace(xcom_pull=Mock(spec=lambda **kwargs: None, return_value="payload"))
    task.render_template_fields({context_name: ti})
    assert task.bash_command == "echo payload"
    ti.xcom_pull.assert_called_once_with(task_ids=producer)
