from configparser import ConfigParser
from inspect import currentframe
from os import environ, getcwd, path


def _get_calling_dag(offset: int = 2) -> str:
    cur_frame = currentframe()
    for _ in range(offset):
        if hasattr(cur_frame, "f_back") and cur_frame.f_back and hasattr(cur_frame.f_back, "f_globals"):
            cur_frame = cur_frame.f_back
        else:
            break
    if "__file__" not in cur_frame.f_globals:  # pragma: no cover
        # Assumed in ipython/interpreter
        return path.join(getcwd(), "ipython.py")  # pragma: no cover
    return cur_frame.f_globals["__file__"]


def _get_dag_root() -> str:
    home = environ.get("AIRFLOW_HOME", "")
    file = path.join(home, "airflow.cfg")
    if home and path.exists(file):
        config = ConfigParser()
        config.read(file)
        return config["core"]["dags_folder"]
    return ""
