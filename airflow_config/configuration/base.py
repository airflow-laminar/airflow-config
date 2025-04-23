import sys
from pathlib import Path
from typing import Dict, Optional

from airflow_pydantic import Dag, DagArgs, Task, TaskArgs
from ccflow import BaseModel, load_config as base_load_config
from pydantic import Field

from airflow_config.exceptions import ConfigNotFoundError
from airflow_config.utils import _get_calling_dag

__all__ = (
    "Configuration",
    "load_config",
)


class Configuration(BaseModel):
    default_task_args: TaskArgs = Field(default_factory=TaskArgs, description="Global default default_args (task arguments)")
    default_dag_args: DagArgs = Field(default_factory=DagArgs, description="Global default dag arguments")

    dags: Optional[Dict[str, Dag]] = Field(default_factory=dict, description="List of dags statically configured via Pydantic")
    tasks: Optional[Dict[str, Task]] = Field(default_factory=dict, description="List of dags statically configured via Pydantic")

    extensions: Optional[Dict[str, BaseModel]] = Field(default_factory=dict, description="Any user-defined extensions")

    # Generic options
    env: Optional[str] = Field(default="", description="Environment to use for this configuration")
    name: Optional[str] = Field(default="", description="Name of the configuration")
    root: Optional[Path] = Field(default=None, description="Root path")
    tags: Optional[Dict[str, str]] = Field(default_factory=dict, description="Generic Tags for config. NOTE: Not related to dag tags")

    @property
    def default_args(self):
        return self.default_task_args

    @staticmethod
    def load(
        config_dir: str = "",
        config_name: str = "",
        overrides: Optional[list[str]] = None,
        *,
        basepath: str = "",
        _offset: int = 2,
    ) -> "Configuration":
        if basepath:
            if basepath.endswith((".py", ".cfg", ".yaml")):
                calling_dag = Path(basepath)
            else:
                calling_dag = Path(basepath) / "dummy.py"
        else:
            calling_dag = Path(_get_calling_dag(offset=_offset))
        folder = calling_dag.parent.resolve()

        try:
            cfg = base_load_config(
                root_config_dir=str(Path(__file__).resolve().parent / "hydra"),
                root_config_name="conf",
                config_dir=config_dir,
                config_name=config_name,
                overrides=overrides,
                overwrite=True,
                basepath=folder,
            )
        except FileNotFoundError as e:
            raise ConfigNotFoundError(folder, calling_dag) from e
        # TODO: omit _target?
        # return Configuration(**(cfg.model_dump()["models"]))
        return Configuration(**cfg.models)

    def pre_apply(self, dag, dag_kwargs):
        # update options in config based on hard-coded overrides
        # in the DAG file itself
        per_dag_default_args = {}

        # look up per-dag options
        if dag_kwargs.get("dag_id", None) in self.dags:
            # first try to see if per-dag options have default_args for subtasks
            per_dag_kwargs = self.dags[dag_kwargs["dag_id"]]

            per_dag_default_args = per_dag_kwargs.default_args

            # if dag is disabled directly, quit right away
            if per_dag_kwargs.enabled is False or (per_dag_kwargs.enabled is None and self.default_dag_args.enabled is False):
                sys.exit(0)

            for attr in DagArgs.model_fields:
                if attr in ("default_args", "enabled"):
                    # skip
                    continue
                if attr == "dag_id":
                    # set
                    per_dag_kwargs.dag_id = dag_kwargs["dag_id"]
                    continue

                val = getattr(per_dag_kwargs, attr, None)

                if attr not in dag_kwargs and val:
                    dag_kwargs[attr] = val
        elif self.default_dag_args.enabled is False:
            # if dag has no per-dag-config, but default dag args is disabled, quit right away
            sys.exit(0)

        # start with empty default_args
        default_args = {}

        # First, override with global defaults specified in config
        for attr in TaskArgs.model_fields:
            if getattr(self.default_args, attr, None) is not None:
                default_args[attr] = getattr(self.default_args, attr)

        # Next, update with per-dag defaults specified in config
        for attr in TaskArgs.model_fields:
            if getattr(per_dag_default_args, attr, None) is not None:
                default_args[attr] = getattr(per_dag_default_args, attr)

        # Finally, override with args hardcoded in the DAG file
        if "default_args" in dag_kwargs:
            default_args.update(dag_kwargs.get("default_args", {}))

        # update the dag_kwargs with the final default_args
        dag_kwargs["default_args"] = default_args

        for attr in DagArgs.model_fields:
            if attr not in dag_kwargs and attr not in ("enabled",):
                val = getattr(self.default_dag_args, attr, None)
                if attr not in dag_kwargs and val is not None:
                    dag_kwargs[attr] = val

    def apply(self, dag, dag_kwargs):
        # update the options in the dag if necessary,
        # instantiate tasks
        if dag.dag_id in self.dags:
            tasks = self.dags[dag.dag_id].tasks
            task_insts = {}
            if tasks:
                for task_id, task_inst in tasks.items():
                    task_inst.task_id = task_id
                    task_insts[task_id] = task_inst.instantiate(dag=dag)
            for task_id, task_inst in task_insts.items():
                task_deps = tasks[task_id].dependencies
                if task_deps:
                    for dep in task_deps:
                        task_insts[dep] >> task_inst


load_config = Configuration.load
