from configparser import ConfigParser
from inspect import currentframe
from os import environ, path


def _get_calling_dag() -> str:
    return currentframe().f_back.f_back.f_globals["__file__"]


def _get_dag_root() -> str:
    home = environ.get("AIRFLOW_HOME", "")
    file = path.join(home, "airflow.cfg")
    if home and path.exists(file):
        config = ConfigParser()
        config.read(file)
        return config["core"]["dags_folder"]
    return ""
