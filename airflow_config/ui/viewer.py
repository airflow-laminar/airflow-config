from __future__ import annotations

import os
from pathlib import Path

from airflow.configuration import conf
from airflow.plugins_manager import AirflowPlugin
from airflow.security import permissions
from airflow.www.auth import has_access
from flask import Blueprint, request
from flask_appbuilder import BaseView, expose

from airflow_config import load_config

__all__ = (
    "AirflowConfigViewerPluginView",
    "AirflowConfigViewerPlugin",
)


class AirflowConfigViewerPluginView(BaseView):
    """Creating a Flask-AppBuilder View"""

    default_view = "home"

    @expose("/")
    @has_access([(permissions.ACTION_CAN_READ, permissions.RESOURCE_WEBSITE)])
    def home(self):
        """Create default view"""
        yaml = request.args.get("yaml")
        overrides = (request.args.get("overrides") or "").split()

        if yaml:
            # Process the yaml, potentially with overrides
            yaml_file = Path(yaml).resolve()
            cfg = load_config(str(yaml_file.parent.name), yaml_file.name, overrides=overrides, basepath=str(yaml_file))
            if not cfg:
                return self.render_template("500.html", yaml=yaml)
            return self.render_template("yaml.html", config=str(cfg.model_dump_json(indent=2, serialize_as_any=True)))

        # Locate the dags folder
        dags_folder = os.environ.get("AIRFLOW__CORE__DAGS_FOLDER", conf.getsection("core").get("dags_folder"))
        if not dags_folder:
            return self.render_template("404.html")

        # Look for yamls inside the dags folder
        yamls = []
        base_path = Path(dags_folder)
        for path in base_path.glob("**/*.yaml"):
            if path.is_file():
                if "_target_: airflow_config.Configuration" in path.read_text():
                    yamls.append(path)
        return self.render_template("config.html", yamls=yamls)


# Instantiate a view
airflow_config_viewer_plugin_view = AirflowConfigViewerPluginView()

# Creating a flask blueprint
bp = Blueprint(
    "Airflow Config",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static",
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
