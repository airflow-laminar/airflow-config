# How-to guides

These guides cover configuration composition, materialization, templates,
environment selection, and ecosystem integrations.

## How to apply shared DAG and task defaults

Set global defaults and override only the fields that differ:

```yaml
# @package _global_
_target_: airflow_config.Configuration

default_task_args:
  _target_: airflow_config.TaskArgs
  owner: platform
  retries: 3
  retry_delay: 00:05:00

default_dag_args:
  _target_: airflow_config.DagArgs
  start_date: "2025-01-01"
  catchup: false
  max_active_runs: 1
  tags: [managed]

dags:
  hourly-import:
    schedule: "@hourly"
  daily-report:
    schedule: "0 6 * * *"
    default_args:
      owner: analytics
```

Per-DAG values override `default_dag_args`. Per-DAG `default_args` values
override `default_task_args` field by field.

## How to select an environment

Keep one file per environment and choose it at load time:

```text
config/
├── dev.yaml
└── prod.yaml
```

```python
import os

from airflow_config import load_config

environment = os.environ.get("AIRFLOW_ENV", "dev")
config = load_config("config", environment)
```

Use Hydra overrides for narrow runtime changes:

```python
config = load_config(
    "config",
    "prod",
    overrides=["dags.daily-report.schedule=0 7 * * *"],
)
```

## How to generate Python DAG files

Write one deterministic file per configured DAG:

```python
from airflow_config import load_config

config = load_config("config", "prod")
config.generate("generated_dags", airflow_major_version=3)
```

Commit or deploy the generated directory when DAG review and an Airflow runtime
without Hydra are preferred. Unchanged files are not rewritten.

To generate without installing Airflow, use the command-line interface and select
the target major version explicitly:

```console
airflow-config config/prod.yaml --output-dir generated_dags --airflow-version 3
```

## How to generate DAGs in memory

Register DAG objects in the calling module:

```python
from airflow_config import load_config

config = load_config("config", "prod")
config.generate_in_mem()
```

Use this path when the scheduler should consume YAML directly. Keep the loader
file and configuration directory at stable relative paths.

## How to combine generated and hand-written DAGs

Create native Airflow DAGs with the configuration-aware wrapper:

```python
from airflow_config import DAG, load_config

config = load_config("config", "prod")

with DAG(dag_id="hand-written", config=config, schedule="@daily") as dag:
    pass

config.generate_in_mem()
```

The wrapper applies matching shared and per-DAG options before the context opens.
Configured DAG models can coexist with explicitly authored DAGs.

## How to reuse DAG and task templates

Store typed templates and reference them with OmegaConf interpolation:

```yaml
templates:
  dag:
    batch:
      _target_: airflow_config.DagArgs
      start_date: "2025-01-01"
      catchup: false
      tags: [batch]
  task:
    shell:
      _target_: airflow_config.BashTaskArgs
      retries: 2
      env:
        MODE: production

dags:
  report:
    template: ${templates.dag.batch}
    schedule: "@daily"
    tasks:
      build:
        _target_: airflow_config.BashTask
        template: ${templates.task.shell}
        bash_command: python /opt/jobs/report.py
```

Explicit DAG and task fields override template fields.

## How to create task dependencies

List upstream task IDs in `dependencies`:

```yaml
tasks:
  extract:
    _target_: airflow_config.BashTask
    bash_command: extract
  transform:
    _target_: airflow_config.BashTask
    bash_command: transform
    dependencies: [extract]
  publish:
    _target_: airflow_config.BashTask
    bash_command: publish
    dependencies: [transform]
```

Multiple downstream tasks may name the same upstream task to create branches.
Every dependency must name a task in the same DAG.

## How to disable DAGs by environment

Use the registered `eq` and `neq` resolvers:

```yaml
env: prod

dags:
  production-report:
    enabled: ${eq:${env},prod}
    schedule: "@daily"
  development-report:
    enabled: ${neq:${env},prod}
    schedule: null
```

An explicitly disabled DAG exits before registration. `default_dag_args.enabled`
provides a global default that individual DAGs can override.

## How to add a supervisord-managed task

Install `airflow-supervisor` and use its task model:

```yaml
dags:
  long-running-worker:
    schedule: "@daily"
    tasks:
      worker:
        _target_: airflow_supervisor.SupervisorTask
        cfg:
          working_dir: /var/tmp/worker-supervisor
          stop_on_exit: true
          cleanup: true
          program:
            worker:
              command: python /opt/jobs/worker.py
```

The underlying process configuration is supplied by
[supervisor-pydantic](https://github.com/airflow-laminar/supervisor-pydantic).

## How to add a systemd-managed task

Install `airflow-systemd` and use its task model:

```yaml
dags:
  system-service:
    schedule: "@daily"
    tasks:
      service:
        _target_: airflow_systemd.SystemdTask
        cfg:
          scope: user
          service:
            report:
              service:
                type: exec
                exec_start: /opt/jobs/report
```

Unit-file models come from
[systemd-pydantic](https://github.com/airflow-laminar/systemd-pydantic).

## How to import cron jobs

Merge DAG models returned by `airflow-cron`:

```python
from airflow_config import Configuration, load_config
from airflow_cron import CronAirflowConfiguration, create_dags

base = load_config("config", "prod")
cron = CronAirflowConfiguration.load("cron.yaml")

config = Configuration.model_validate(
    {
        **base.model_dump(),
        "dags": {**(base.dags or {}), **create_dags(cron)},
    }
)
config.generate_in_mem()
```

The source crontab models are provided by
[cron-pydantic](https://github.com/airflow-laminar/cron-pydantic).

## How to select a host with airflow-balancer

Store the balancer in `extensions` and interpolate it into an SSH task query:

```yaml
extensions:
  balancer:
    _target_: airflow_pydantic.BalancerConfiguration
    hosts:
      - name: reports-1
        tags: [reports]

dags:
  remote-report:
    start_date: "2025-01-01"
    tasks:
      report:
        _target_: airflow_config.SSHTask
        ssh_hook:
          _target_: airflow_pydantic.BalancerHostQueryConfiguration
          balancer: ${extensions.balancer}
          tag: reports
        command: python /opt/jobs/report.py
```

Install [airflow-balancer](https://github.com/airflow-laminar/airflow-balancer)
when using its full configuration and runtime selection features.

## How to inspect configurations visually

Start the standalone viewer with a configuration path:

```bash
airflow-config-viewer --help
```

Airflow 2 also discovers the packaged viewer plugin through its plugin entry
point. The standalone viewer is available without enabling the webserver plugin.
