from airflow_config import create_dag, load_config


def test_config_and_empty_file():
    conf = load_config("config", "basic")
    assert conf.default_args.owner == "test"
    assert str(conf.model_dump_json(exclude_unset=True, indent=2, serialize_as_any=True))


def test_config_and_empty_file_create_dag():
    d = create_dag("config", "basic")
    assert d.dag_id == "tests-setups-basic-test-basic-empty"
    assert d.dag_id in globals()
    assert d.default_args["owner"] == "test"


def test_config_and_empty_file_create_dag2():
    d = create_dag("config", "basic2")
    assert d.dag_id == "tests-setups-basic-test-basic-empty"
    assert d.dag_id in globals()
    assert d.default_args["owner"] == "test2"
