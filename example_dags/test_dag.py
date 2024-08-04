from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

from airflow_config import load_config

EMAIL = "t.paine154@gmail.com"
USERNAME = "timkpaine"

config = load_config()

# with DAG(
#     dag_id="test-dag",
#     default_args={
#         "depends_on_past": False,
#         "email": [EMAIL],
#         "email_on_failure": False,
#         "email_on_retry": False,
#         "retries": 0,
#     },
#     description="test that dag is working properly",
#     schedule=timedelta(minutes=1),
#     start_date=datetime(2024, 1, 1),
#     catchup=False,
#     tags=["utility", "test"],
# ):
#     BashOperator(
#         task_id="test-task",
#         bash_command="echo 'test'",
#     )
