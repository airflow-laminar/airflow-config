from unittest.mock import patch

import pytest

from airflow_config import load_config


def test_create_dag_from_config():
    try:
        from airflow_config import DAG
    except ImportError:
        pytest.skip("Airflow is not installed, skipping timetable tests")

    with patch("sys.exit") as sys_exit:
        conf = load_config("config", "disable")
        DAG(dag_id="testdag", config=conf)
        assert sys_exit.call_count == 1
        DAG(dag_id="example_dag", config=conf)
        assert sys_exit.call_count == 2


def test_create_dag_from_config_disable_perdag():
    try:
        from airflow_config import DAG
    except ImportError:
        pytest.skip("Airflow is not installed, skipping timetable tests")

    with patch("sys.exit") as sys_exit:
        conf = load_config("config", "disable_perdag")
        DAG(dag_id="testdag", config=conf)
        assert sys_exit.call_count == 1

        DAG(dag_id="example_dag", config=conf)
        assert sys_exit.call_count == 1

        DAG(dag_id="example_da2", config=conf)
        assert sys_exit.call_count == 2


def test_create_dag_from_config_disable_omegaconf():
    try:
        from airflow_config import DAG
    except ImportError:
        pytest.skip("Airflow is not installed, skipping timetable tests")

    with patch("sys.exit") as sys_exit:
        conf = load_config("config", "disable_env")

        DAG(dag_id="testdag", config=conf)
        assert sys_exit.call_count == 1

        DAG(dag_id="prod_dag", config=conf)
        assert sys_exit.call_count == 1

        DAG(dag_id="nonprod_dag", config=conf)
        assert sys_exit.call_count == 2
