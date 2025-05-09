from pathlib import Path
from unittest.mock import patch

from airflow_config.ui.functions import get_configs_from_yaml, get_yaml_files
from airflow_config.ui.standalone import build_app, main


class TestAirflowPlugin:
    def test_plugin(self):
        from airflow_config.ui.viewer import AirflowConfigViewerPlugin, AirflowConfigViewerPluginView

        AirflowConfigViewerPluginView()
        AirflowConfigViewerPlugin()


class TestPluginFunctions:
    def test_plugin_functions_get_yamls(self):
        root = Path(__file__).parent
        assert sorted(get_yaml_files(root)) == sorted(
            [
                root / "setups/extensions/priority/config/test.yaml",
                root / "setups/good/options/config/test.yaml",
                root / "setups/good/complex/config/config.yaml",
                root / "setups/good/dag-disable/config/test.yaml",
                root / "setups/good/basic/config/test.yaml",
                root / "setups/good/dag-factory/config/test.yaml",
                root / "setups/good/dag-specialize/config/test.yaml",
                root / "setups/good/dag-disable-perdag/config/test.yaml",
                root / "setups/good/envs/config/dev.yaml",
                root / "setups/good/envs/config/prod.yaml",
            ]
        )

    def test_plugin_functions_get_configs(self):
        root = Path(__file__).parent
        assert (
            get_configs_from_yaml(Path(root) / "setups/good/basic/config/test.yaml", [])
            == """{
  "default_task_args": {
    "owner": "test",
    "email": null,
    "email_on_failure": null,
    "email_on_retry": null,
    "retries": null,
    "retry_delay": null,
    "start_date": null,
    "end_date": null,
    "depends_on_past": null,
    "queue": null,
    "pool": null,
    "pool_slots": null,
    "do_xcom_push": null,
    "task_display_name": null
  },
  "default_dag_args": {
    "description": null,
    "schedule": null,
    "start_date": null,
    "end_date": null,
    "max_active_tasks": null,
    "max_active_runs": null,
    "default_view": null,
    "orientation": null,
    "catchup": null,
    "is_paused_upon_creation": null,
    "tags": null,
    "dag_display_name": null,
    "enabled": null
  },
  "dags": {},
  "tasks": {},
  "extensions": {},
  "env": "",
  "name": "",
  "root": null,
  "tags": {}
}"""
        )


class TestStandaloneUI:
    def test_standalone_ui(self):
        # Test the build_app function
        app = build_app()
        assert app is not None

    def test_launch(self):
        # Test the main function
        with patch("airflow_config.ui.standalone.run") as mock_run:
            main()
            mock_run.assert_called_once()

    def test_main(self):
        import airflow_config.ui.standalone.__main__  # noqa: F401
