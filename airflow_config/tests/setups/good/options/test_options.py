from airflow_config import load_config
from unittest.mock import patch


def test_config_and_options():
    with patch("airflow_config.configuration.base._get_calling_dag") as m1:
        m1.return_value = __file__
        conf = load_config("config", "test")
        assert conf.global_.owner == "test"