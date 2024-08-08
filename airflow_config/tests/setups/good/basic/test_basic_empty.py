from airflow_config import create_dag, load_config


def test_config_and_empty_file():
    conf = load_config("config", "test")
    assert conf.default_args.owner == "test"


def test_config_and_empty_file_create_dag():
    d = create_dag("config", "test")
    assert d.dag_id == "tests-setups-good-basic-test-basic-empty"
    assert d.dag_id in globals()
    assert d.default_args["owner"] == "test"
