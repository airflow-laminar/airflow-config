from pathlib import Path
from unittest.mock import patch

from airflow_config.cli import main


def test_generate_cli_selects_airflow_version():
    config_path = Path("config/prod.yaml").resolve()

    with patch("airflow_config.cli.load_config") as load_config:
        main(
            [
                str(config_path),
                "--output-dir",
                "generated_dags",
                "--airflow-version",
                "3",
                "--override",
                "dags.example.schedule=None",
            ]
        )

    load_config.assert_called_once_with(
        "config",
        "prod.yaml",
        overrides=["dags.example.schedule=None"],
        basepath=str(config_path),
    )
    load_config.return_value.generate.assert_called_once_with(Path("generated_dags"), airflow_major_version=3)
