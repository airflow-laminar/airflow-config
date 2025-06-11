from airflow_config import load_config


def get_ssh_hook_from_config():
    conf = load_config("config", "self_reference")
    return conf.extensions["balancer"].select_host(name="server2").hook()
