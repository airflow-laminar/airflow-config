from datetime import datetime, timedelta
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field

from .utils import RelativeDelta

__all__ = (
    "DefaultArgs",
    "DAGArgs",
    "DagConfiguration",
)

# TODO
# from airflow.models.dag import ScheduleArg
# ScheduleArg = Union[ArgNotSet, ScheduleInterval, Timetable, BaseDatasetEventInput, Collection["Dataset"]]
# ScheduleInterval = Union[None, str, timedelta, relativedelta]

ScheduleArg = Union[Literal["NOTSET"], None, str, timedelta, RelativeDelta]


class DefaultArgs(BaseModel):
    # Operator Args
    # https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/baseoperator/index.html#airflow.models.baseoperator.BaseOperator
    owner: str = Field(
        default="airflow",
        description="the owner of the task. Using a meaningful description (e.g. user/person/team/role name) to clarify ownership is recommended.",
    )
    email: List[str] = Field(default_factory=list, description="the 'to' email address(es) used in email alerts")
    email_on_failure: bool = Field(default=False, description="Indicates whether email alerts should be sent when a task failed")
    email_on_retry: bool = Field(default=False, description="Indicates whether email alerts should be sent when a task is retried")
    retries: int = Field(default=0, description="the number of retries that should be performed before failing the task")
    retry_delay: timedelta = Field(default=timedelta(minutes=5), description="delay between retries")
    # retry_exponential_backoff: bool = Field(
    #     default=False,
    #     description="allow progressively longer waits between retries by using exponential backoff algorithm on retry delay (delay will be converted into seconds)",
    # )
    # max_retry_delay: Optional[timedelta] = Field(default=None, description="maximum delay interval between retries")
    depends_on_past: bool = Field(
        default=False,
        description="when set to true, task instances will run sequentially and only if the previous instance has succeeded or has been skipped. The task instance for the start_date is allowed to run.",
    )
    # wait_for_past_depends_before_skipping: bool = Field(
    #     default=False,
    #     description="when set to true, if the task instance should be marked as skipped, and depends_on_past is true, the ti will stay on None state waiting the task of the previous run",
    # )
    # wait_for_downstream: bool = Field(
    #     default=False,
    #     description="when set to true, an instance of task X will wait for tasks immediately downstream of the previous instance of task X to finish successfully or be skipped before it runs. This is useful if the different instances of a task X alter the same asset, and this asset is used by tasks downstream of task X. Note that depends_on_past is forced to True wherever wait_for_downstream is used. Also note that only tasks immediately downstream of the previous task instance are waited for; the statuses of any tasks further downstream are ignored.",
    # )
    # priority_weight: int = Field(
    #     default=1,
    #     description="priority weight of this task against other task. This allows the executor to trigger higher priority tasks before others when things get backed up. Set priority_weight as a higher number for more important tasks.",
    # )
    # weight_rule: str = Field(
    #     default="downstream",
    #     description="weighting method used for the effective total priority weight of the task. Options are: { downstream | upstream | absolute } default is downstream When set to downstream the effective weight of the task is the aggregate sum of all downstream descendants. As a result, upstream tasks will have higher weight and will be scheduled more aggressively when using positive weight values. This is useful when you have multiple dag run instances and desire to have all upstream tasks to complete for all runs before each dag can continue processing downstream tasks. When set to upstream the effective weight is the aggregate sum of all upstream ancestors. This is the opposite where downstream tasks have higher weight and will be scheduled more aggressively when using positive weight values. This is useful when you have multiple dag run instances and prefer to have each dag complete before starting upstream tasks of other dags. When set to absolute, the effective weight is the exact priority_weight specified without additional weighting. You may want to do this when you know exactly what priority weight each task should have. Additionally, when set to absolute, there is bonus effect of significantly speeding up the task creation process as for very large DAGs. Options can be set as string or using the constants defined in the static class airflow.utils.WeightRule",
    # )
    # queue: str = Field(
    #     default="",
    #     description="which queue to target when running this job. Not all executors implement queue management, the CeleryExecutor does support targeting specific queues.",
    # )
    # pool: Optional[str] = Field(
    #     default=None,
    #     description="the slot pool this task should run in, slot pools are a way to limit concurrency for certain tasks",
    # )
    # pool_slots: int = Field(default=1, description="the number of pool slots this task should use (>= 1) Values less than 1 are not allowed")
    # sla: Optional[datetime] = Field(
    #     default=None,
    #     description="time by which the job is expected to succeed. Note that this represents the timedelta after the period is closed. For example if you set an SLA of 1 hour, the scheduler would send an email soon after 1:00AM on the 2016-01-02 if the 2016-01-01 instance has not succeeded yet. The scheduler pays special attention for jobs with an SLA and sends alert emails for SLA misses. SLA misses are also recorded in the database for future reference. All tasks that share the same SLA time get bundled in a single email, sent soon after that time. SLA notification are sent once and only once for each task instance.",
    # )
    # execution_timeout: Optional[timedelta] = Field(
    #     default=None,
    #     description="max time allowed for the execution of this task instance, if it goes beyond it will raise and fail.",
    # )
    # trigger_rule: str = Field(
    #     default="all_success",
    #     description="defines the rule by which dependencies are applied for the task to get triggered. Options are: { all_success | all_failed | all_done | all_skipped | one_success | one_done | one_failed | none_failed | none_failed_min_one_success | none_skipped | always} default is all_success. Options can be set as string or using the constants defined in the static class airflow.utils.TriggerRule",
    # )
    # run_as_user: Optional[str] = Field(default=None, description="unix username to impersonate while running the task")
    # max_active_tis_per_dag: Optional[int] = Field(
    #     default=None, description="When set, a task will be able to limit the concurrent runs across execution_dates."
    # )
    # max_active_tis_per_dagrun: Optional[int] = Field(
    #     default=None, description="When set, a task will be able to limit the concurrent task instances per DAG run."
    # )


