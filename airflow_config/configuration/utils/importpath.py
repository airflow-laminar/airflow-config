from importlib import import_module
from typing import Annotated

from pydantic import BeforeValidator


def get_import_path(path: str) -> type:
    if isinstance(path, type):
        return path
    if not isinstance(path, str):
        raise TypeError(path)
    module, callable = path.rsplit(".", 1)
    return getattr(import_module(module), callable)


ImportPath = Annotated[type, BeforeValidator(get_import_path)]
CallablePath = Annotated[object, BeforeValidator(get_import_path)]
