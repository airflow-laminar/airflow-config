__all__ = ("ConfigNotFoundError",)


class ConfigNotFoundError(RuntimeError):
    def __init__(self, config_dir, dagfile):
        super().__init__(f"Could not find `{config_dir}` directory on or above DAG: {dagfile}")