class DAGArgs(BaseModel):
    # DAG args
    # https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/dag/index.html#airflow.models.dag.DAG
    start_date: datetime = Field(default_factory=datetime.today, description="The timestamp from which the scheduler will attempt to backfill")
    end_date: Optional[datetime] = Field(default=None, description="A date beyond which your DAG won’t run, leave to None for open-ended scheduling")
    # max_active_tasks: int = Field(default=16, description="the number of task instances allowed to run concurrently")
    # max_active_tasks: int = Field(
    #     default=16,
    #     description="maximum number of active DAG runs, beyond this number of DAG runs in a running state, the scheduler won’t create new active DAG runs",
    # )
    # default_view: str = Field(
    #     default="grid",
    #     description="Specify DAG default view (grid, graph, duration, gantt, landing_times), default grid",
    # )
    # orientation: str = Field(default="LR", description="Specify DAG orientation in graph view (LR, TB, RL, BT), default LR")
    catchup: bool = Field(default=False, description="Perform scheduler catchup (or only run latest)? Defaults to False")
    # is_paused_upon_creation: bool = Field(
    #     default=True,
    #     description="Specifies if the dag is paused when created for the first time. If the dag exists already, this flag will be ignored.",
    # )
    # DEFINED PER-DAG:
    # dag_id (str) – The id of the DAG; must consist exclusively of alphanumeric characters, dashes, dots and underscores (all ASCII)
    # description (str | None) – The description for the DAG to e.g. be shown on the webserver
    # schedule (ScheduleArg) – Defines the rules according to which DAG runs are scheduled. Can accept cron string, timedelta object, Timetable, or list of Dataset objects. If this is not provided, the DAG will be set to the default schedule timedelta(days=1). See also Customizing DAG Scheduling with Timetables.
    # TODO
    # template_searchpath: List[str] = Field(default_factory=list, description="This list of folders (non-relative) defines where jinja will look for your templates. Order matters. Note that jinja/airflow includes the path of your DAG file by default")
    # template_undefined (type[jinja2.StrictUndefined]) – Template undefined type.
    # user_defined_macros (dict | None) – a dictionary of macros that will be exposed in your jinja templates. For example, passing dict(foo='bar') to this argument allows you to {{ foo }} in all jinja templates related to this DAG. Note that you can pass any type of object here.
    # user_defined_filters (dict | None) – a dictionary of filters that will be exposed in your jinja templates. For example, passing dict(hello=lambda name: 'Hello %s' % name) to this argument allows you to {{ 'world' | hello }} in all jinja templates related to this DAG.
    # default_args (dict | None) – A dictionary of default parameters to be used as constructor keyword parameters when initialising operators. Note that operators have the same hook, and precede those defined here, meaning that if your dict contains ‘depends_on_past’: True here and ‘depends_on_past’: False in the operator’s call default_args, the actual value will be False.
    # params (collections.abc.MutableMapping | None) – a dictionary of DAG level parameters that are made accessible in templates, namespaced under params. These params can be overridden at the task level.
    # dagrun_timeout (datetime.timedelta | None) – specify how long a DagRun should be up before timing out / failing, so that new DagRuns can be created.
    # sla_miss_callback (None | SLAMissCallback | list[SLAMissCallback]) – specify a function or list of functions to call when reporting SLA timeouts. See sla_miss_callback for more information about the function signature and parameters that are passed to the callback.
    # on_failure_callback (None | DagStateChangeCallback | list[DagStateChangeCallback]) – A function or list of functions to be called when a DagRun of this dag fails. A context dictionary is passed as a single parameter to this function.
    # on_success_callback (None | DagStateChangeCallback | list[DagStateChangeCallback]) – Much like the on_failure_callback except that it is executed when the dag succeeds.
    # access_control (dict | None) – Specify optional DAG-level actions, e.g., “{‘role1’: {‘can_read’}, ‘role2’: {‘can_read’, ‘can_edit’, ‘can_delete’}}”
    # jinja_environment_kwargs (dict | None) – additional configuration options to be passed to Jinja Environment for template rendering

    # DEFINED PER-OPERATOR
    # task_id (str) – a unique, meaningful id for the task
    # start_date (datetime.datetime | None) – The start_date for the task, determines the execution_date for the first task instance. The best practice is to have the start_date rounded to your DAG’s schedule_interval. Daily jobs have their start_date some day at 00:00:00, hourly jobs have their start_date at 00:00 of a specific hour. Note that Airflow simply looks at the latest execution_date and adds the schedule_interval to determine the next execution_date. It is also very important to note that different tasks’ dependencies need to line up in time. If task A depends on task B and their start_date are offset in a way that their execution_date don’t line up, A’s dependencies will never be met. If you are looking to delay a task, for example running a daily task at 2AM, look into the TimeSensor and TimeDeltaSensor. We advise against using dynamic start_date and recommend using fixed ones. Read the FAQ entry about start_date for more information.
    # end_date (datetime.datetime | None) – if specified, the scheduler won’t go beyond this date
    # dag (airflow.models.dag.DAG | None) – a reference to the dag the task is attached to (if any)
    # on_failure_callback (None | airflow.models.abstractoperator.TaskStateChangeCallback | list[airflow.models.abstractoperator.TaskStateChangeCallback]) – a function or list of functions to be called when a task instance of this task fails. a context dictionary is passed as a single parameter to this function. Context contains references to related objects to the task instance and is documented under the macros section of the API.
    # on_execute_callback (None | airflow.models.abstractoperator.TaskStateChangeCallback | list[airflow.models.abstractoperator.TaskStateChangeCallback]) – much like the on_failure_callback except that it is executed right before the task is executed.
    # on_retry_callback (None | airflow.models.abstractoperator.TaskStateChangeCallback | list[airflow.models.abstractoperator.TaskStateChangeCallback]) – much like the on_failure_callback except that it is executed when retries occur.
    # on_success_callback (None | airflow.models.abstractoperator.TaskStateChangeCallback | list[airflow.models.abstractoperator.TaskStateChangeCallback]) – much like the on_failure_callback except that it is executed when the task succeeds.
    # pre_execute (TaskPreExecuteHook | None) –
    # post_execute (TaskPostExecuteHook | None) –
    # resources (dict[str, Any] | None) – A map of resource parameter names (the argument names of the Resources constructor) to their values.
    # executor_config (dict | None) –

    # OTHER
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags to Inject onto DAGs by default")


