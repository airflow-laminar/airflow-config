# airflow-config

[Apache Airflow](https://airflow.apache.org) utilities for for configuration of many DAGs and DAG environments

[![Build Status](https://github.com/airflow-laminar/airflow-config/actions/workflows/build.yml/badge.svg?branch=main&event=push)](https://github.com/airflow-laminar/airflow-config/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/airflow-laminar/airflow-config/branch/main/graph/badge.svg)](https://codecov.io/gh/airflow-laminar/airflow-config)
[![License](https://img.shields.io/github/license/airflow-laminar/airflow-config)](https://github.com/airflow-laminar/airflow-config)
[![PyPI](https://img.shields.io/pypi/v/airflow-config.svg)](https://pypi.python.org/pypi/airflow-config)

## Overview

This library allows for `YAML`-driven configuration of Airflow, including DAGs, Operators, and declaratively defined DAGs (à la [dag-factory](https://github.com/astronomer/dag-factory)). It is built with [Pydantic](https://pydantic.dev), [Hydra](https://hydra.cc), and [OmegaConf](https://omegaconf.readthedocs.io/).

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
  _target_: airflow_config.DefaultArgs
  owner: test
  email: [myemail@myemail.com]
  email_on_failure: false
  email_on_retry: false
  retries: 0
  depends_on_past: false
all_dags:
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

## Configuration

More documentation coming soon!

## Integrations

Configuration can be arbitrarily extended by the key `extensions`. Support is built in for [`airflow-priority`](https://github.com/airflow-laminar/airflow-priority), but can be extended to any aribitrary pydantic model as seen in the [README of `airflow-supervisor`](https://github.com/airflow-laminar/airflow-supervisor).

## License

This software is licensed under the Apache 2.0 license. See the [LICENSE](LICENSE) file for details.
