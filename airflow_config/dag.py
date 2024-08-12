from functools import singledispatch
from inspect import currentframe
from typing import Any, Optional, cast
from uuid import uuid4

from airflow.models.dag import DAG as BaseDag

from .configuration.base import Configuration
from .utils import _get_calling_dag, _get_dag_root

__all__ = (
    "generate_dag_id",
    "create_dag",
    "create_dags",
    "DAG",
)


class DAG(BaseDag):
    def __init__(self, config: Configuration = None, **kwargs):
        if config:
            config.pre_apply(self, kwargs)
        super().__init__(**kwargs)
        if config:
            config.apply(self, kwargs)


def generate_dag_id(name: str = "", dag_root: str = "", offset: int = 2) -> str:
    if not name:
        try:
            # get file of calling python file, can't use the module name as one might
            # have the same module in multiple folders
            caller = _get_calling_dag(offset=offset)
            # remove python suffix, replace path with dash
            name = caller.replace(".py", "").replace("/", "-").replace("_", "-")
            # remove root folder
            dag_root = dag_root or _get_dag_root()
            name = name.replace(dag_root.replace("/", "-").replace("_", "-"), "")
            while name.startswith("-"):
                name = name[1:]
        except Exception:
            name = cast(str, uuid4())
    return name


@singledispatch
def create_dag(arg, **kwargs: Any) -> DAG:
    raise NotImplementedError()


@singledispatch
def create_dags(arg, **kwargs: Any) -> DAG:
    raise NotImplementedError()


@create_dag.register
def _create_dag_config(config: Configuration, dag_id: str = "", _offset: int = 3) -> DAG:
    dag_id = dag_id or generate_dag_id(offset=_offset + 1)
    dag = DAG(config=config, dag_id=dag_id)
    cur_frame = currentframe()
    for _ in range(_offset - 1):
        if hasattr(cur_frame, "f_back") and cur_frame.f_back and hasattr(cur_frame.f_back, "f_globals"):
            cur_frame = cur_frame.f_back
        else:
            break
    cur_frame.f_globals[dag_id] = dag
    return dag


@create_dag.register
def _create_dag_dir(config_dir: str = "config", config_name: str = "", overrides: Optional[list[str]] = None, dag_id: str = "", **kwargs: Any) -> DAG:
    dag_id = dag_id or generate_dag_id(offset=4)
    config = Configuration.load(config_dir=config_dir, config_name=config_name, overrides=overrides, _offset=5)
    return create_dag(config, dag_id=dag_id, _offset=5, **kwargs)


@create_dags.register
def _create_dags_config(configs: list, dag_ids: list[str] = None, **kwargs: Any) -> list[DAG]:
    ret = []
    dag_ids = dag_ids or []
    for i, config in enumerate(configs):
        if i < len(dag_ids):
            dag_id = dag_ids[i]
        else:
            dag_id = ""
        ret.append(create_dag(config, dag_id=dag_id, _offset=5, **kwargs))
    return ret


@create_dags.register
def _create_dags_dirs(
    config_dir: str = "config",
    config_names: list[list[str]] = None,
    overrides: Optional[list[str]] = None,
    dag_id_base: str = "",
    **kwargs: Any,
) -> list[DAG]:
    ret = []
    dag_id_base = dag_id_base or generate_dag_id(offset=4)
    for config_name in config_names:
        config = Configuration.load(config_dir=config_dir, config_name=config_name, overrides=overrides, _offset=5)
        ret.append(create_dag(config, dag_id=f"{dag_id_base}-{config_name}", _offset=5, **kwargs))
    return ret
