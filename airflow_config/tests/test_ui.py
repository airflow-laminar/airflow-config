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
                root / "setups" / "priority" / "config" / "test.yaml",
                root / "setups" / "basic" / "config" / "basic.yaml",
                root / "setups" / "basic" / "config" / "basic2.yaml",
                root / "setups" / "basic" / "config" / "complex.yaml",
                root / "setups" / "basic" / "config" / "options.yaml",
                root / "setups" / "envs" / "config" / "dev.yaml",
                root / "setups" / "envs" / "config" / "prod.yaml",
                root / "setups" / "factory" / "config" / "balancer.yaml",
                root / "setups" / "factory" / "config" / "factory.yaml",
                root / "setups" / "factory" / "config" / "host.yaml",
                root / "setups" / "factory" / "config" / "multi.yaml",
                root / "setups" / "factory" / "config" / "self_reference.yaml",
                root / "setups" / "factory" / "config" / "type_override.yaml",
                root / "setups" / "specialize" / "config" / "disable.yaml",
                root / "setups" / "specialize" / "config" / "disable_perdag.yaml",
                root / "setups" / "specialize" / "config" / "specialize.yaml",
            ]
        )

    def test_plugin_functions_get_configs(self):
        root = Path(__file__).parent
        val = get_configs_from_yaml(Path(root) / "setups/basic/config/basic.yaml", [])
        print("\n\n")
        print(val)
        print("\n\n")
        assert val == '{\n  "default_task_args": {\n    "owner": "test"\n  },\n  "default_dag_args": {},\n  "dags": {}\n}'

    def test_plugin_functions_get_configs_backtick_bug(self):
        root = Path(__file__).parent
        val = get_configs_from_yaml(Path(root) / "setups/factory/config/factory.yaml", [])
        print("\n\n")
        print(val)
        print("\n\n")

        assert (
            val
            == '{\n  "default_task_args": {\n    "owner": "test",\n    "email": [\n      "myemail@myemail.com"\n    ],\n    "email_on_failure": false,\n    "email_on_retry": false,\n    "retries": 0,\n    "depends_on_past": false\n  },\n  "default_dag_args": {\n    "schedule": "PT1H",\n    "start_date": "2024-01-01T00:00:00",\n    "catchup": false,\n    "tags": [\n      "utility",\n      "test"\n    ]\n  },\n  "dags": {\n    "example_dag": {\n      "description": "this is an example dag",\n      "schedule": "0 3 * * *",\n      "dag_id": "example_dag",\n      "default_args": {\n        "owner": "custom_owner"\n      },\n      "tasks": {\n        "task_1": {\n          "do_xcom_push": true,\n          "ssh_hook": {\n            "remote_host": "test",\n            "username": "test",\n            "port": 22,\n            "cmd_timeout": 10,\n            "keepalive_interval": 30,\n            "banner_timeout": 30.0\n          },\n          "ssh_conn_id": "test",\n          "command": "test",\n          "cmd_timeout": 10,\n          "environment": {\n            "test": "test"\n          },\n          "get_pty": true,\n          "task_id": "task_1"\n        },\n        "task_2": {\n          "python_callable": "airflow_config.tests.conftest.should_short_circuit",\n          "task_id": "task_2",\n          "dependencies": [\n            "task_1"\n          ]\n        },\n        "task_3": {\n          "bash_command": "echo \'1\'",\n          "task_id": "task_3",\n          "dependencies": [\n            "task_2"\n          ]\n        },\n        "task_4": {\n          "bash_command": "echo `pwd`",\n          "task_id": "task_4",\n          "dependencies": [\n            "task_3"\n          ]\n        },\n        "task_5": {\n          "python_callable": "airflow_config.tests.setups.utils.print_hello.print_hello",\n          "op_args": [],\n          "op_kwargs": {},\n          "templates_dict": {},\n          "templates_exts": null,\n          "show_return_value_in_logs": true,\n          "task_id": "task_5",\n          "dependencies": [\n            "task_4"\n          ]\n        }\n      }\n    },\n    "example_dag2": {\n      "schedule": "0 4 * * *",\n      "dag_id": "example_dag2",\n      "default_args": {\n        "owner": "custom_owner2"\n      },\n      "tasks": {\n        "task_1": {\n          "bash_command": "echo \\"1\\"",\n          "task_id": "task_1",\n          "operator": "airflow.operators.bash.BashOperator"\n        },\n        "task_2": {\n          "bash_command": "echo 2",\n          "task_id": "task_2",\n          "operator": "airflow.operators.bash.BashOperator",\n          "dependencies": [\n            "task_1"\n          ]\n        },\n        "task_3": {\n          "bash_command": "echo 3",\n          "task_id": "task_3",\n          "operator": "airflow.operators.bash.BashOperator",\n          "dependencies": [\n            "task_1"\n          ]\n        }\n      }\n    },\n    "example_dag3": {\n      "schedule": "0 5 * * *",\n      "dag_id": "example_dag3"\n    }\n  }\n}'
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
