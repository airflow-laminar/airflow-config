try:
    from airflow_priority.models import *
except ImportError:
    pass

try:
    from airflow_balancer.config import *
except ImportError:
    pass

from airflow_pydantic import *

# NOTE: put this here to avoid airflow_balancer.load_config conflicting with this load_config
from .base import *
