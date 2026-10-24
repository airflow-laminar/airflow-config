"""Assertions for configuration models without an Airflow database."""

from collections.abc import Collection

from airflow_pydantic import Dag

from .configuration import Configuration

__all__ = ("assert_dag_ids", "assert_task_ids", "assert_task_type")


def assert_dag_ids(config: Configuration, expected: Collection[str]) -> None:
    """Assert the exact set of DAG keys in a configuration."""
    actual, expected = set(config.dags), set(expected)
    assert actual == expected, f"DAG IDs differ: missing={sorted(expected - actual)}; unexpected={sorted(actual - expected)}"


def assert_task_ids(dag: Dag, expected: Collection[str]) -> None:
    """Assert the exact set of task keys in a DAG model."""
    actual, expected = set(dag.tasks or {}), set(expected)
    assert actual == expected, f"DAG {dag.dag_id!r} task IDs differ: missing={sorted(expected - actual)}; unexpected={sorted(actual - expected)}"


def assert_task_type(dag: Dag, task_id: str, expected: type) -> None:
    """Assert a task model type or an installed Airflow operator base class."""
    tasks = dag.tasks or {}
    assert task_id in tasks, f"Task {task_id!r} missing from DAG {dag.dag_id!r}; available={sorted(tasks)}"
    task = tasks[task_id]
    assert isinstance(task, expected) or issubclass(task.operator, expected), (
        f"DAG {dag.dag_id!r} task {task_id!r} has model {type(task).__name__} and operator {task.operator.__name__}; expected {expected.__name__}"
    )
