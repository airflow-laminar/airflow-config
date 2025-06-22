import os
import sys
from inspect import currentframe
from logging import getLogger
from pathlib import Path
from typing import Dict, Optional

from airflow.operators.bash import BashOperator
from airflow.utils.session import NEW_SESSION, provide_session
from airflow_pydantic import Dag, DagArgs, Task, TaskArgs
from hydra import compose, initialize_config_dir
from hydra.utils import instantiate
from pydantic import AliasChoices, BaseModel, Field, model_validator

from airflow_config.exceptions import ConfigNotFoundError
from airflow_config.utils import _get_calling_dag

__all__ = (
    "Configuration",
    "load_config",
)

_log = getLogger(__name__)


class Configuration(BaseModel):
    default_task_args: TaskArgs = Field(
        default_factory=TaskArgs,
        description="Global default default_args (task arguments)",
        validation_alias=AliasChoices("default_args", "default_task_args"),
    )
    default_dag_args: DagArgs = Field(default_factory=DagArgs, description="Global default dag arguments")

    dags: Optional[Dict[str, Dag]] = Field(default_factory=dict, description="List of dags statically configured via Pydantic")
    tasks: Optional[Dict[str, Task]] = Field(default_factory=dict, description="List of tasks statically configured via Pydantic")

    # Extensions
    extensions: Optional[Dict[str, BaseModel]] = Field(default_factory=dict, description="Any user-defined extensions")

    # Generic options
    env: Optional[str] = Field(default="", description="Environment to use for this configuration")
    name: Optional[str] = Field(default="", description="Name of the configuration")
    root: Optional[Path] = Field(default=None, description="Root path")
    tags: Optional[Dict[str, str]] = Field(default_factory=dict, description="Generic Tags for config. NOTE: Not related to dag tags")

    @property
    def default_args(self):
        return self.default_task_args

    @model_validator(mode="after")
    def _validate(self):
        # TODO add more validation here
        if not self.default_dag_args.start_date:
            _log.warning("No start_date set in default_dag_args, please set a start_date in the default_dag_args or in the dag itself.")
        return self

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
        per_dag_default_args = None

        # look up per-dag options
        if dag_kwargs.get("dag_id", None) in self.dags:
            # first try to see if per-dag options have default_args for subtasks
            per_dag_kwargs = self.dags[dag_kwargs["dag_id"]]

            per_dag_default_args = per_dag_kwargs.default_args

            # if dag is disabled directly, quit right away
            if per_dag_kwargs.enabled is False or (per_dag_kwargs.enabled is None and self.default_dag_args.enabled is False):
                sys.exit(0)

            for attr, val in per_dag_kwargs.model_dump(exclude_unset=True, exclude={"default_args", "enabled", "tasks"}).items():
                if attr == "dag_id":
                    # set
                    per_dag_kwargs.dag_id = dag_kwargs["dag_id"]
                    continue
                if attr not in dag_kwargs:
                    dag_kwargs[attr] = val

        elif self.default_dag_args.enabled is False:
            # if dag has no per-dag-config, but default dag args is disabled, quit right away
            sys.exit(0)

        # start with empty default_args
        default_args = {}

        # First, override with global defaults specified in config
        for attr, val in self.default_args.model_dump(exclude_unset=True).items():
            default_args[attr] = val

        # Next, update with per-dag defaults specified in config
        if per_dag_default_args is not None:
            for attr, val in per_dag_default_args.model_dump(exclude_unset=True).items():
                default_args[attr] = val

        # Finally, override with args hardcoded in the DAG file
        if "default_args" in dag_kwargs:
            default_args.update(dag_kwargs.get("default_args", {}))

        # update the dag_kwargs with the final default_args
        dag_kwargs["default_args"] = default_args

        for attr, val in self.default_dag_args.model_dump(exclude_unset=True, exclude={"enabled"}).items():
            if attr not in dag_kwargs:
                dag_kwargs[attr] = val

        doc_md = dag_kwargs.get("doc_md", "")
        if dag_kwargs.get("dag_id", None) in self.dags and self.dags[dag_kwargs["dag_id"]].tasks:
            doc_md += f"\n# Code Equivalent\n```python\n{self.dags[dag_kwargs['dag_id']].render()}\n```"
            # doc_md += f"\n# DAG Config\n```json\n{self.dags[dag_kwargs['dag_id']].model_dump_json(indent=2, serialize_as_any=True)}\n```"
        # doc_md += f"\n# Global Config\n```json\n{self.model_dump_json(indent=2, serialize_as_any=True)}\n```"
        if doc_md:
            dag_kwargs["doc_md"] = doc_md

    def apply(self, dag, dag_kwargs):
        # update the options in the dag if necessary, instantiate tasks
        if dag.dag_id in self.dags:
            # Instantiate self against the dag
            self.dags[dag.dag_id].instantiate(dag=dag)

    @provide_session
    def generate_in_mem(self, dir: Path | str = None, session=NEW_SESSION, placeholder_dag_id: str = "airflow-config-generate-dags"):
        from ..dag import DAG

        cur_frame = currentframe().f_back

        _log.info("Generating Placeholder DAG for in-memory generation")
        placeholder_dag = DAG(dag_id=placeholder_dag_id, config=self, schedule=None)
        with placeholder_dag:
            BashOperator(task_id=f"{placeholder_dag_id}-placeholder-task", bash_command='echo "Placeholder task"')
        cur_frame.f_globals[placeholder_dag_id] = placeholder_dag

        dir = dir or Path.cwd()
        dir_path = Path(dir)

        for dag_id, dag in self.dags.items():
            if dag.tasks:
                _log.info(f"Generating DAG: {dag_id} in memory")
                # rendered = dag.render()
                dag_path = dir_path / f"{dag_id}.py"

                dag_instance = DAG(dag_id=dag_id, config=self)
                # dag_instance.doc_md = f"# Code\n```python\n{rendered}\n```"
                _log.info(f"Updating DAG fileloc from {dag_instance.fileloc} to {str(dag_path)}")
                dag_instance.fileloc = str(dag_path)
                cur_frame.f_globals[dag_id] = dag_instance

                # Swap out DagCode
                # First, grab DAG code
                # _log.info(f"Updating DagModel for {dag_id} in memory")
                # query = select(DagModel).where(DagModel.dag_id == dag_id)
                # query = with_row_locks(query, of=DagModel, session=session)
                # orm_dag: DagModel = session.scalars(query).unique().first()

                # if not orm_dag:
                #     _log.info(f"No existing DagModel found for {dag_id}, check logs!")
                #     continue
                # else:
                #     orm_dag.fileloc = str(dag_path)
                #     orm_dag.last_parsed_time = timezone.utcnow()
                #     session.merge(orm_dag)

                # _log.info(f"Updating DagCode for {dag_id} in memory")
                # dag_code = DagCode(full_filepath=str(dag_path), source_code=rendered)
                # _log.info(f"Querying DB for {dag_code.fileloc_hash}")
                # existing_orm_dag_code = session.scalars(select(DagCode).where(DagCode.fileloc_hash == dag_code.fileloc_hash)).first()
                # if existing_orm_dag_code:
                #     _log.info(f"Updating existing DagCode for {dag_id} in memory")
                #     existing_orm_dag_code.last_updated = timezone.utcnow()
                #     existing_orm_dag_code.source_code = rendered
                #     session.merge(existing_orm_dag_code)
                # else:
                #     _log.info(f"Adding new DagCode for {dag_id} in memory")
                #     session.add(dag_code)
                _log.info(f"Adding DAG {dag_id} complete")
        session.commit()

    def generate(self, dir: Path | str = None):
        dir = dir or Path.cwd()
        dir_path = Path(dir)
        dir_path.mkdir(parents=True, exist_ok=True)

        for dag_id, dag in self.dags.items():
            if dag.tasks:
                rendered = dag.render()
                dag_path = dir_path / f"{dag_id}.py"
                if dag_path.exists() and dag_path.read_text() == rendered:
                    continue
                dag_path.write_text(rendered)


load_config = Configuration.load
