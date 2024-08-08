from helpers import get_calling_dag


def test_get_calling_dag_path():
    assert get_calling_dag(0).endswith("airflow_config/utils.py")
    assert get_calling_dag(1).endswith("helpers.py")
    assert get_calling_dag(2).endswith("test_utils.py")
