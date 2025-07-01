from pathlib import Path

import pytest


def test_generate_dag_id(airflow_config):
    try:
        from airflow_config import generate_dag_id
    except ImportError:
        pytest.skip("Airflow is not installed, skipping DAG tests")
    assert generate_dag_id(dag_root=str(Path(__file__).parent.parent.resolve())) == "tests-test-dag"


def test_create_dag_base(configuration):
    try:
        from airflow_config import create_dag
    except ImportError:
        pytest.skip("Airflow is not installed, skipping DAG tests")

    d = create_dag(configuration)
    assert d.dag_id == "tests-test-dag"
    assert "tests-test-dag" in globals()


def test_dag_base(configuration):
    try:
        from airflow_config import DAG
    except ImportError:
        pytest.skip("Airflow is not installed, skipping DAG tests")

    d = DAG(config=configuration, dag_id="test")
    assert d.dag_id == "test"
