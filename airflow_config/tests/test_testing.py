import pytest
from airflow_pydantic import BashTask, Dag, SSHTask
from airflow_pydantic.airflow import BashOperator

from airflow_config import Configuration
from airflow_config.testing import assert_dag_ids, assert_task_ids, assert_task_type


@pytest.fixture
def config():
    return Configuration(
        dags={
            "report": Dag(dag_id="report", tasks={"run": BashTask(bash_command="echo ok")}),
            "empty": Dag(dag_id="empty", tasks=None, enabled=False),
        }
    )


def test_expected_ids_and_task_types(config):
    assert_dag_ids(config, ["report", "empty"])
    assert_task_ids(config.dags["report"], ["run"])
    assert_task_ids(config.dags["empty"], [])
    assert_task_type(config.dags["report"], "run", BashTask)
    assert_task_type(config.dags["report"], "run", BashOperator)


def test_dag_ids_report_missing_and_unexpected(config):
    with pytest.raises(AssertionError, match=r"missing=\['absent'\].*unexpected=\['empty'\]"):
        assert_dag_ids(config, ["report", "absent"])


def test_task_ids_report_missing_and_unexpected(config):
    with pytest.raises(AssertionError, match=r"report.*missing=\['absent'\].*unexpected=\['run'\]"):
        assert_task_ids(config.dags["report"], ["absent"])


def test_task_type_reports_actual_and_expected_types(config):
    with pytest.raises(AssertionError, match=r"report.*run.*BashTask.*SSHTask"):
        assert_task_type(config.dags["report"], "run", SSHTask)


def test_missing_task_reports_available_ids(config):
    with pytest.raises(AssertionError, match=r"absent.*report.*available=\['run'\]"):
        assert_task_type(config.dags["report"], "absent", BashTask)
