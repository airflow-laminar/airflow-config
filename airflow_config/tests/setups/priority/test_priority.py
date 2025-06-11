from unittest.mock import patch

from airflow_config import load_config


def test_priority():
    with patch("airflow_config.configuration.base._get_calling_dag") as m1:
        m1.return_value = __file__
        conf = load_config("config", "test")
        assert conf.default_args.owner == "test"
        assert "priority" in conf.extensions
        assert str(conf.model_dump_json(indent=2, serialize_as_any=True))
