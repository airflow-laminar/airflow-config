__all__ = ("ConfigNotFoundError",)


class ConfigNotFoundError(RuntimeError):
    def __init__(self, dagfile):
        super().__init__(f"Could not find `config` directory on or above DAG: {dagfile}")
