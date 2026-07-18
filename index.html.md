# airflow-config

Declarative Apache Airflow DAGs from Hydra YAML and `airflow-pydantic` models.

[![Build Status](https://github.com/airflow-laminar/airflow-config/actions/workflows/build.yaml/badge.svg?branch=main&event=push)](https://github.com/airflow-laminar/airflow-config/actions/workflows/build.yaml)
[![codecov](https://codecov.io/gh/airflow-laminar/airflow-config/branch/main/graph/badge.svg)](https://codecov.io/gh/airflow-laminar/airflow-config)
[![License](https://img.shields.io/github/license/airflow-laminar/airflow-config)](https://github.com/airflow-laminar/airflow-config)
[![PyPI](https://img.shields.io/pypi/v/airflow-config.svg)](https://pypi.python.org/pypi/airflow-config)

```yaml
# config/pipeline.yaml
# @package _global_
_target_: airflow_config.Configuration

dags:
  daily-report:
    schedule: "0 6 * * *"
    start_date: "2025-01-01"
    catchup: false
    tasks:
      report:
        _target_: airflow_config.BashTask
        bash_command: python /opt/jobs/report.py
```

```python
from airflow_config import load_config

config = load_config("config", "pipeline")
config.generate_in_mem()
```

Configuration can provide shared defaults, environment overrides, templates,
extensions, generated Python DAG files, or in-memory DAG registration.

## Documentation

- [Tutorial: generate a DAG from YAML](docs/src/tutorial.md)
- [How-to guides](docs/src/how-to.md)
- [Why configuration and DAG models are separate](docs/src/explanation.md)
- [API reference](docs/src/api.md)

Published documentation is available at
[airflow-laminar.github.io/airflow-config](https://airflow-laminar.github.io/airflow-config/).

## Ecosystem

- [airflow-pydantic](https://github.com/airflow-laminar/airflow-pydantic) supplies the DAG, task, sensor, schedule, pool, and variable models.
- [airflow-supervisor](https://github.com/airflow-laminar/airflow-supervisor) and [supervisor-pydantic](https://github.com/airflow-laminar/supervisor-pydantic) manage supervisord jobs.
- [airflow-systemd](https://github.com/airflow-laminar/airflow-systemd) and [systemd-pydantic](https://github.com/airflow-laminar/systemd-pydantic) manage systemd services.
- [airflow-cron](https://github.com/airflow-laminar/airflow-cron) and [cron-pydantic](https://github.com/airflow-laminar/cron-pydantic) convert crontabs into DAG models.
- [airflow-balancer](https://github.com/airflow-laminar/airflow-balancer) supplies host and port selection extensions.
- [airflow-common](https://github.com/airflow-laminar/airflow-common) supplies common operators and library management.

#### NOTE
This library was generated using [copier](https://copier.readthedocs.io/en/stable/) from the [Base Python Project Template repository](https://github.com/python-project-templates/base).
