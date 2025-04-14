from unittest.mock import patch

import pytest

from airflow_config import ConfigNotFoundError, load_config


def test_no_config_file():
    with patch("airflow_config.configuration.base._get_calling_dag") as m1:
        m1.return_value = __file__
        with pytest.raises(ConfigNotFoundError):
            load_config("config", "missing.yaml")
