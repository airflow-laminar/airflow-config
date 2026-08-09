import sys
from pathlib import Path
from unittest.mock import call, patch

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


def test_generate_cli_imports_modules_before_loading():
    config_path = Path("config/prod.yaml").resolve()

    with (
        patch("airflow_config.cli.import_module") as import_module,
        patch("airflow_config.cli.load_config") as load_config,
    ):
        import_module.side_effect = lambda module: load_config.assert_not_called()
        main(
            [
                str(config_path),
                "--output-dir",
                "generated_dags",
                "--airflow-version",
                "3",
                "--import",
                "my_resolvers",
                "--import",
                "my_other_resolvers",
            ]
        )

    assert import_module.call_args_list == [call("my_resolvers"), call("my_other_resolvers")]


def test_generate_cli_adds_current_directory_to_python_path(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "path", sys.path.copy())

    with (
        patch("airflow_config.cli.import_module"),
        patch("airflow_config.cli.load_config"),
    ):
        main(
            [
                "config/prod.yaml",
                "--output-dir",
                "generated_dags",
                "--airflow-version",
                "3",
                "--import",
                "my_resolvers",
            ]
        )

    assert sys.path[-1] == str(tmp_path)
