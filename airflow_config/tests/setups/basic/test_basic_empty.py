import pytest

from airflow_config import load_config


def test_config_and_empty_file():
    conf = load_config("config", "basic")
    assert conf.default_args.owner == "test"
    assert str(conf.model_dump_json(exclude_unset=True, indent=2, serialize_as_any=True))


def test_config_and_empty_file_create_dag():
    try:
        from airflow_config import create_dag
    except ImportError:
        pytest.skip("Airflow is not installed, skipping DAG tests")

    d = create_dag("config", "basic")
    assert d.dag_id == "tests-setups-basic-test-basic-empty"
    assert d.dag_id in globals()
    assert d.default_args["owner"] == "test"


def test_config_and_empty_file_create_dag2():
    try:
        from airflow_config import create_dag
    except ImportError:
        pytest.skip("Airflow is not installed, skipping DAG tests")

    d = create_dag("config", "basic2")
    assert d.dag_id == "tests-setups-basic-test-basic-empty"
    assert d.dag_id in globals()
    assert d.default_args["owner"] == "test2"
