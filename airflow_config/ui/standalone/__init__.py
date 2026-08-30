import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..functions import get_configs_from_yaml, get_dags_folder, get_yaml_files

_static_path = Path(__file__).parent.parent.parent / "extension"
_static_airflow_path = Path(__file__).parent / "static"

__all__ = ("build_app", "main")


class AD(dict):
    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def _url_for(name: str, filename: str, **kwargs) -> str:
    if name == "Airflow Config.static":
        return f"static/{filename}"
    return ""


def build_app(*, dependencies: list[Any] | None = None) -> FastAPI:
    # Create a FastAPI instance
    app = FastAPI(dependencies=dependencies)

    # Serve static files
    app.mount(
        "/static",
        StaticFiles(directory=_static_path),
        name="static",
    )

    app.mount(
        "/static_airflow",
        StaticFiles(directory=_static_airflow_path),
        name="static_airflow",
    )

    # Templates
    templates = Jinja2Templates(
        directory=[
            Path(__file__).parent.parent / "templates" / "airflow_config",
            Path(__file__).parent / "templates",
        ],
    )

    # Mount top level routes
    # @app.get("/favicon.ico", include_in_schema=False, response_class=FileResponse)
    # async def readFavicon():
    #     return FileResponse(_static_path / "img" / "favicon.png")

    # Facsimile of Flask Appbuilder + Airflow templates
    fab_common_mock = {
        "request": AD(url_for=_url_for),
        "base_template": "airflow_mock.html",
        "appbuilder": AD(
            app_theme="",
            app_name="airflow-config",
            app_icon="",
            menu=AD(get_list=list, extra_classes=None),
            languages={},
            get_url_for_index="/",
            get_url_for_login="",
        ),
        "get_flashed_messages": lambda *args, **kwargs: [],
        "current_user": AD(is_anonymous=True),
        "session": {"locale": "en"},
        "_": lambda *args, **kwargs: "",
        "baselib": AD(get_nonce=lambda: ""),
    }

    @app.get("/")
    async def home(request: Request):
        dags_folder = get_dags_folder() or os.environ.get("AIRFLOW_HOME") or os.getcwd()
        yamls = get_yaml_files(dags_folder=dags_folder)
        if not yamls:
            return templates.TemplateResponse(request, "404.html", fab_common_mock)
        return templates.TemplateResponse(request, "home.html", {"yamls": yamls, **fab_common_mock})

    @app.get("/yaml")
    async def yaml(request: Request, yaml: str = "", overrides: list[str] | None = None):
        if not yaml:
            return templates.TemplateResponse(request, "500.html", {"yaml": "- yaml file not specified", **fab_common_mock})
        config = get_configs_from_yaml(yaml, overrides=overrides or [])
        return templates.TemplateResponse(request, "yaml.html", {"config": config, **fab_common_mock})

    return app


def main():
    from uvicorn import run

    # Build the FastAPI application
    app = build_app()

    # Run the application using Uvicorn
    run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
