import pytest
from airflow_balancer.testing import pools
from airflow_pydantic.utils import _airflow_3

from airflow_config import load_config


def test_config_and_options():
    with pools():
        conf = load_config("config", "complex")

        assert str(conf.model_dump_json(exclude_unset=True, indent=2, serialize_as_any=True))


def test_config_null_schedule():
    with pools():
        conf = load_config("config", "complex")

        assert "none-schedule" in conf.dags
        assert conf.dags["none-schedule"].schedule is None


def test_none_schedule_instantiation():
    try:
        from airflow.timetables.simple import NullTimetable
    except ImportError:
        pytest.skip("Airflow is not installed, skipping timetable tests")

    with pools():
        conf = load_config("config", "complex")

        assert "none-schedule" in conf.dags
        assert conf.dags["none-schedule"].schedule is None

        inst = conf.dags["none-schedule"].instantiate()
        if _airflow_3() or not hasattr(inst, "schedule_interval"):
            assert inst.schedule is None
        else:
            assert inst.schedule_interval is None
        assert isinstance(inst.timetable, NullTimetable)
