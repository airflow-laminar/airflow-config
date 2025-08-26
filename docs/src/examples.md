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

### Example 1 - Operators and Dependencies

```yaml
# config/test.yaml
# @package _global_
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
        _target_: airflow_config.SSHTask
        ssh_conn_id: test
        ssh_hook: airflow_pydantic.tests.conftest.hook
        command: test
        do_xcom_push: true
        cmd_timeout: 10
        get_pty: true
        environment: {"test": "test"}
      task_2:
        _target_: airflow_config.ShortCircuitTask
        python_callable: airflow_config.tests.conftest.should_short_circuit
        dependencies: [task_1]
      task_3:
        _target_: airflow_config.BashTask
        bash_command: "echo '1'"
        dependencies: [task_2]
      task_4:
        _target_: airflow_config.BashTask
        bash_command: "echo `pwd`"
        dependencies: [task_3]
      task_5:
        _target_: airflow_config.PythonTask
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
from datetime import datetime

from airflow.models import DAG
from airflow.providers.ssh.hooks.ssh import SSHHook
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator, ShortCircuitOperator

from airflow_config.tests.conftest import should_short_circuit
from airflow_config.tests.setups.utils.print_hello import print_hello

with DAG(
    description="this is an example dag",
    schedule="0 3 * * *",
    start_date=datetime.fromisoformat("2024-01-01T00:00:00"),
    catchup=False,
    tags=["utility", "test"],
    dag_id="example_dag",
    default_args={
        "owner": "custom_owner",
        "email": ["myemail@myemail.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 0,
        "depends_on_past": False,
    },
) as dag:
    task_1 = SSHOperator(
        do_xcom_push=True,
        ssh_hook=SSHHook(remote_host="test", username="test"),
        ssh_conn_id="test",
        command="test",
        cmd_timeout=10,
        environment={"test": "test"},
        get_pty=True,
        task_id="task_1",
        dag=dag,
    )
    task_2 = ShortCircuitOperator(python_callable=should_short_circuit, task_id="task_2", dag=dag)
    task_3 = BashOperator(bash_command="echo '1'", task_id="task_3", dag=dag)
    task_4 = BashOperator(bash_command="echo `pwd`", task_id="task_4", dag=dag)
    task_5 = PythonOperator(
        python_callable=print_hello,
        op_args=[],
        op_kwargs={},
        templates_dict={},
        templates_exts=None,
        show_return_value_in_logs=True,
        task_id="task_5",
        dag=dag,
    )
    task_1 >> task_2
    task_2 >> task_3
    task_3 >> task_4
    task_4 >> task_5
```

### Example 2 - Template Tasks


```yaml
# config/test.yaml
# @package _global_

# @package _global_
_target_: airflow_config.Configuration

templates:
  dag:
    dag_template:
      _target_: airflow_config.DagArgs
      default_args:
        _target_: airflow_config.TaskArgs
        owner: test
        email: [myemail@myemail.com]
        email_on_failure: false
        email_on_retry: false
        retries: 0
        depends_on_past: false
      schedule: "01:00"
      start_date: "2024-01-01"
      catchup: false
      tags: ["utility", "test"]
  tasks:
    task_template:
      _target_: airflow_config.PythonTaskArgs
      python_callable: airflow_config.tests.setups.utils.print_hello.print_hello
      op_args: []
      op_kwargs: {}
      templates_dict: {}
      templates_exts: null
      show_return_value_in_logs: true
      dependencies: [task_4]
    ssh_task_template:
      _target_: airflow_config.SSHTaskArgs
      ssh_conn_id: test
      ssh_hook: airflow_pydantic.tests.conftest.hook
      command: test
      do_xcom_push: true
      cmd_timeout: 10
      get_pty: true
      environment: {"test": "test"}

dags:
  example_dag:
    template: ${templates.dag.dag_template}
    default_args:
      owner: "custom_owner"
    description: "this is an example dag"
    schedule: "0 3 * * *"
    tasks:
      task_1:
        _target_: airflow_config.PythonOperator
        template: ${templates.tasks.task_template}
      task_2:
        _target_: airflow_config.SSHOperator
        template: ${templates.tasks.ssh_task_template}
        dependencies: [task_1]
        environment: {"blerg": "blerg"}
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
from datetime import datetime

from airflow.models import DAG
from airflow.providers.ssh.hooks.ssh import SSHHook
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.providers.standard.operators.python import PythonOperator

from airflow_config.tests.setups.utils.print_hello import print_hello

with DAG(
    description="this is an example dag",
    schedule="0 3 * * *",
    start_date=datetime.fromisoformat("2024-01-01T00:00:00"),
    catchup=False,
    tags=["utility", "test"],
    dag_id="example_dag",
    default_args={
        "owner": "custom_owner",
        "email": ["myemail@myemail.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 0,
        "depends_on_past": False,
    },
) as dag:
    task_1 = PythonOperator(
        python_callable=print_hello,
        op_args=[],
        op_kwargs={},
        templates_dict={},
        templates_exts=None,
        show_return_value_in_logs=True,
        task_id="task_1",
        dag=dag,
    )
    task_2 = SSHOperator(
        do_xcom_push=True,
        ssh_hook=SSHHook(remote_host="test", username="test"),
        ssh_conn_id="test",
        command="test",
        cmd_timeout=10,
        environment={"blerg": "blerg", "test": "test"},
        get_pty=True,
        task_id="task_2",
        dag=dag,
    )
    task_1 >> task_2
```


