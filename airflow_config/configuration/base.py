import os
from pathlib import Path
from typing import Dict, Optional

from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from pydantic import BaseModel, Field

from airflow_config.configuration.airflow import DagArgs, DagConfiguration, DefaultArgs
from airflow_config.configuration.python import PythonConfiguration
from airflow_config.exceptions import ConfigNotFoundError
from airflow_config.utils import _get_calling_dag

__all__ = (
    "Configuration",
    "load_config",
)


class Configuration(BaseModel):
    default_args: DefaultArgs = Field(
        default_factory=DefaultArgs, description="Task-level args to set for all DAGs, unless overridden in the DAG itself"
    )
    all_dags: DagArgs = Field(default_factory=DagArgs, description="Per-dag arguments to set global defaults")
    python: PythonConfiguration = Field(default_factory=PythonConfiguration, description="Global Python configuration")
    extensions: Optional[Dict[str, BaseModel]] = Field(default_factory=dict, description="Any user-defined extensions")
    dags: Optional[Dict[str, DagConfiguration]] = Field(default_factory=dict, description="List of dags statically configured via Pydantic")

    @staticmethod
    def _find_parent_config_folder(config_dir: str = "config", config_name: str = "", *, basepath: str = "", _offset: int = 2):
        if basepath:
            if basepath.endswith((".py", ".cfg", ".yml", ".yaml")):
                calling_dag = Path(basepath)
            else:
                calling_dag = Path(basepath) / "dummy.py"
        else:
            calling_dag = Path(_get_calling_dag(offset=_offset))
        folder = calling_dag.parent.resolve()
        exists = (
            (folder / config_dir).exists()
            if not config_name
            else ((folder / config_dir / f"{config_name}.yml").exists() or (folder / config_dir / f"{config_name}.yaml").exists())
        )
        while not exists:
            folder = folder.parent
            if str(folder) == os.path.abspath(os.sep):
                raise ConfigNotFoundError(config_dir=config_dir, dagfile=calling_dag)
            exists = (
                (folder / config_dir).exists()
                if not config_name
                else ((folder / config_dir / f"{config_name}.yml").exists() or (folder / config_dir / f"{config_name}.yaml").exists())
            )

        config_dir = (folder / config_dir).resolve()
        if not config_name:
            return folder.resolve(), config_dir, ""
        elif (folder / config_dir / f"{config_name}.yml").exists():
            return folder.resolve(), config_dir, (folder / config_dir / f"{config_name}.yml").resolve()
        return folder.resolve(), config_dir, (folder / config_dir / f"{config_name}.yaml").resolve()

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

                cfg = compose(config_name="base", overrides=[], return_hydra_config=True)
                searchpaths = cfg["hydra"]["searchpath"]
                searchpaths.extend([hydra_folder, config_dir])
                if config_name:
                    overrides = [f"+config={config_name}", *overrides.copy(), f"hydra.searchpath=[{','.join(searchpaths)}]"]
                else:
                    overrides = [*overrides.copy(), f"hydra.searchpath=[{','.join(searchpaths)}]"]

            cfg = compose(config_name="base", overrides=overrides)
            config = instantiate(cfg)

            if not isinstance(config, Configuration):
                config = Configuration(**config)
            return config

    def pre_apply(self, dag, dag_kwargs):
        # update options in config based on hard-coded overrides
        # in the DAG file itself
        if "default_args" not in dag_kwargs:
            dag_kwargs["default_args"] = {}
        if "owner" not in dag_kwargs["default_args"] and self.default_args.owner:
            dag_kwargs["default_args"]["owner"] = self.default_args.owner

    def apply(self, dag, dag_kwargs):
        # update the options in the dag
        # TODO loop
        dag.start_date = self.all_dags.start_date
        dag.end_date = self.all_dags.end_date
        dag.catchup = self.all_dags.catchup
        dag.tags = self.all_dags.tags

        dag.email = self.default_args.email
        dag.email_on_failure = self.default_args.email_on_failure
        dag.email_on_retry = self.default_args.email_on_retry
        dag.retries = self.default_args.retries
        dag.retry_delay = self.default_args.retry_delay
        dag.depends_on_past = self.default_args.depends_on_past


load_config = Configuration.load
