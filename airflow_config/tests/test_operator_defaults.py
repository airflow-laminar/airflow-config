from datetime import UTC, datetime

import pytest
from airflow_pydantic import BashTask, Dag, PythonTask, SSHTask

from airflow_config import Configuration


@pytest.mark.parametrize("operator", ["airflow_pydantic.BashTask", "airflow_config.BashTask"])
def test_operator_defaults_preserve_explicit_task_values(operator):
    config = Configuration(
        default_operator_args=[{"operator": operator, "cwd": "/shared", "env": {"SHARED": "yes"}}],
        dags={
            "test": Dag(
                dag_id="test",
                tasks={
                    "default": BashTask(task_id="default", bash_command="pwd"),
                    "explicit": BashTask(task_id="explicit", bash_command="pwd", cwd="/custom", env=None),
                    "other": PythonTask(task_id="other", python_callable="builtins.print"),
                },
            )
        },
    )
    tasks = config.dags["test"].tasks
    assert tasks is not None
    assert isinstance(tasks["default"], BashTask)
    assert isinstance(tasks["explicit"], BashTask)
    assert tasks["default"].cwd == "/shared"
    assert tasks["default"].env == {"SHARED": "yes"}
    assert tasks["explicit"].cwd == "/custom"
    assert tasks["explicit"].env is None
    assert "cwd" not in tasks["other"].model_dump()


def test_later_rules_override_earlier_defaults_without_sharing_mutable_values():
    config = Configuration(
        default_operator_args=[
            {"operator": "airflow_pydantic.BashTask", "cwd": "/first", "env": {"SHARED": "yes"}},
            {"operator": "airflow_pydantic.BashTask", "cwd": "/last"},
        ],
        dags={"test": Dag(dag_id="test", tasks={name: BashTask(task_id=name, bash_command="pwd") for name in ["one", "two"]})},
    )
    tasks = config.dags["test"].tasks
    assert tasks is not None
    one, two = tasks["one"], tasks["two"]
    assert isinstance(one, BashTask) and isinstance(two, BashTask)
    assert one.cwd == two.cwd == "/last"
    assert one.env is not None
    one.env["SHARED"] = "changed"
    assert two.env == {"SHARED": "yes"}


def test_defaults_match_airflow_operator_class_and_reach_instantiated_dag(has_airflow):
    from airflow.providers.standard.operators.bash import BashOperator

    config = Configuration(
        default_operator_args=[{"operator": BashOperator, "cwd": "/shared"}],
        dags={
            "test": Dag(
                dag_id="test",
                start_date=datetime(2025, 1, 1, tzinfo=UTC),
                schedule=None,
                tasks={"run": BashTask(task_id="run", bash_command="pwd")},
            )
        },
    )
    assert config.dags["test"].instantiate().get_task("run").cwd == "/shared"
    assert 'cwd="/shared"' in config.dags["test"].render()


def test_operator_defaults_validate_argument_values():
    with pytest.raises(ValueError):
        Configuration(
            default_operator_args=[{"operator": "airflow_pydantic.BashTask", "cwd": ["invalid"]}],
            dags={"test": Dag(dag_id="test", tasks={"run": BashTask(task_id="run", bash_command="pwd")})},
        )


def test_ssh_defaults_preserve_false_and_round_trip():
    defaults = Configuration(
        default_operator_args=[{"operator": "airflow_pydantic.SSHTask", "conn_timeout": 20, "get_pty": True}],
    )
    restored = Configuration.model_validate_json(defaults.model_dump_json(exclude_unset=True))
    config = Configuration(
        default_operator_args=restored.default_operator_args,
        dags={"test": Dag(dag_id="test", tasks={"run": SSHTask(task_id="run", command="hostname", ssh_conn_id="worker", get_pty=False)})},
    )
    tasks = config.dags["test"].tasks
    assert tasks is not None
    task = tasks["run"]
    assert isinstance(task, SSHTask)
    assert task.conn_timeout == 20
    assert task.get_pty is False
