import os
import sys
from pathlib import Path
from typing import Dict, Optional

from airflow_pydantic import Dag, DagArgs, Task, TaskArgs
from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from pydantic import BaseModel, Field

from airflow_config.exceptions import ConfigNotFoundError
from airflow_config.utils import _get_calling_dag

try:
    from airflow_priority import PriorityConfiguration

    have_priority = True
except ImportError:
    have_priority = False

try:
    from airflow_balancer import BalancerConfiguration

    have_balancer = True
except ImportError:
    have_balancer = False

__all__ = (
    "Configuration",
    "load_config",
)


class Configuration(BaseModel):
    default_task_args: TaskArgs = Field(default_factory=TaskArgs, description="Global default default_args (task arguments)", alias="default_args")
    default_dag_args: DagArgs = Field(default_factory=DagArgs, description="Global default dag arguments")

    dags: Optional[Dict[str, Dag]] = Field(default_factory=dict, description="List of dags statically configured via Pydantic")
    tasks: Optional[Dict[str, Task]] = Field(default_factory=dict, description="List of dags statically configured via Pydantic")

    # Extensions
    if have_priority:
        priority: Optional[PriorityConfiguration] = Field(default=None, description="Priority configuration for tasks")
    else:
        priority: Optional[object] = None
    if have_balancer:
        balancer: Optional[BalancerConfiguration] = Field(default=None, description="Balancer configuration for tasks")
    else:
        balancer: Optional[object] = None
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
    def _find_parent_config_folder(config_dir: str = "config", config_name: str = "", *, basepath: str = "", _offset: int = 2):
        if config_name.endswith(".yml"):
            raise Exception("Config file must be .yaml, not .yml")
        if config_name and not config_name.endswith(".yaml"):
            config_name = f"{config_name}.yaml"
        if basepath:
            if basepath.endswith((".py", ".cfg", ".yaml")):
                calling_dag = Path(basepath)
            else:
                calling_dag = Path(basepath) / "dummy.py"
        else:
            calling_dag = Path(_get_calling_dag(offset=_offset))
        folder = calling_dag.parent.resolve()
        exists = (folder / config_dir).exists() if not config_name else (folder / config_dir / f"{config_name}").exists()
        while not exists:
            folder = folder.parent
            if str(folder) == os.path.abspath(os.sep):
                raise ConfigNotFoundError(config_dir=config_dir, dagfile=calling_dag)
            exists = (folder / config_dir).exists() if not config_name else (folder / config_dir / f"{config_name}").exists()
            if not exists and (folder / config_dir / f"{config_name}.yml").exists():
                raise Exception(f"Config file {config_name}.yml exists in {config_dir} but must be .yaml!")

        config_dir = (folder / config_dir).resolve()
        if not config_name:
            return folder.resolve(), config_dir, ""
        elif (folder / config_dir / f"{config_name}.yml").exists():
            raise Exception(f"Config file {config_name}.yml exists in {config_dir} but must be .yaml!")
        return folder.resolve(), config_dir, (folder / config_dir / f"{config_name}").resolve()

    @staticmethod
    def load(
        config_dir: str = "config",
        config_name: str = "",
        overrides: Optional[list[str]] = None,
        *,
        basepath: str = "",
        _offset: int = 3,
    ) -> "Configuration":
        overrides = overrides or []

        with initialize_config_dir(config_dir=str(Path(__file__).resolve().parent / "hydra"), version_base=None):
            if config_dir:
                hydra_folder, config_dir, _ = Configuration._find_parent_config_folder(
                    config_dir=config_dir, config_name=config_name, basepath=basepath, _offset=_offset
                )

                cfg = compose(config_name="conf", overrides=[], return_hydra_config=True)
                searchpaths = cfg["hydra"]["searchpath"]
                searchpaths.extend([hydra_folder, config_dir])
                if config_name:
                    overrides = [f"+config={config_name}", *overrides.copy(), f"hydra.searchpath=[{','.join(searchpaths)}]"]
                else:
                    overrides = [*overrides.copy(), f"hydra.searchpath=[{','.join(searchpaths)}]"]

            cfg = compose(config_name="conf", overrides=overrides)
            config = instantiate(cfg)

            if not isinstance(config, Configuration):
                config = Configuration(**config)

            # Populate dag ids and task ids as a convenience
            for dag_id, dag in config.dags.items():
                if not dag.dag_id:
                    dag.dag_id = dag_id
                for task_id, task in dag.tasks.items():
                    if not task.task_id:
                        task.task_id = task_id
            return config

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

    def generate(self, dir):
        dir_path = Path(dir)
        dir_path.mkdir(parents=True, exist_ok=True)
        for dag_id, dag in self.dags.items():
            if dag.tasks:
                dag_path = dir_path / f"{dag_id}.py"
                rendered = dag.render()
                if dag_path.exists() and dag_path.read_text() == rendered:
                    continue
                dag_path.write_text(rendered)


load_config = Configuration.load
