__version__ = "1.10.7"

from .configuration import *

try:
    from .dag import DAG, create_dag, create_dags
except ImportError:
    # Allow airflow be removed
    pass
from .exceptions import *
from .utils import generate_dag_id
