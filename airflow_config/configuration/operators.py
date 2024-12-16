from typing import Dict, List, Optional

from pydantic import ConfigDict, Field

from .airflow import _TaskSpecificArgs
from .utils import CallablePath

__all__ = (
    "PythonOperatorArgs",
    "BashOperatorArgs",
    "SSHOperatorArgs",
)


class PythonOperatorArgs(_TaskSpecificArgs):
    # task shared
    # python operator args
    # https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/python/index.html#airflow.operators.python.PythonOperator
    python_callable: Optional[CallablePath] = Field(default=None, description="python_callable")
    op_args: Optional[List[object]] = Field(
        default=None, description="a list of positional arguments that will get unpacked when calling your callable"
    )
    op_kwargs: Optional[Dict[str, object]] = Field(
        default=None, description="a dictionary of keyword arguments that will get unpacked in your function"
    )
    templates_dict: Optional[Dict[str, object]] = Field(
        default=None,
        description="a dictionary where the values are templates that will get templated by the Airflow engine sometime between __init__ and execute takes place and are made available in your callable’s context after the template has been applied. (templated)",
    )
    templates_exts: Optional[List[str]] = Field(
        default=None, description="a list of file extensions to resolve while processing templated fields, for examples ['.sql', '.hql']"
    )
    show_return_value_in_logs: Optional[bool] = Field(
        default=None,
        description="a bool value whether to show return_value logs. Defaults to True, which allows return value log output. It can be set to False",
    )


class BashOperatorArgs(_TaskSpecificArgs):
    # bash operator args
    # https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/operators/bash/index.html#airflow.operators.bash.BashOperator
    bash_command: Optional[str] = Field(default=None, description="bash_command")
    env: Optional[Dict[str, str]] = Field(default=None)
    append_env: Optional[bool] = Field(default=False)
    output_encoding: Optional[str] = Field(default="utf-8")
    skip_exit_code: Optional[bool] = Field(default=None)
    skip_on_exit_code: Optional[int] = Field(default=99)
    cwd: Optional[str] = Field(default=None)
    output_processor: Optional[CallablePath] = None


class SSHOperatorArgs(_TaskSpecificArgs):
    # ssh operator args
    ...

    # generic extras
    model_config = ConfigDict(extra="allow")
