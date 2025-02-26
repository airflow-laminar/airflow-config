from __future__ import annotations

from flask import Blueprint
from flask_appbuilder import BaseView, expose

from airflow.plugins_manager import AirflowPlugin
from airflow.security import permissions
from airflow.security import permissions
from airflow.www.auth import has_access


class AirflowConfigViewerPluginView(BaseView):
    """Creating a Flask-AppBuilder View"""

    default_view = "test"

    @expose("/")
    @has_access([(permissions.ACTION_CAN_READ, permissions.RESOURCE_WEBSITE)])
    def test(self):
        """Create default view"""
        return self.render_template("test.html", content="Hello world")

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

view_subitem = {
    "label": "Config",
    "category": "Laminar",
    "name": "Laminar",
    "view": airflow_config_viewer_plugin_view
}


class AirflowConfigViewerPlugin(AirflowPlugin):
    """Defining the plugin class"""

    name = "Airflow Config"
    flask_blueprints = [bp]
    appbuilder_views = [view_subitem]
    appbuilder_menu_items = [docs_link_subitem]
