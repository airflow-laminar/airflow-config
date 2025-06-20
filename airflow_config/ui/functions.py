from __future__ import annotations

from logging import getLogger
from pathlib import Path

from hydra.errors import InstantiationException

from airflow_config import ConfigNotFoundError, load_config

__all__ = (
    "get_configs_from_yaml",
    "get_yaml_files",
)

log = getLogger(__name__)


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
    return str(cfg.model_dump_json(exclude_unset=True, indent=2, serialize_as_any=True))


def get_yaml_files(dags_folder: str) -> list[Path]:
    # Look for yamls inside the dags folder
    yamls = []
    base_path = Path(dags_folder)

    # Look if the file directly instantiates a BalancerConfiguration
    for path in base_path.glob("**/*.yaml"):
        if path.is_file():
            if "_target_: airflow_config.Configuration" in path.read_text():
                yamls.append(path)
    len_yamls = len(yamls)
    len_yamls_last = 0
    # If we have yamls, look for any that reference them
    while len_yamls != len_yamls_last:
        for path in base_path.glob("**/*.yaml"):
            if path.is_file() and path not in yamls:
                # Check and see if this references any existing yamls
                for yaml in yamls:
                    if path.parent == yaml.parent and f"{yaml.stem}@" in path.read_text():
                        yamls.append(path)
                        break
        len_yamls_last = len_yamls
        len_yamls = len(yamls)
    return sorted(yamls)