### Example 3 - Attribute Access / HighAvailabilityTask


```yaml
# @package _global_
_target_: airflow_config.Configuration
default_task_args:
  _target_: airflow_config.TaskArgs
  owner: laminar
  email: [dev@paine.nyc]
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
  test-high-availability:
    description: "Test HA operator"
    tags: ["test", "utility"]
    schedule: "0 12 * * *"
    tasks:
      pre:
        _target_: airflow_pydantic.PythonTask
        python_callable: validation_dags.test_ha_foo._pre
      ha:
        _target_: airflow_ha.HighAvailabilityTask
        python_callable: validation_dags.test_ha_foo._choose
        runtime: 120
        maxretrigger: 2
        endtime: 23:00:00
        timeout: 1000
        poke_interval: 10
        dependencies: [pre]
      retrigger-fail:
        _target_: airflow_pydantic.PythonTask
        python_callable: validation_dags.test_ha_foo._pre
        dependencies: [ha]
```

**validation_dags.test_ha_foo**
```python
from random import choice

from airflow_ha import Action, Result


def _pre(**kwargs):
    return "test"


def _choose(**kwargs):
    return choice(
        (
            (Result.PASS, Action.CONTINUE),
            (Result.PASS, Action.RETRIGGER),
            # (Result.PASS, Action.STOP),
            # (Result.FAIL, Action.CONTINUE),
            # (Result.FAIL, Action.RETRIGGER),
            # (Result.FAIL, Action.STOP),
        )
    )
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
from datetime import datetime, time

from airflow.models import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow_ha.operator import HighAvailabilitySensor
from validation_dags.test_ha_foo import _choose, _pre

with DAG(
    description="Test HA operator",
    schedule="0 12 * * *",
    start_date=datetime.fromisoformat("2025-01-01T00:00:00-04:56"),
    max_active_runs=1,
    catchup=False,
    tags=["test", "utility"],
    dag_id="test-high-availability",
    default_args={
        "owner": "laminar",
        "email": ["dev@paine.nyc"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 0,
        "depends_on_past": False,
    },
) as dag:
    pre = PythonOperator(python_callable=_pre, task_id="pre", dag=dag)
    ha = HighAvailabilitySensor(
        poke_interval=10.0,
        timeout=1000.0,
        python_callable=_choose,
        runtime=120,
        endtime=time(23, 0, 0, 0),
        maxretrigger=2,
        task_id="ha",
        dag=dag,
    )
    retrigger_fail = PythonOperator(
        python_callable=_pre, task_id="retrigger-fail", dag=dag
    )
    pre >> ha
    ha >> retrigger_fail
```

### Example 4 - Supervisor / Balancer


