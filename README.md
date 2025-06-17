# airflow-config

[Apache Airflow](https://airflow.apache.org) utilities for configuration of DAGs and DAG environments

[![Build Status](https://github.com/airflow-laminar/airflow-config/actions/workflows/build.yaml/badge.svg?branch=main&event=push)](https://github.com/airflow-laminar/airflow-config/actions/workflows/build.yaml)
[![codecov](https://codecov.io/gh/airflow-laminar/airflow-config/branch/main/graph/badge.svg)](https://codecov.io/gh/airflow-laminar/airflow-config)
[![License](https://img.shields.io/github/license/airflow-laminar/airflow-config)](https://github.com/airflow-laminar/airflow-config)
[![PyPI](https://img.shields.io/pypi/v/airflow-config.svg)](https://pypi.python.org/pypi/airflow-config)

## Overview

This library allows for `YAML`-driven configuration of Airflow, including DAGs, Operators, and declaratively defined DAGs (à la [dag-factory](https://github.com/astronomer/dag-factory)).
It is built with [Pydantic](https://pydantic.dev), [Hydra](https://hydra.cc), and [OmegaConf](https://omegaconf.readthedocs.io/).

Consider the following basic DAG:

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

with DAG(
    dag_id="test-dag",
    default_args={
        "depends_on_past": False,
        "email": ["my.email@myemail.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 0,
    },
    description="test that dag is working properly",
    schedule=timedelta(minutes=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["utility", "test"],
):
    BashOperator(
        task_id="test-task",
        bash_command="echo 'test'",
    )
```

We can already see many options that we might want to drive centrally via config, perhaps based on some notion of environment (e.g. `dev`, `prod`, etc).

- `"email": ["my.email@myemail.com"]`
- `"email_on_failure": False`
- `"email_on_retry": False`
- `"retries": 0`
- `schedule=timedelta(minutes=1)`
- `tags=["utility", "test"]`

If we want to change these in our DAG, we need to modify code. Now imagine we have hundreds of DAGs, this can quickly get out of hand, especially since Airflow DAGs are Python code, and we might easily inject a syntax error or a trailing comma or other common problem.

Now consider the alternative, config-driven approach:

`config/dev.yaml`

```yaml
# @package _global_
_target_: airflow_config.Configuration
default_args:
  _target_: airflow_config.TaskArgs
  owner: test
  email: [myemail@myemail.com]
  email_on_failure: false
  email_on_retry: false
  retries: 0
  depends_on_past: false
default_dag_args:
  _target_: airflow_config.DagArgs
  schedule: "01:00"
  start_date: "2024-01-01"
  catchup: false
  tags: ["utility", "test"]
```

```python
from airflow.operators.bash import BashOperator
from airflow_config import DAG, load_config

config = load_config(config_name="dev")

with DAG(
    dag_id="test-dag",
    description="test that dag is working properly",
    schedule=timedelta(minutes=1),
    config=config
):
    BashOperator(
        task_id="test-task",
        bash_command="echo 'test'",
    )
```

This has a number of benefits:

- Make changes without code changes, with static type validation
- Make changes across any number of DAGs without having to copy-paste
- Organize collections of DAGs into groups, e.g. via enviroment like `dev`, `prod`, etc

## Features

- Configure DAGs from a central config file or...
- from multiple env-specific config files (e.g. `dev`, `uat`, `prod`)
- Specialize DAGs by `dag_id` from a single file (e.g. set each DAG's `schedule` from a single shared file)
- Generate entire DAGs declaratively, like [astronomer/dag-factory](https://github.com/astronomer/dag-factory)
- Configure other extensions like:
  - [airflow-priority](https://github.com/airflow-laminar/airflow-priority)
  - [airflow-balancer](https://github.com/airflow-laminar/airflow-balancer)
  - [airflow-supervisor](https://github.com/airflow-laminar/airflow-supervisor)
  - or write your own pydantic-based model and get yaml-based configuration for free


## Configuration

```python
class Configuration(BaseModel):
    # default task args
    # https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/baseoperator/index.html#airflow.models.baseoperator.BaseOperator
    default_task_args: TaskArgs

    # default dag args
    # https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/dag/index.html#airflow.models.dag.DAG
    default_dag_args: DagArgs

    # string (dag id) to Dag mapping
    dags: Optional[Dict[str, Dag]]

    # string (dag id) to Task mapping
    tasks: Optional[Dict[str, Task]]

    # used for extensions to inject arbitrary configuration.
    # See e.g.: https://github.com/airflow-laminar/airflow-supervisor?tab=readme-ov-file#example-dag-airflow-config
    extensions: Optional[Dict[str, BaseModel]]
```

Here is an example configuration defined via yaml:

```yaml
# @package _global_
_target_: airflow_config.Configuration
default_task_args:
  _target_: airflow_config.TaskArgs
  owner: blerg
  email: []
  email_on_failure: false
  email_on_retry: false
  retries: 0
  depends_on_past: false

default_dag_args:
  _target_: airflow_config.DagArgs
  start_date: ["2025-01-01", "America/New_York"]
  catchup: false
  max_active_runs: 1

dags:
  reboot:
    tags: ["reboot", "utility"]
    description: "Reboot machines"
    schedule: "0 0 * * *"
    max_active_tasks: 1
  clean-logs:
    tags: ["celery", "utility"]
    description: "Clean worker logs"
    schedule: "0 4 * * *"
```


## Examples

- [Basic 1](https://airflow-laminar.github.io/airflow-config/docs/src/examples.html#load-defaults-from-config)
- [Basic 2](https://airflow-laminar.github.io/airflow-config/docs/src/examples.html#load-more-defaults-from-config)
- [Specialize DAGs](https://airflow-laminar.github.io/airflow-config/docs/src/examples.html#specialize-individual-dags)
- [Declarative DAGs (DAG Factory)](https://airflow-laminar.github.io/airflow-config/docs/src/examples.html#declarative-dags-dag-factory)
- [Test Suite Setups](https://github.com/airflow-laminar/airflow-config/tree/main/airflow_config/tests/setups)


## License

This software is licensed under the Apache 2.0 license. See the [LICENSE](LICENSE) file for details.
