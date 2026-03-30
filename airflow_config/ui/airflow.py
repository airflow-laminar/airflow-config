from __future__ import annotations

import logging
import os

from airflow.plugins_manager import AirflowPlugin

__all__ = (
    "AirflowConfigViewerPluginView",
    "AirflowConfigViewerPlugin",
)

_log = logging.getLogger(__name__)

try:
    from airflow.configuration import conf
    from airflow.security import permissions
    from airflow.www.auth import has_access
    from flask import Blueprint, request
    from flask_appbuilder import BaseView, expose

    from .functions import get_configs_from_yaml, get_yaml_files

    class AirflowConfigViewerPluginView(BaseView):
        """Creating a Flask-AppBuilder View"""

        default_view = "home"

        @expose("/yaml")
        @has_access([(permissions.ACTION_CAN_READ, permissions.RESOURCE_WEBSITE)])
        def yaml(self):
            yaml = request.args.get("yaml")
            overrides = (request.args.get("overrides") or "").split()

            if not yaml:
                return self.render_template("airflow_config/500.html", yaml="- yaml file not specified")
            cfg = get_configs_from_yaml(yaml, overrides=overrides)
            if not cfg:
                return self.render_template("airflow_config/500.html", yaml=yaml)
            return self.render_template("airflow_config/yaml.html", config=cfg)

        @expose("/")
        @has_access([(permissions.ACTION_CAN_READ, permissions.RESOURCE_WEBSITE)])
        def home(self):
            """Create default view"""
            # Locate the dags folder
            dags_folder = os.environ.get("AIRFLOW__CORE__DAGS_FOLDER", conf.getsection("core").get("dags_folder"))
            if not dags_folder:
                return self.render_template("airflow_config/404.html")
            yamls = get_yaml_files(dags_folder=dags_folder)
            return self.render_template("airflow_config/home.html", yamls=yamls)

    # Instantiate a view
    airflow_config_viewer_plugin_view = AirflowConfigViewerPluginView()

    # Creating a flask blueprint
    bp = Blueprint(
        "Airflow Config",
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/static/airflow-config",
    )

    # Create menu items
    docs_link_subitem = {
        "label": "Airflow Config Docs",
        "name": "Airflow Config Docs",
        "href": "https://airflow-laminar.github.io/airflow-config/",
        "category": "Docs",
    }

    view_subitem = {"label": "Airflow Config Viewer", "category": "Laminar", "name": "Laminar", "view": airflow_config_viewer_plugin_view}

    class AirflowConfigViewerPlugin(AirflowPlugin):
        """Defining the plugin class"""

        name = "Airflow Config"
        flask_blueprints = [bp]
        appbuilder_views = [view_subitem]
        appbuilder_menu_items = [docs_link_subitem]

except ImportError:
    _log.info("airflow-config UI plugin disabled: airflow.www / Flask-AppBuilder not available (Airflow 3+)")

    class AirflowConfigViewerPluginView:  # type: ignore[no-redef]
        pass

    class AirflowConfigViewerPlugin(AirflowPlugin):  # type: ignore[no-redef]
        """No-op plugin when Flask-AppBuilder UI is not available."""

        name = "Airflow Config"
