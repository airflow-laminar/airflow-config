# Why configuration and DAG models are separate

`airflow-config` treats DAG authoring as configuration composition followed by
materialization. Hydra composes YAML; Pydantic validates the resulting object
graph; `airflow-pydantic` renders or instantiates Airflow objects. Each layer has
one responsibility.

## Composition before execution

Airflow DAG files are executable modules, which makes ordinary Python imports a
natural configuration mechanism. That approach becomes repetitive when many
DAGs share schedules, retry policies, hosts, pools, and task shapes.

Hydra adds named configuration files, defaults lists, search paths,
interpolation, and command-style overrides before any Airflow object is
created. Pydantic then converts Hydra's generic data into a typed graph. This
ordering makes composition flexible without leaving validation until task
execution.

## Why `_target_` is the extension boundary

Hydra `_target_` entries identify Python model classes. A Bash task, SSH task,
supervisord lifecycle, systemd lifecycle, and host query can therefore appear
in the same task mapping without `airflow-config` knowing every integration in
advance.

This is deliberately a model boundary rather than an arbitrary code-execution
framework. Targets construct configuration objects; Airflow still owns DAG
parsing and operator execution. Configuration repositories should receive the
same review and access controls as Python DAG repositories.

## Generated source versus in-memory DAGs

Generated Python makes deployment artifacts explicit. Reviewers can inspect
the exact DAG source, and the scheduler does not need Hydra or source YAML.
Generation adds an artifact-management step and requires regeneration after
configuration changes.

In-memory generation keeps YAML authoritative and eliminates generated-file
drift. It places configuration loading on the scheduler's DAG-import path, so
dependency availability and parse performance matter more.

The two modes share one `Configuration` model and can coexist. Teams can use
generated files for controlled production releases and in-memory generation
for development without changing the YAML schema.

## Relationship to airflow-pydantic

[airflow-pydantic](https://github.com/airflow-laminar/airflow-pydantic) defines
the typed DAG vocabulary and can be used independently from Python.
`airflow-config` owns discovery, Hydra composition, shared defaults,
environment selection, templates, and materialization across collections of
DAGs.

This division keeps the data model reusable and prevents the configuration
loader from becoming a second Airflow API.

## Relationship to DAG factories

Like other DAG factories, `airflow-config` reduces repeated Python and makes
DAG structures data-driven. Its distinguishing choice is to use public
Pydantic models as the schema and Hydra as the composition engine. The benefits
are Python/YAML parity, normal Pydantic serialization, and an open extension
boundary. The cost is exposure to Hydra concepts such as search paths,
defaults, packages, and interpolation.

Projects that need only a few static DAGs may find direct Python clearer. The
configuration layer becomes valuable when shared policy, environment variants,
generated artifacts, or third-party model extensions outweigh that additional
machinery.

## The wider ecosystem

The extension boundary connects configuration to runtime-specific models:

- [airflow-supervisor](https://github.com/airflow-laminar/airflow-supervisor) and [supervisor-pydantic](https://github.com/airflow-laminar/supervisor-pydantic) model supervisord workloads.
- [airflow-systemd](https://github.com/airflow-laminar/airflow-systemd) and [systemd-pydantic](https://github.com/airflow-laminar/systemd-pydantic) model systemd workloads.
- [airflow-cron](https://github.com/airflow-laminar/airflow-cron) and [cron-pydantic](https://github.com/airflow-laminar/cron-pydantic) import cron workloads.
- [airflow-balancer](https://github.com/airflow-laminar/airflow-balancer) composes host, port, queue, and pool selection.
- [airflow-common](https://github.com/airflow-laminar/airflow-common) contributes common operators and library management.

The result is one declarative graph whose components retain independent owners
and release cycles.
