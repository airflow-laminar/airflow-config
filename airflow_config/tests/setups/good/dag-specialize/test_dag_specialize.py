from datetime import datetime, timedelta

from airflow.timetables.interval import DeltaDataIntervalTimetable

from airflow_config import DAG, create_dag, load_config


def test_config_and_options():
    conf = load_config("config", "test")
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
    conf = load_config("config", "test")
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

    d = DAG(dag_id="example_dag2", config=conf)
    assert d.default_args["owner"] == "custom_owner2"
    assert d.default_args["email"] == ["myemail@myemail.com"]
    assert d.schedule_interval == "0 4 * * *"


def test_create_dag_from_config_create_dag():
    d = create_dag("config", "test")
    assert d.dag_id == "tests-setups-good-dag-specialize-test-dag-specialize"
    assert d.dag_id in globals()
    assert d.default_args["owner"] == "test"
