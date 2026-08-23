import "@andypf/json-viewer";

declare global {
  interface Window {
    __AIRFLOW_CONFIG__: string;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const root = document.getElementById("airflow-config-root");
  if (!root) {
    return;
  }

  const raw_config = window.__AIRFLOW_CONFIG__;
  const json_viewer = document.createElement("andypf-json-viewer");
  json_viewer.setAttribute("data", raw_config);
  json_viewer.setAttribute("indent", "8");
  json_viewer.setAttribute("expanded", "true");
  json_viewer.setAttribute("expand-icon-type", "square");
  json_viewer.setAttribute("show-toolbar", "true");
  json_viewer.setAttribute("show-data-types", "false");
  root.appendChild(json_viewer);
});
