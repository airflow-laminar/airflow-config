import os
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Dict, Optional

from hydra import initialize_config_dir, compose
from hydra.utils import instantiate

from airflow_config.exceptions import ConfigNotFoundError
from airflow_config.utils import _get_calling_dag
from airflow_config.configuration.airflow import GlobalDagConfiguration, DagConfiguration
from airflow_config.configuration.python import PythonConfiguration


__all__ = (
    "Configuration",
    "load_config",
)


class Configuration(BaseModel):
    global_: GlobalDagConfiguration = Field(description="Global DAG configuration, to apply to all DAGs unless explicitly overridden")
    python: PythonConfiguration = Field(description="Global Python configuration")
    dags: Optional[Dict[str, DagConfiguration]] = Field(description="List of dags statically configured via Pydantic")
    # user_configuration: UserConfiguration

    @staticmethod
    def _find_parent_config_folder(config_dir: str = "config", config_name: str = ""):
        calling_dag = _get_calling_dag()
        folder = Path(calling_dag).parent.resolve()
        exists = (
            (folder / config_dir).exists()
            if not config_name
            else ((folder / config_dir / f"{config_name}.yml").exists() or (folder / config_dir / f"{config_name}.yaml").exists())
        )
        while not exists:
            folder = folder.parent
            if str(folder) == os.path.abspath(os.sep):
                raise ConfigNotFoundError(calling_dag)
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
    ) -> "Configuration":
        overrides = overrides or []

        with initialize_config_dir(config_dir=str(Path(__file__).resolve().parent / "hydra"), version_base=None):
            if config_dir:
                hydra_folder, config_dir, _ = Configuration._find_parent_config_folder(config_dir=config_dir, config_name=config_name)

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


load_config = Configuration.load
