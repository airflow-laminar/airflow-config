# Examples

## Load defaults from config


```yaml
# config/test.yaml
# @package _global_
_target_: airflow_config.Configuration
default_args:
  _target_: airflow_config.DefaultTaskArgs
  owner: test
```

```python
from airflow_config import load_config, DAG, create_dag

conf = load_config("config", "test")
d = create_dag("config", "test")
# or d = DAG(dag_id="test-dag", config=conf)

assert conf.default_args.owner == "test"
```

## Load more defaults from config

```yaml
# config/test.yaml
# @package _global_
_target_: airflow_config.Configuration
default_args:
  _target_: airflow_config.DefaultTaskArgs
  owner: test
  email: [myemail@myemail.com]
  email_on_failure: false
  email_on_retry: false
  retries: 0
  depends_on_past: false
default_dag_args:
  _target_: airflow_config.DagArgs
  schedule: "01:10"
  start_date: "2024-01-01"
  catchup: false
  tags: ["utility", "test"]
```

```python
from airflow_config import load_config, DAG, create_dag

conf = load_config("config", "test")
d = create_dag("config", "test")
# or d = DAG(dag_id="test-dag", config=conf)
assert conf.default_args.owner == "test"
assert conf.default_args.email == ["myemail@myemail.com"]
assert conf.default_args.email_on_failure is False
assert conf.default_args.email_on_retry is False
assert conf.default_args.retries == 0
assert conf.default_args.depends_on_past is False
assert conf.default_dag_args.start_date == datetime(2024, 1, 1)
assert conf.default_dag_args.catchup is False
assert conf.default_dag_args.tags == ["utility", "test"]
```

## Specialize individual DAGs

```yaml
# config/test.yaml
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

dags:
  example_dag:
    default_args:
      owner: "custom_owner"
    description: "this is an example dag"
    schedule: "0 3 * * *"

  example_dag2:
    default_args:
      owner: "custom_owner2"
    schedule: "0 4 * * *"
```

```python
from airflow_config import load_config, DAG, create_dag

conf = load_config("config", "test")
d = create_dag("config", "test")
# or d = DAG(dag_id="test-dag", config=conf)
assert d.default_args["owner"] == "test"
assert d.default_args["email"] == ["myemail@myemail.com"]
assert d.default_args["email_on_failure"] is False
assert d.default_args["email_on_retry"] is False
assert d.default_args["retries"] == 0
assert d.default_args["depends_on_past"] is False
assert d.schedule_interval == timedelta(seconds=3600)
assert isinstance(d.timetable, DeltaDataIntervalTimetable)
assert isinstance(d.timetable._delta, timedelta)
assert d.start_date.year == 2024
assert d.start_date.month == 1
assert d.start_date.day == 1
assert d.catchup is False
assert set(d.tags) == set(["utility", "test"])

# specialized by dag_id from shared config file
d = DAG(dag_id="example_dag", config=conf)
assert d.default_args["owner"] == "custom_owner"
assert d.default_args["email"] == ["myemail@myemail.com"]
assert d.schedule_interval == "0 3 * * *"

# specialized by dag_id from shared config file
d = DAG(dag_id="example_dag2", config=conf)
assert d.default_args["owner"] == "custom_owner2"
assert d.default_args["email"] == ["myemail@myemail.com"]
assert d.schedule_interval == "0 4 * * *"
```

## Declarative Dags - "DAG Factory"

```yaml
# config/test.yaml
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

dags:
  example_dag:
    default_args:
      owner: "custom_owner"
    description: "this is an example dag"
    schedule: "0 3 * * *"
    tasks:
      task_1:
        _target_: airflow_config.SSHOperator
        ssh_conn_id: test
        ssh_hook: airflow_pydantic.tests.conftest.hook
        command: test
        do_xcom_push: true
        cmd_timeout: 10
        get_pty: true
        environment: {"test": "test"}
      task_2:
        _target_: airflow_config.ShortCircuitOperator
        python_callable: airflow_config.tests.conftest.should_short_circuit
        dependencies: [task_1]
      task_3:
        _target_: airflow_config.BashOperator
        bash_command: "echo '1'"
        dependencies: [task_2]
      task_4:
        _target_: airflow_config.BashOperator
        bash_command: "echo `pwd`"
        dependencies: [task_3]
      task_5:
        _target_: airflow_config.PythonOperator
        python_callable: airflow_config.tests.setups.utils.print_hello.print_hello
        op_args: []
        op_kwargs: {}
        templates_dict: {}
        templates_exts: null
        show_return_value_in_logs: true
        dependencies: [task_4]
```

```python
from pathlib import Path
from airflow_config import load_config
conf = load_config("config", "test")
conf.generate(Path(__file__).parent.resolve())
```

**Generated DAG**

```python
# Generated by airflow-config
from airflow.models import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.operators.python import ShortCircuitOperator
from airflow.providers.ssh.hooks.ssh import SSHHook
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow_config.tests.conftest import should_short_circuit
from airflow_config.tests.setups.utils.print_hello import print_hello
with DAG('example_dag') as dag:
    task_1 = SSHOperator(do_xcom_push=True, ssh_hook=SSHHook(remote_host='test', username='test', port=22, cmd_timeout=10, keepalive_interval=30, banner_timeout=30.0), ssh_conn_id='test', command='test', cmd_timeout=10, environment={'test': 'test'}, get_pty=True, task_id='task_1', dag=dag)
    task_2 = ShortCircuitOperator(python_callable=should_short_circuit, task_id='task_2', dag=dag)
    task_3 = BashOperator(bash_command="echo '1'", append_env=False, output_encoding='utf-8', skip_on_exit_code=99, task_id='task_3', dag=dag)
    task_4 = BashOperator(bash_command='echo `pwd`', append_env=False, output_encoding='utf-8', skip_on_exit_code=99, task_id='task_4', dag=dag)
    task_5 = PythonOperator(python_callable=print_hello, op_args=[], op_kwargs={}, templates_dict={}, show_return_value_in_logs=True, task_id='task_5', dag=dag)
    task_1 >> task_2
    task_2 >> task_3
    task_3 >> task_4
    task_4 >> task_5
```
