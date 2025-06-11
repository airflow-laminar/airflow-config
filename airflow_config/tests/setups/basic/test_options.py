from datetime import datetime, timedelta

from airflow.timetables.interval import DeltaDataIntervalTimetable
from pytz import timezone

from airflow_config import DAG, create_dag, load_config


def test_config_and_options():
    conf = load_config("config", "options")
    assert conf.default_args.owner == "test"
    assert conf.default_args.email == ["myemail@myemail.com"]
    assert conf.default_args.email_on_failure is False
    assert conf.default_args.email_on_retry is False
    assert conf.default_args.retries == 0
    assert conf.default_args.depends_on_past is False
    assert conf.default_dag_args.start_date == datetime(2024, 1, 1, tzinfo=timezone("America/New_York"))
    assert conf.default_dag_args.catchup is False
    assert conf.default_dag_args.tags == ["utility", "test"]


def test_create_dag_from_config():
    conf = load_config("config", "options")
    d = DAG(dag_id="testdag", config=conf)
    assert d.default_args["owner"] == "test"
    assert d.default_args["email"] == ["myemail@myemail.com"]
    assert d.default_args["email_on_failure"] is False
    assert d.default_args["email_on_retry"] is False
    assert d.default_args["retries"] == 0
    assert d.default_args["depends_on_past"] is False

    assert d.schedule_interval == timedelta(hours=1, minutes=10)
    assert isinstance(d.timetable, DeltaDataIntervalTimetable)
    assert isinstance(d.timetable._delta, timedelta)
    assert d.timetable._delta.total_seconds() == 4200
    assert d.start_date.year == 2024
    assert d.start_date.month == 1
    assert d.start_date.day == 1
    assert d.catchup is False
    assert d.tags == ["utility", "test"]


def test_create_dag_from_config_create_dag():
    d = create_dag("config", "options")
    assert d.dag_id == "tests-setups-basic-test-options"
    assert d.dag_id in globals()
    assert d.default_args["owner"] == "test"
