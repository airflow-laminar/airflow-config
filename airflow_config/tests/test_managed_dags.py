import subprocess
import sys
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


class VersionedManagedDagExtension(ManagedDagExtension):
    version: int | None = None

    def generated_files(self, airflow_major_version=None):
        self.version = airflow_major_version
        return self.files


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

    config.generate(tmp_path, airflow_major_version=2)

    assert (tmp_path / "managed_runtime.py").read_text() == "RUNTIME = True\n"
    assert (tmp_path / "managed_dag.py").read_text() == "DAG = True\n"


@pytest.mark.parametrize("airflow_major_version", [2, 3])
def test_generate_formats_extension_managed_python_files(tmp_path, airflow_major_version):
    (tmp_path / "pyproject.toml").write_text('[tool.ruff.format]\nquote-style = "single"\n')
    config = Configuration(
        dags={},
        extensions={
            "test": ManagedDagExtension(
                files={
                    "managed.py": ('import os\nimport json\n\n\nwith open(os.devnull, "w") as stream:\n    json.dump({"value": "ready"}, stream)\n'),
                    "settings.json": '{"keep":  true}',
                }
            )
        },
    )

    config.generate(tmp_path, airflow_major_version=airflow_major_version)

    generated = tmp_path / "managed.py"
    for arguments in (("check", "--select", "I"), ("format", "--check")):
        result = subprocess.run(
            [sys.executable, "-m", "ruff", *arguments, str(generated)],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "settings.json").read_text() == '{"keep":  true}'
    modified = generated.stat().st_mtime_ns

    config.generate(tmp_path, airflow_major_version=airflow_major_version)

    assert generated.stat().st_mtime_ns == modified


def test_generate_without_ruff_keeps_extension_source(tmp_path, monkeypatch):
    monkeypatch.setattr(sys.modules["airflow_config.configuration.base"], "which", lambda executable: None)
    source = "VALUE=  1\n"
    config = Configuration(dags={}, extensions={"test": ManagedDagExtension(files={"managed.py": source})})

    config.generate(tmp_path, airflow_major_version=2)

    assert (tmp_path / "managed.py").read_text() == source


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
        config.generate(tmp_path, airflow_major_version=2)


def test_generate_passes_airflow_version_to_extensions(tmp_path):
    config = Configuration(dags={}, extensions={"test": VersionedManagedDagExtension()})

    config.generate(tmp_path, airflow_major_version=3)

    extension = config.extensions["test"]
    assert isinstance(extension, VersionedManagedDagExtension)
    assert extension.version == 3
