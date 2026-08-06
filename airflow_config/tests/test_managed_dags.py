from airflow_pydantic import BalancerConfiguration, Host
from hydra.utils import instantiate
from omegaconf import OmegaConf

from airflow_config import Configuration


def test_generate_pool_manager_with_normal_dag_configuration(tmp_path):
    config = Configuration(
        dags={},
        extensions={
            "balancer": BalancerConfiguration(
                hosts=[Host(name="worker", size=4)],
                pool_manager={
                    "dag": {
                        "dag_id": "custom_pool_manager",
                        "schedule": "0 * * * *",
                        "tags": ["platform"],
                        "max_active_runs": 2,
                    },
                    "task": {"queue": "system", "retries": 5},
                },
            )
        },
    )

    config.generate(tmp_path)

    runtime = (tmp_path / "_airflow_laminar_pool_runtime.py").read_text()
    controller = (tmp_path / "custom_pool_manager.py").read_text()
    assert "airflow_pydantic" not in runtime
    assert "airflow_pydantic" not in controller
    assert 'dag_id="custom_pool_manager"' in controller
    assert 'schedule="0 * * * *"' in controller
    assert 'tags=["platform"]' in controller
    assert "max_active_runs=2" in controller
    assert 'queue="system"' in controller
    assert "retries=5" in controller
    assert '"name": "worker"' in controller


def test_generate_pool_manager_in_memory(tmp_path):
    config = Configuration(
        dags={},
        extensions={
            "balancer": BalancerConfiguration(
                hosts=[Host(name="worker", size=4)],
                pool_manager={"dag": {"dag_id": "in_memory_pool_manager"}},
            )
        },
    )

    try:
        config.generate_in_mem(tmp_path, placeholder_dag_id="pool_manager_placeholder")
        manager = globals()["in_memory_pool_manager"]

        assert manager.dag_id == "in_memory_pool_manager"
        assert manager.get_task("reconcile_pools").pool == "default_pool"
    finally:
        globals().pop("in_memory_pool_manager", None)
        globals().pop("pool_manager_placeholder", None)


def test_pool_manager_accepts_airflow_config_yaml_shape(tmp_path):
    config = instantiate(
        OmegaConf.create(
            {
                "_target_": "airflow_config.Configuration",
                "dags": {},
                "extensions": {
                    "balancer": {
                        "_target_": "airflow_pydantic.BalancerConfiguration",
                        "hosts": [{"name": "worker", "size": 4}],
                        "pool_manager": {
                            "dag": {"schedule": "0 2 * * *", "tags": ["platform"]},
                            "task": {"queue": "system"},
                        },
                    }
                },
            }
        )
    )

    config.generate(tmp_path)

    controller = (tmp_path / "airflow_laminar_pool_manager.py").read_text()
    assert 'schedule="0 2 * * *"' in controller
    assert 'tags=["platform"]' in controller
    assert 'queue="system"' in controller
