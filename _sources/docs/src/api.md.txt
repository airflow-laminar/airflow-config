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
