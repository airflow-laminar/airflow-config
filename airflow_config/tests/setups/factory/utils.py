from airflow_pydantic import BalancerConfiguration, Host

from airflow_config import load_config


def get_ssh_hook_from_config():
    conf = load_config("config", "self_reference")
    balancer = conf.extensions["balancer"]
    assert isinstance(balancer, BalancerConfiguration)
    host = balancer.select_host(name="server2")
    assert isinstance(host, Host)
    return host.hook()
