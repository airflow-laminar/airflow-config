from unittest.mock import patch

from airflow_config import load_config


def test_config_and_options():
    with patch("airflow_balancer.config.balancer.Pool"):
        conf = load_config("config", "config")

        assert str(conf.model_dump_json(indent=2, serialize_as_any=True))