class DagConfiguration(BaseModel):
    # DAG args
    # https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/dag/index.html#airflow.models.dag.DAG
    dag_id: str = Field(
        description="The id of the DAG; must consist exclusively of alphanumeric characters, dashes, dots and underscores (all ASCII)"
    )
    description: Optional[str] = Field(description="The description for the DAG to e.g. be shown on the webserver")
    schedule: ScheduleArg = Field(
        description="Defines the rules according to which DAG runs are scheduled. Can accept cron string, timedelta object, Timetable, or list of Dataset objects. If this is not provided, the DAG will be set to the default schedule timedelta(days=1). See also Customizing DAG Scheduling with Timetables."
    )
    # TODO
    # template_searchpath: List[str] = Field(default_factory=list, description="This list of folders (non-relative) defines where jinja will look for your templates. Order matters. Note that jinja/airflow includes the path of your DAG file by default")
    # template_undefined (type[jinja2.StrictUndefined]) – Template undefined type.
    # user_defined_macros (dict | None) – a dictionary of macros that will be exposed in your jinja templates. For example, passing dict(foo='bar') to this argument allows you to {{ foo }} in all jinja templates related to this DAG. Note that you can pass any type of object here.
    # user_defined_filters (dict | None) – a dictionary of filters that will be exposed in your jinja templates. For example, passing dict(hello=lambda name: 'Hello %s' % name) to this argument allows you to {{ 'world' | hello }} in all jinja templates related to this DAG.
    # default_args (dict | None) – A dictionary of default parameters to be used as constructor keyword parameters when initialising operators. Note that operators have the same hook, and precede those defined here, meaning that if your dict contains ‘depends_on_past’: True here and ‘depends_on_past’: False in the operator’s call default_args, the actual value will be False.
    # params (collections.abc.MutableMapping | None) – a dictionary of DAG level parameters that are made accessible in templates, namespaced under params. These params can be overridden at the task level.
    # dagrun_timeout (datetime.timedelta | None) – specify how long a DagRun should be up before timing out / failing, so that new DagRuns can be created.
    # sla_miss_callback (None | SLAMissCallback | list[SLAMissCallback]) – specify a function or list of functions to call when reporting SLA timeouts. See sla_miss_callback for more information about the function signature and parameters that are passed to the callback.
    # on_failure_callback (None | DagStateChangeCallback | list[DagStateChangeCallback]) – A function or list of functions to be called when a DagRun of this dag fails. A context dictionary is passed as a single parameter to this function.
    # on_success_callback (None | DagStateChangeCallback | list[DagStateChangeCallback]) – Much like the on_failure_callback except that it is executed when the dag succeeds.
    # access_control (dict | None) – Specify optional DAG-level actions, e.g., “{‘role1’: {‘can_read’}, ‘role2’: {‘can_read’, ‘can_edit’, ‘can_delete’}}”
    # jinja_environment_kwargs (dict | None) – additional configuration options to be passed to Jinja Environment for template rendering
