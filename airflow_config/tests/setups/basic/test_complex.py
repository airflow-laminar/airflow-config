from unittest.mock import patch

from airflow.timetables.simple import NullTimetable

from airflow_config import load_config


def test_config_and_options():
    with patch("airflow_balancer.config.balancer.Pool"):
        conf = load_config("config", "complex")

        assert str(conf.model_dump_json(exclude_unset=True, indent=2, serialize_as_any=True))


def test_config_null_schedule():
    with patch("airflow_balancer.config.balancer.Pool"):
        conf = load_config("config", "complex")

        assert "none-schedule" in conf.dags
        assert conf.dags["none-schedule"].schedule is None

        inst = conf.dags["none-schedule"].instantiate()
        assert inst.schedule_interval is None
        assert isinstance(inst.timetable, NullTimetable)
