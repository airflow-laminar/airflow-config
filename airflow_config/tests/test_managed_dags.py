from typing import Any
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel, Field

from airflow_config import Configuration


class ManagedDagExtension(BaseModel):
    files: dict[str, str] = Field(default_factory=dict)
    dags: list[Any] = Field(default_factory=list)

    def generated_files(self):
        return self.files

    def managed_dags(self):
        return self.dags


class ManagedDag:
    def __init__(self, dag_id, instance):
        self.dag_id = dag_id
        self.instance = instance

    def instantiate(self):
        return self.instance


def test_generate_writes_extension_managed_files(tmp_path):
    config = Configuration(
        dags={},
        extensions={
            "test": ManagedDagExtension(
                files={"managed_runtime.py": "RUNTIME = True\n", "managed_dag.py": "DAG = True\n"},
            )
        },
    )

    config.generate(tmp_path)

    assert (tmp_path / "managed_runtime.py").read_text() == "RUNTIME = True\n"
    assert (tmp_path / "managed_dag.py").read_text() == "DAG = True\n"


def test_generate_in_memory_adds_extension_managed_dag(tmp_path, has_airflow):
    manager = MagicMock()
    config = Configuration(
        dags={},
        extensions={"test": ManagedDagExtension(dags=[ManagedDag("managed_dag", manager)])},
    )

    try:
        config.generate_in_mem(tmp_path, placeholder_dag_id="managed_dag_placeholder")

        assert globals()["managed_dag"] is manager
        assert manager.fileloc == str(tmp_path / "managed_dag.py")
    finally:
        globals().pop("managed_dag", None)
        globals().pop("managed_dag_placeholder", None)


def test_generate_rejects_conflicting_extension_files(tmp_path):
    config = Configuration(
        dags={},
        extensions={
            "first": ManagedDagExtension(files={"managed.py": "FIRST = True\n"}),
            "second": ManagedDagExtension(files={"managed.py": "SECOND = True\n"}),
        },
    )

    with pytest.raises(ValueError, match="Extensions generated conflicting files named managed.py"):
        config.generate(tmp_path)
