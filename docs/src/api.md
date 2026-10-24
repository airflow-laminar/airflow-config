# API reference

This reference is generated from public signatures and docstrings.

## Configuration

`Configuration.default_operator_args` is a list of mappings. Each mapping contains
an `operator` import path or class followed by default task arguments. The selector
matches task model instances or subclasses of an installed Airflow operator class.
Later matching entries override earlier entries. Explicit task values, including
`None`, override these defaults. Values are validated against the task model and
copied for each task. The rules apply to tasks in `Configuration.dags`.

Operator defaults become task arguments, taking precedence over the DAG's
`default_args` and global `default_task_args` during rendering and instantiation.

```{eval-rst}
.. automodule:: airflow_config.configuration.base
   :members:
   :undoc-members:
```

## DAG creation

```{eval-rst}
.. automodule:: airflow_config.dag
   :members:
   :undoc-members:
```

## Utilities

### Configuration testing

`airflow_config.testing` provides database-free assertions over stored model
definitions. DAG and task IDs refer to mapping keys. Disabled definitions are
included; DAGs produced by extensions are outside these assertions.

- `assert_dag_ids(config, expected)` checks the exact set of configuration DAG keys.
- `assert_task_ids(dag, expected)` checks the exact set of task keys in a DAG model.
- `assert_task_type(dag, task_id, expected)` accepts a task model class or an
  installed Airflow operator base class. Subclasses match. A missing task reports
  the available keys; a type mismatch reports the actual model and operator.

ID mismatches raise `AssertionError` with missing and unexpected keys. These
assertions inspect definitions and do not execute tasks or resolve connections.

```{eval-rst}
.. automodule:: airflow_config.testing
   :members:
```

```{eval-rst}
.. automodule:: airflow_config.utils
   :members:
   :undoc-members:
```

## Exceptions

```{eval-rst}
.. automodule:: airflow_config.exceptions
   :members:
   :undoc-members:
```

## Viewer functions

```{eval-rst}
.. automodule:: airflow_config.ui.functions
   :members:
   :undoc-members:
```
