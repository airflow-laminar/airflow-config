import "@andypf/json-viewer";
import "@andypf/json-viewer";

document.addEventListener("DOMContentLoaded", () => {
  const root: HTMLDivElement = document.getElementById("airflow-config-root");
  const raw_config: string = window.__AIRFLOW_CONFIG__;
  const json_viewer = document.createElement("andypf-json-viewer");
  json_viewer.setAttribute("data", raw_config);
  json_viewer.setAttribute("indent", "8");
  json_viewer.setAttribute("expanded", "true");
  json_viewer.setAttribute("expand-icon-type", "square");
  json_viewer.setAttribute("show-toolbar", "true");
  json_viewer.setAttribute("show-data-types", "false");
  root.appendChild(json_viewer);
});
