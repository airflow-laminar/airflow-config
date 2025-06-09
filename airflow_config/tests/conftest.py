import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from jinja2 import DictLoader, Environment

from airflow_config import Configuration, DagArgs, TaskArgs


def should_short_circuit(**kwargs):
    return False


@pytest.fixture(autouse=True)
def airflow_config():
    config_template = (Path(__file__).parent / "airflow.cfg.jinja").read_text()
    j2 = Environment(loader=DictLoader({"airflow.cfg": config_template}), trim_blocks=True)
    with TemporaryDirectory() as td:
        tmpl = j2.get_template("airflow.cfg").render(
            # Set to root path of airflow_config
            DAGS_ROOT=str(Path(__file__).parent.parent.resolve()),
        )
        (Path(td) / "airflow.cfg").write_text(tmpl)
        os.environ["AIRFLOW_HOME"] = str(Path(td))
        os.environ["AIRFLOW_CONFIG"] = str((Path(td) / "airflow.cfg"))
        import airflow.configuration

        airflow.configuration.AIRFLOW_HOME = os.environ["AIRFLOW_HOME"]
        airflow.configuration.AIRFLOW_CONFIG = os.environ["AIRFLOW_CONFIG"]
        airflow_config_parser = airflow.configuration.AirflowConfigParser()
        airflow.configuration.load_standard_airflow_configuration(airflow_config_parser)
        airflow_config_parser.validate()
        airflow.configuration.conf = airflow_config_parser
        yield


@pytest.fixture(scope="function", autouse=True)
def configuration() -> Configuration:
    config = Configuration(
        default_args=TaskArgs(),
        default_dag_args=DagArgs(),
        dags={},
    )
    return config
