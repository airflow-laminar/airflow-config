from pathlib import Path

from airflow_config import DAG, create_dag, generate_dag_id


def test_generate_dag_id(airflow_config):
    assert generate_dag_id(dag_root=str(Path(__file__).parent.parent.resolve())) == "tests-test-dag"


def test_create_dag_base(configuration):
    d = create_dag(configuration)
    assert d.dag_id == "tests-test-dag"
    assert "tests-test-dag" in globals()


def test_dag_base(configuration):
    d = DAG(config=configuration, dag_id="test")
    assert d.dag_id == "test"
