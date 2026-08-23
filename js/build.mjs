import { bundle } from "./tools/bundle.mjs";
import { bundle_css } from "./tools/css.mjs";
import { node_modules_external } from "./tools/externals.mjs";

import fs from "fs";
import cpy from "cpy";
import path from "path";

const BUNDLES = [
  {
    entryPoints: ["src/ts/index.ts"],
    plugins: [node_modules_external()],
    outfile: "dist/esm/index.js",
  },
  {
    entryPoints: ["src/ts/index.ts"],
    outfile: "dist/cdn/index.js",
  },
];
const DIST_DIR = path.resolve("dist");

async function build() {
  fs.rmSync("dist", { recursive: true, force: true });
  fs.rmSync("../airflow_config/extension", {
    recursive: true,
    force: true,
  });

  // Bundle css
  await bundle_css();

  // Copy HTML
  await cpy("src/html/*", "dist/");

  // Copy images
<<<<<<< before updating
  fs.mkdirSync("dist/img", { recursive: true });
  await cpy("src/img/*", "dist/img");
=======
  if (fs.existsSync("src/img")) {
    fs.mkdirSync("dist/img", { recursive: true });
    await cpy("src/img/*", "dist/img");
  }
>>>>>>> after updating

  await Promise.all(BUNDLES.map(bundle)).catch(() => process.exit(1));

  // Copy servable assets to python extension (exclude esm/)
<<<<<<< before updating
  fs.mkdirSync("../airflow_config/ui/static", { recursive: true });
  await cpy("dist/**/*", "../airflow_config/ui/static", {
    filter: (file) => !path.relative(DIST_DIR, file.path).startsWith("esm"),
=======
  fs.mkdirSync("../airflow_config/extension", { recursive: true });
  await cpy("dist/**/*", "../airflow_config/extension", {
    filter: (file) =>
      !file.relativePath.startsWith("esm/") &&
      !file.relativePath.startsWith("dist/esm/"),
>>>>>>> after updating
  });
}

await build();
