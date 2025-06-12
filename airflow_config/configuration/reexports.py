try:
    from airflow_priority.models import *  # noqa: F401, F403
except ImportError:
    pass

try:
    from airflow_balancer.config import *  # noqa: F401, F403
except ImportError:
    pass

from airflow_pydantic import (  # noqa: F401
    BashOperator,
    BashOperatorArgs,
    BranchPythonOperator,
    BranchPythonOperatorArgs,
    Dag,
    DagArgs,
    PythonOperator,
    PythonOperatorArgs,
    ShortCircuitOperator,
    ShortCircuitOperatorArgs,
    SSHOperatorArgs,
    Task,
    TaskArgs,
)

# NOTE: put this here to avoid airflow_balancer.load_config conflicting with this load_config
from .base import *  # noqa: F403
