from airflow_config import Configuration, create_dags


def test_create_dag_from_multiple():
    dags = create_dags("config", ["dev", "prod"])
    assert dags[0].dag_id == "tests-setups-envs-test-envs-dev"
    assert dags[1].dag_id == "tests-setups-envs-test-envs-prod"
    assert dags[0].dag_id in globals()
    assert dags[1].dag_id in globals()
    assert dags[0].default_args["owner"] == "dev"
    assert dags[0].default_args["email"] == ["myemail@myemail.com"]
    assert dags[1].default_args["owner"] == "prod"
    assert dags[1].default_args["email"] == ["myemail@myemail.com"]


def test_create_dag_from_multiple_configs():
    confs_dev = Configuration.load("config", "dev")
    confs_prod = Configuration.load("config", "prod")
    dags = create_dags([confs_dev, confs_prod], ["test-dev", "test-prod"])
    assert dags[0].dag_id == "test-dev"
    assert dags[1].dag_id == "test-prod"
    assert dags[0].dag_id in globals()
    assert dags[1].dag_id in globals()
    assert dags[0].default_args["owner"] == "dev"
    assert dags[0].default_args["email"] == ["myemail@myemail.com"]
    assert dags[1].default_args["owner"] == "prod"
    assert dags[1].default_args["email"] == ["myemail@myemail.com"]
