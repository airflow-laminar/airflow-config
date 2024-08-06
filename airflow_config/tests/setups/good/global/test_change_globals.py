from unittest.mock import patch

from airflow_config import load_config


def test_config_and_owners_change_via_global():
    with patch("airflow_config.configuration.base._get_calling_dag") as m1:
        m1.return_value = __file__
        conf = load_config("config", overrides=["+global=owner"])
        assert conf.default_args.owner == "test"
