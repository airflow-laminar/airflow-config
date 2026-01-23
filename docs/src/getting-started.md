# Getting Started

## Why airflow-config?

`airflow-config` enables **YAML-driven, declarative configuration** for Apache Airflow DAGs. Instead of hardcoding settings in Python files, you define your DAG configurations in YAML files that can be:

- **Centrally managed**: Change settings across multiple DAGs from a single file
- **Environment-specific**: Maintain separate configurations for dev, staging, and production
- **Version controlled**: Track configuration changes separately from code changes
- **Validated**: Pydantic models ensure configuration correctness before deployment

**Key Benefits:**

- **Separation of Concerns**: Keep business logic separate from DAG configuration
- **No Code Changes**: Update schedules, retries, emails, etc. without touching Python
- **DAG Factory**: Generate entire DAGs declaratively from YAML
- **Type Safety**: Pydantic validation catches configuration errors early
- **Extensibility**: Integrate with other airflow-laminar libraries seamlessly

## The airflow-laminar Ecosystem

`airflow-config` is the configuration backbone of the [airflow-laminar](https://github.com/airflow-laminar) ecosystem. It integrates with several libraries to provide a comprehensive Airflow development experience:

### Core Foundation: airflow-pydantic

[**airflow-pydantic**](https://github.com/airflow-laminar/airflow-pydantic) is the underpinning library that makes `airflow-config` possible. It provides:

- **Pydantic Models**: Every Airflow construct (DAGs, Operators, Sensors, Hooks) has a corresponding Pydantic model
- **Serialization**: Full JSON/YAML serialization support for all Airflow constructs
- **Code Generation**: Models can render themselves as Python code via the `render()` method
- **Instantiation**: Models can create runtime Airflow objects via the `instantiate()` method
- **Type Validation**: Automatic validation of all configuration values

```yaml
# airflow-pydantic models power the _target_ declarations
default_args:
  _target_: airflow_pydantic.TaskArgs  # Pydantic model from airflow-pydantic
  owner: data-team
  retries: 3
```

### Host & Port Management: airflow-balancer

[**airflow-balancer**](https://github.com/airflow-laminar/airflow-balancer) provides utilities for tracking hosts and ports across your infrastructure. When integrated with `airflow-config`, you can:

- Define your host infrastructure in YAML
- Automatically create Airflow pools for each host
- Select hosts based on queues, OS, tags, or custom criteria
- Track port usage to avoid conflicts

```yaml
# config/config.yaml
extensions:
  balancer:
    _target_: airflow_balancer.BalancerConfiguration
    default_key_file: /home/airflow/.ssh/id_rsa
    hosts:
      - name: worker1
        os: ubuntu
        size: 16
        queues: [compute]
```

### Long-Running Jobs: airflow-supervisor

[**airflow-supervisor**](https://github.com/airflow-laminar/airflow-supervisor) enables running long-running or always-on jobs with [supervisord](http://supervisord.org). Integration with `airflow-config` allows you to:

- Define supervisor configurations in YAML
- Automatically generate supervisor DAGs
- Combine with `airflow-balancer` for host selection

```yaml
dags:
  long-running-job:
    tasks:
      supervisor:
        _target_: airflow_supervisor.SupervisorSSHTask
        cfg:
          _target_: airflow_supervisor.SupervisorSSHAirflowConfiguration
          runtime: 3600
          program:
            worker:
              _target_: airflow_supervisor.ProgramConfiguration
              command: python worker.py
```

### Common Operators: airflow-common

[**airflow-common**](https://github.com/airflow-laminar/airflow-common) provides common operators, topology helpers, and library management tasks. It integrates with `airflow-config` to provide:

- **Control Operators**: `Skip`, `Fail`, `Pass` for workflow control
- **Topology Helpers**: Functions for building complex DAG structures
- **Library Management**: Operators for installing pip/conda packages

## Installation

Install from PyPI:

```bash
pip install airflow-config
```

For use with Apache Airflow 2.x:

```bash
pip install airflow-config[airflow]
```

For use with Apache Airflow 3.x:

```bash
pip install airflow-config[airflow3]
```

Or via conda:

```bash
conda install airflow-config -c conda-forge
```

## Basic Usage

### Step 1: Create a Configuration File

Create a `config` directory in your Airflow DAGs folder and add a configuration file:

```yaml
# dags/config/dev.yaml
# @package _global_
_target_: airflow_config.Configuration

default_args:
  _target_: airflow_config.TaskArgs
  owner: data-team
  email: [alerts@example.com]
  email_on_failure: true
  email_on_retry: false
  retries: 3
  depends_on_past: false

default_dag_args:
  _target_: airflow_config.DagArgs
  schedule: "@daily"
  start_date: "2024-01-01"
  catchup: false
  tags: ["production"]
```

### Step 2: Load Configuration in Your DAG

```python
# dags/my_dag.py
from airflow.providers.standard.operators.bash import BashOperator
from airflow_config import DAG, load_config

# Load the configuration
config = load_config(config_name="dev")

# Create the DAG with config
with DAG(
    dag_id="my-etl-pipeline",
    description="Daily ETL pipeline",
    config=config,
):
    extract = BashOperator(task_id="extract", bash_command="python extract.py")
    transform = BashOperator(task_id="transform", bash_command="python transform.py")
    load = BashOperator(task_id="load", bash_command="python load.py")

    extract >> transform >> load
```

### Step 3: Environment-Specific Configurations

Create separate configs for different environments:

```yaml
# dags/config/prod.yaml
# @package _global_
_target_: airflow_config.Configuration

default_args:
  _target_: airflow_config.TaskArgs
  owner: data-team
  email: [production-alerts@example.com]
  email_on_failure: true
  retries: 5  # More retries in production

default_dag_args:
  _target_: airflow_config.DagArgs
  schedule: "0 6 * * *"  # 6 AM daily in production
  start_date: "2024-01-01"
  catchup: false
  tags: ["production", "critical"]
```

```python
# dags/my_dag.py
import os
from airflow_config import DAG, load_config

# Load environment-specific config
env = os.getenv("AIRFLOW_ENV", "dev")
config = load_config(config_name=env)

with DAG(dag_id="my-etl-pipeline", config=config):
    # ... tasks
```

## DAG Factory: Fully Declarative DAGs

`airflow-config` can generate entire DAGs from YAML, similar to [dag-factory](https://github.com/astronomer/dag-factory) but with additional benefits. There are two approaches to DAG generation:

| Approach | Method | Use Case |
|----------|--------|----------|
| **File Generation** | `config.generate()` | Generate Python DAG files that can be version controlled and inspected |
| **In-Memory Generation** | `config.generate_in_mem()` | Create DAGs at runtime without writing files |

### Defining DAGs in YAML

First, define your DAGs declaratively in YAML:

```yaml
# dags/config/declarative.yaml
# @package _global_
_target_: airflow_config.Configuration

default_args:
  _target_: airflow_config.TaskArgs
  owner: data-team
  retries: 2

default_dag_args:
  _target_: airflow_config.DagArgs
  start_date: "2024-01-01"
  catchup: false

dags:
  etl-pipeline:
    description: "ETL Pipeline"
    schedule: "0 6 * * *"
    tags: ["etl", "production"]
    tasks:
      extract:
        _target_: airflow_config.BashTask
        bash_command: "python extract.py"
      transform:
        _target_: airflow_config.PythonTask
        python_callable: my_module.transform
        dependencies: [extract]
      load:
        _target_: airflow_config.BashTask
        bash_command: "python load.py"
        dependencies: [transform]
```

### Approach 1: Generate Python DAG Files

Use `config.generate()` to create actual Python files on disk. This approach is useful when you want to:

- **Version control** the generated DAG code
- **Inspect and debug** the generated Python code
- **Review changes** before deployment
- **Use standard Airflow tooling** that expects `.py` files

```python
# dags/generate_dags.py
from pathlib import Path
from airflow_config import load_config

config = load_config("config", "declarative")
config.generate(Path(__file__).parent)  # Generates Python DAG files
```

This creates a file like `dags/etl-pipeline.py`:

```python
# Generated by airflow-config
from datetime import datetime

from airflow.models import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator

from my_module import transform

with DAG(
    description="ETL Pipeline",
    schedule="0 6 * * *",
    start_date=datetime.fromisoformat("2024-01-01T00:00:00"),
    catchup=False,
    tags=["etl", "production"],
    dag_id="etl-pipeline",
    default_args={
        "owner": "data-team",
        "retries": 2,
    },
) as dag:
    extract = BashOperator(bash_command="python extract.py", task_id="extract", dag=dag)
    transform_task = PythonOperator(python_callable=transform, task_id="transform", dag=dag)
    load = BashOperator(bash_command="python load.py", task_id="load", dag=dag)
    extract >> transform_task
    transform_task >> load
```

### Approach 2: In-Memory DAG Generation

Use `config.generate_in_mem()` to create DAGs directly in memory at runtime. This approach is useful when you want to:

- **Avoid file management** - no generated files to maintain
- **Dynamic DAGs** - DAGs are created fresh on each scheduler parse
- **Simpler deployment** - just deploy the YAML configs and one Python file
- **Cleaner DAG folder** - fewer Python files to manage

```python
# dags/generate_dags.py
from pathlib import Path
from airflow_config import load_config

config = load_config("config", "declarative")
config.generate_in_mem(dir=Path(__file__).parent)  # Creates DAGs in memory
```

> **Note:** When using `generate_in_mem()`, a placeholder DAG is created to ensure Airflow's scheduler recognizes the file. The actual DAGs are injected into the module's global namespace.

### Comparison

| Feature | `generate()` | `generate_in_mem()` |
|---------|-------------|---------------------|
| Creates Python files | ✅ Yes | ❌ No |
| Version controllable output | ✅ Yes | ❌ No |
| Inspectable generated code | ✅ Yes | ⚠️ Via `doc_md` |
| Dynamic at runtime | ❌ No (must re-run) | ✅ Yes |
| File management overhead | Higher | Lower |
| Debugging ease | Easier | Harder |

### Hybrid Approach

You can use file generation during development for easier debugging, then switch to in-memory generation in production:

```python
# dags/generate_dags.py
import os
from pathlib import Path
from airflow_config import load_config

config = load_config("config", "declarative")

if os.getenv("AIRFLOW_ENV") == "development":
    # Generate files for easier debugging
    config.generate(Path(__file__).parent)
else:
    # Use in-memory for cleaner production deployment
    config.generate_in_mem(dir=Path(__file__).parent)
```

## Visualization

`airflow-config` includes a built-in UI for viewing your configurations.

### Airflow Plugin

The plugin adds a "Config" menu item to the Airflow toolbar, allowing you to browse and validate your configurations directly in Airflow.

### Standalone Viewer

You can also run the viewer as a standalone application:

```bash
airflow-config-viewer
```

## Next Steps

- See the [Examples](examples.md) page for comprehensive usage patterns
- Check the [API Reference](API.md) for complete API documentation
- Explore the [Test Setups](https://github.com/airflow-laminar/airflow-config/tree/main/airflow_config/tests/setups) for real-world examples
