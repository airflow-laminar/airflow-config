from airflow_config import create_dag, load_config


def test_config_and_owners_change_via_global():
    conf = load_config("config", overrides=["+default_args=owner"])
    assert conf.default_args.owner == "test"


def test_config_and_owners_change_via_global_create_dag():
    d = create_dag("config", overrides=["+default_args=owner"])
    assert d.dag_id == "tests-setups-basic-test-change-globals"
    assert d.dag_id in globals()
    assert d.default_args["owner"] == "test"
