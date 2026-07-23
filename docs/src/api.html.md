# API reference

This reference is generated from public signatures and docstrings.

## Configuration

### *pydantic model* airflow_config.configuration.base.Configuration

Bases: `BaseModel`

#### *field* default_task_args *: TaskArgs | None* *[Optional]*

Global default default_args (task arguments)

#### *field* default_dag_args *: DagArgs* *[Optional]*

Global default dag arguments

#### *field* dags *: dict[str, Annotated[Dag, SerializeAsAny()]] | None* *[Optional]*

List of dags statically configured via Pydantic

#### *field* templates *: \_Templates | None* *[Optional]*

Templates for DAGs and Tasks

#### *field* extensions *: dict[str, BaseModel] | None* *[Optional]*

Any user-defined extensions

#### *field* env *: str | None* *= ''*

Environment to use for this configuration

#### *field* name *: str | None* *= ''*

Name of the configuration

#### *field* root *: Path | None* *= None*

Root path

#### *field* tags *: dict[str, str] | None* *[Optional]*

Generic Tags for config. NOTE: Not related to dag tags

#### *property* default_args

#### *static* load(config_dir: str = 'config', config_name: str = '', overrides: list[str] | None = None, , basepath: str = '', \_offset: int = 3) → [Configuration](#airflow_config.configuration.base.Configuration)

#### pre_apply(dag, dag_kwargs)

#### apply(dag, dag_kwargs)

#### generate_in_mem(dir: Path | str | None = None, placeholder_dag_id: str = 'airflow-config-generate-dags')

#### generate(dir: Path | str | None = None)

### airflow_config.configuration.base.load_config(config_dir: str = 'config', config_name: str = '', overrides: list[str] | None = None, , basepath: str = '', \_offset: int = 3) → [Configuration](#airflow_config.configuration.base.Configuration)

## DAG creation

### *class* airflow_config.dag.DAG(config: [Configuration](#airflow_config.configuration.base.Configuration) = None, \*\*kwargs)

Bases: `DAG`

### airflow_config.dag.create_dag(arg, \*\*kwargs: Any) → [DAG](#airflow_config.dag.DAG)

### airflow_config.dag.create_dag(config: [Configuration](#airflow_config.configuration.base.Configuration), dag_id: str = '', \_offset: int = 3) → [DAG](#airflow_config.dag.DAG)

### airflow_config.dag.create_dag(config_dir: str = 'config', config_name: str = '', overrides: list[str] | None = None, dag_id: str = '', \*\*kwargs: Any) → [DAG](#airflow_config.dag.DAG)

### airflow_config.dag.create_dags(arg, \*\*kwargs: Any) → [DAG](#airflow_config.dag.DAG)

### airflow_config.dag.create_dags(configs: list, dag_ids: list[str] | None = None, \*\*kwargs: Any) → list[[DAG](#airflow_config.dag.DAG)]

### airflow_config.dag.create_dags(config_dir: str = 'config', config_names: list[list[str]] | None = None, overrides: list[str] | None = None, dag_id_base: str = '', \*\*kwargs: Any) → list[[DAG](#airflow_config.dag.DAG)]

### airflow_config.dag.generate_dag_id(name: str = '', dag_root: str = '', offset: int = 2) → str

## Utilities

### airflow_config.utils.generate_dag_id(name: str = '', dag_root: str = '', offset: int = 2) → str

## Exceptions

### *exception* airflow_config.exceptions.ConfigFileExtensionError

Bases: `ValueError`

Raised when a configuration file uses an unsupported extension.

### *exception* airflow_config.exceptions.ConfigNotFoundError(config_dir, dagfile)

Bases: `RuntimeError`

## Viewer functions

### airflow_config.ui.functions.get_configs_from_yaml(yaml: str, overrides: list[str]) → list[str]

### airflow_config.ui.functions.get_yaml_files(dags_folder: str) → list[Path]
