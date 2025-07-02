import pytest

from airflow_config import load_config


def test_config_and_owners_change_via_global():
    conf = load_config("config", overrides=["+default_args=owner"])
    assert conf.default_args.owner == "test"


def test_config_and_owners_change_via_global_create_dag():
    try:
        from airflow_config import create_dag
    except ImportError:
        pytest.skip("Airflow is not installed, skipping DAG tests")

    d = create_dag("config", overrides=["+default_args=owner"])
    assert d.dag_id == "tests-setups-basic-test-change-globals"
    assert d.dag_id in globals()
    assert d.default_args["owner"] == "test"
