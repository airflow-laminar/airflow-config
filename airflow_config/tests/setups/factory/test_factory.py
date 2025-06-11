from datetime import datetime, timedelta

from airflow.timetables.interval import DeltaDataIntervalTimetable

from airflow_config import DAG, create_dag, load_config


def test_config_and_options():
    conf = load_config("config", "factory")
    assert conf.default_args.owner == "test"
    assert conf.default_args.email == ["myemail@myemail.com"]
    assert conf.default_args.email_on_failure is False
    assert conf.default_args.email_on_retry is False
    assert conf.default_args.retries == 0
    assert conf.default_args.depends_on_past is False
    # assert conf.global_.schedule == timedelta(seconds=60)
    assert conf.default_dag_args.start_date == datetime(2024, 1, 1)
    assert conf.default_dag_args.catchup is False
    assert conf.default_dag_args.tags == ["utility", "test"]

    assert conf.dags["example_dag"].default_args.owner == "custom_owner"


def test_create_dag_from_config():
    conf = load_config("config", "factory")
    d = DAG(dag_id="testdag", config=conf)
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
    assert d.tags == ["utility", "test"]

    d = DAG(dag_id="example_dag", config=conf)
    assert d.default_args["owner"] == "custom_owner"
    assert d.default_args["email"] == ["myemail@myemail.com"]
    assert d.schedule_interval == "0 3 * * *"


def test_create_dag_tasks_from_config():
    conf = load_config("config", "factory")
    d = DAG(dag_id="example_dag", config=conf)
    assert len(d.tasks) == 5
    assert d.tasks[0].task_id == "task_1"
    assert d.tasks[1].task_id == "task_2"
    assert d.tasks[1].upstream_task_ids == {"task_1"}
    assert d.tasks[2].task_id == "task_3"
    assert d.tasks[2].upstream_task_ids == {"task_2"}
    assert d.tasks[3].task_id == "task_4"
    assert d.tasks[3].upstream_task_ids == {"task_3"}
    assert d.tasks[4].task_id == "task_5"
    assert d.tasks[4].upstream_task_ids == {"task_4"}
    assert conf.dags["example_dag"].tasks["task_5"].model_dump()["show_return_value_in_logs"] is True


def test_create_dag_from_config_create_dag():
    d = create_dag("config", "factory")
    assert d.dag_id == "tests-setups-factory-test-factory"
    assert d.dag_id in globals()
    assert d.default_args["owner"] == "test"


def test_serialize_with_airflow_extras():
    conf = load_config("config", "factory")
    print(conf.model_dump_json(serialize_as_any=True))
    assert '"operator":"airflow.operators.bash.BashOperator"' in conf.model_dump_json()