```yaml
# @package _global_
_target_: airflow_config.Configuration
default_task_args:
  _target_: airflow_config.TaskArgs
  owner: laminar
  email: [dev@paine.nyc]
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
  test-supervisor:
    description: "Test supervisor"
    tags: ["test", "utility"]
    schedule: "0 0 * * *"
    tasks:
      supervisor:
        _target_: airflow_supervisor.SupervisorSSHTask
        cfg:
          _target_: airflow_supervisor.SupervisorSSHAirflowConfiguration
          check_interval: 10
          check_timeout: 60
          cleanup: true
          endtime: 23:00:00
          maxretrigger: 5
          restart_on_initial: true
          restart_on_retrigger: false
          runtime: 360
          ssh_operator_args:
            cmd_timeout: 63
          stop_on_exit: true
          working_dir: "/tmp/supervisor"
          program:
            test:
              _target_: airflow_supervisor.ProgramConfiguration
              command: bash -c "sleep 3600; exit 0"
        host:
          _target_: airflow_balancer.HostQuery
          balancer: ${extensions.balancer}
          queue: primary
        port:
          _target_: airflow_balancer.PortQuery
          balancer: ${extensions.balancer}
          name: test-supervisor-port

extensions:
  balancer:
    _target_: airflow_balancer.BalancerConfiguration
    default_key_file: /home/airflow/.ssh/id_rsa
    hosts:
      - name: myhost
        os: ubuntu
        size: 32
        queues: [primary]
        tags: []
    ports:
      - name: test-supervisor-port
        host_name: nuc2
        port: 9091
        tags: [supervisor]
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
from datetime import datetime, time, timedelta
from pathlib import Path

from airflow.models import DAG
from airflow.models.pool import Pool
from airflow_pydantic import Host, Port
from airflow_supervisor.airflow.ssh import SupervisorSSH

with DAG(
    description="Test supervisor",
    schedule="0 0 * * *",
    start_date=datetime.fromisoformat("2025-01-01T00:00:00-04:56"),
    max_active_runs=1,
    catchup=False,
    tags=["test", "utility"],
    dag_id="test-supervisor",
    default_args={
        "owner": "laminar",
        "email": ["dev@paine.nyc"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 0,
        "depends_on_past": False,
    },
) as dag:
    supervisor = SupervisorSSH(
        cfg={
            "inet_http_server": {"port": "*:9001", "username": None, "password": None},
            "program": {
                "test": {
                    "command": 'bash -c "sleep 3600; exit 0"',
                    "autostart": False,
                    "startsecs": 1,
                    "startretries": None,
                    "autorestart": False,
                    "exitcodes": [0],
                    "stopsignal": "TERM",
                    "stopwaitsecs": 30,
                    "stopasgroup": True,
                    "killasgroup": True,
                    "stdout_logfile": Path("/tmp/supervisor/test/output.log"),
                    "stderr_logfile": Path("/tmp/supervisor/test/error.log"),
                    "directory": Path("/tmp/supervisor/test"),
                }
            },
            "rpcinterface": {
                "supervisor": {
                    "rpcinterface_factory": "supervisor.rpcinterface:make_main_rpcinterface"
                }
            },
            "config_path": Path("/tmp/supervisor/supervisord.conf"),
            "working_dir": Path("/tmp/supervisor"),
            "check_interval": timedelta(10.0),
            "check_timeout": timedelta(60.0),
            "runtime": timedelta(360.0),
            "endtime": time(23, 0, 0, 0),
            "maxretrigger": 5,
            "stop_on_exit": True,
            "cleanup": True,
            "restart_on_initial": True,
            "restart_on_retrigger": False,
            "ssh_operator_args": {"cmd_timeout": 63},
        },
        host=Host(
            name="myhost",
            key_file="/home/airflow/.ssh/id_rsa",
            os="ubuntu",
            pool=Pool.create_or_update_pool(
                name="myhost",
                slots=32,
                description="Balancer pool for host(myhost)",
                include_deferred=False,
            ).pool,
            size=32,
            queues=["primary"],
            tags=[],
        ),
        port=Port(
            name="test-supervisor-port",
            host=Host(
                name="myhost",
                key_file="/home/airflow/.ssh/id_rsa",
                os="ubuntu",
                pool=Pool.create_or_update_pool(
                    name="myhost",
                    slots=32,
                    description="Balancer pool for host(myhost)",
                    include_deferred=False,
                ).pool,
                size=32,
                queues=["primary"],
                tags=[],
            ),
            host_name="myhost",
            port=9091,
            tags=["supervisor"],
        ),
        task_id="supervisor",
        dag=dag,
    )
```