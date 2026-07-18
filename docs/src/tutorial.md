# Tutorial: generate a DAG from YAML

In this tutorial, we will describe a two-task workflow in YAML, load its
Pydantic models, and register the resulting DAG with Airflow.

## Install the packages

For Airflow 3, run:

```bash
pip install 'airflow-config[airflow3]'
```

## Create the configuration

Create `config/etl.yaml` beside your DAG file:

```yaml
# @package _global_
_target_: airflow_config.Configuration

default_task_args:
  _target_: airflow_config.TaskArgs
  owner: data-platform
  retries: 2

default_dag_args:
  _target_: airflow_config.DagArgs
  start_date: "2025-01-01"
  catchup: false
  tags: [tutorial]

dags:
  daily-etl:
    schedule: "0 2 * * *"
    tasks:
      extract:
        _target_: airflow_config.BashTask
        bash_command: python /opt/etl/extract.py
      load:
        _target_: airflow_config.BashTask
        bash_command: python /opt/etl/load.py
        dependencies: [extract]
```

## Load the configuration

Create `daily_etl.py` beside the `config` directory:

```python
from airflow_config import load_config

config = load_config("config", "etl")

dag = config.dags["daily-etl"]
print(dag.schedule)
print(dag.default_args.owner)
print(dag.tasks["load"].dependencies)
```

Run the file with Python. The output should be:

```text
0 2 * * *
data-platform
['extract']
```

The loader found the configuration relative to the calling file, composed it
with Hydra, instantiated each `_target_`, and applied shared defaults.

## Register the DAG

Add this line to `daily_etl.py`:

```python
config.generate_in_mem()
```

Place the Python file and `config` directory in an Airflow DAG folder. Then
inspect the result:

```bash
airflow dags list | grep daily-etl
airflow tasks list daily-etl
```

The DAG contains `extract` and `load`, with `load` downstream of `extract`.

You have now generated an Airflow DAG from validated, composable YAML.
