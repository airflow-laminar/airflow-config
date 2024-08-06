from unittest.mock import patch

from airflow_config import create_dags


def test_create_dag_from_multiple():
    with patch("airflow_config.configuration.base._get_calling_dag") as m1:
        m1.return_value = __file__
        dags = create_dags("config", ["dev", "prod"])
        assert dags[0].default_args["owner"] == "dev"
        assert dags[0].email == ["myemail@myemail.com"]
        assert dags[1].default_args["owner"] == "prod"
        assert dags[1].email == ["myemail@myemail.com"]
