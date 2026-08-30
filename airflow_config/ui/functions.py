from __future__ import annotations

import os
from logging import getLogger
from pathlib import Path

from hydra.errors import InstantiationException

from airflow_config import ConfigNotFoundError, load_config

__all__ = (
    "get_configs_from_yaml",
    "get_dags_folder",
    "get_yaml_files",
)

log = getLogger(__name__)


def get_dags_folder() -> str | None:
    """Resolve the dags folder from the environment, falling back to the Airflow config.

    Returns None when Airflow is unavailable, so the standalone viewer can supply its own default.
    """
    dags_folder = os.environ.get("AIRFLOW__CORE__DAGS_FOLDER")
    if dags_folder:
        return dags_folder
    try:
        from airflow.configuration import conf

        return (conf.getsection("core") or {}).get("dags_folder")
    except Exception:
        log.debug("Could not read dags_folder from the Airflow configuration", exc_info=True)
        return None


def _read_text(path: Path) -> str:
    """Read a yaml file, skipping any that cannot be decoded or accessed."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        log.debug(f"Skipping unreadable file {path}", exc_info=True)
        return ""


def get_configs_from_yaml(yaml: str, overrides: list[str]) -> list[str]:
    # Process the yaml
    yaml_file = Path(yaml).resolve()
    try:
        cfg = load_config(str(yaml_file.parent.name), yaml_file.name, overrides=overrides, basepath=str(yaml_file))
    except (ConfigNotFoundError, InstantiationException):
        log.exception(f"Error loading YAML file {yaml}")
        return ""
    if not cfg:
        return ""
    return str(cfg.model_dump_json(exclude_unset=True, indent=2))


def get_yaml_files(dags_folder: str) -> list[Path]:
    # Look for yamls inside the dags folder
    yamls = []
    base_path = Path(dags_folder)

    # Look if the file directly instantiates a BalancerConfiguration
    for path in base_path.glob("**/*.yaml"):
        if path.is_file() and "_target_: airflow_config.Configuration" in _read_text(path):
            yamls.append(path)
    len_yamls = len(yamls)
    len_yamls_last = 0
    # If we have yamls, look for any that reference them
    while len_yamls != len_yamls_last:
        for path in base_path.glob("**/*.yaml"):
            if path.is_file() and path not in yamls:
                # Check and see if this references any existing yamls
                for yaml in yamls:
                    if path.parent == yaml.parent and f"{yaml.stem}@" in _read_text(path):
                        yamls.append(path)
                        break
        len_yamls_last = len_yamls
        len_yamls = len(yamls)
    return sorted(yamls)
