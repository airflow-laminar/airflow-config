from datetime import datetime
from unittest.mock import patch

from airflow_config import DAG, load_config


def test_config_and_options():
    with patch("airflow_config.configuration.base._get_calling_dag") as m1:
        m1.return_value = __file__
        conf = load_config("config", "test")
        assert conf.default_args.owner == "test"
        assert conf.default_args.email == ["myemail@myemail.com"]
        assert conf.default_args.email_on_failure is False
        assert conf.default_args.email_on_retry is False
        assert conf.default_args.retries == 0
        assert conf.default_args.depends_on_past is False
        # assert conf.global_.schedule == timedelta(seconds=60)
        assert conf.all_dags.start_date == datetime(2024, 1, 1)
        assert conf.all_dags.catchup is False
        assert conf.all_dags.tags == ["utility", "test"]


def test_create_dag_from_config():
    with patch("airflow_config.configuration.base._get_calling_dag") as m1:
        m1.return_value = __file__
        conf = load_config("config", "test")
        d = DAG(dag_id="testdag", config=conf)
        assert d.default_args["owner"] == "test"
        assert d.email == ["myemail@myemail.com"]
        assert d.email_on_failure is False
        assert d.email_on_retry is False
        assert d.retries == 0
        assert d.depends_on_past is False
        # assert d.schedule == timedelta(seconds=60)
        assert d.start_date == datetime(2024, 1, 1)
        assert d.catchup is False
        assert d.tags == ["utility", "test"]
