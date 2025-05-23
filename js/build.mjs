import { build } from "@finos/perspective-esbuild-plugin/build.js";
import { BuildCss } from "@prospective.co/procss/target/cjs/procss.js";
import { getarg } from "./tools/getarg.mjs";
import fs from "fs";
import cpy from "cpy";
import { createRequire } from "node:module";

const DEBUG = getarg("--debug");

const COMMON_DEFINE = {
  global: "window",
  "process.env.DEBUG": `${DEBUG}`,
};

const BUILD = [
  {
    define: COMMON_DEFINE,
    entryPoints: ["src/ts/index.ts"],
    plugins: [],
    format: "esm",
    loader: {
      ".css": "text",
      ".html": "text",
    },
    outfile: "dist/cdn/index.js",
  },
];

const require = createRequire(import.meta.url);
function add(builder, path, path2) {
  builder.add(path, fs.readFileSync(require.resolve(path2 || path)).toString());
}

async function compile_css() {
  const builder1 = new BuildCss("");
  add(builder1, "./src/less/index.less");
  // add(
  //   builder1,
  //   "shoelace_light.css",
  //   "@shoelace-style/shoelace/dist/themes/light.css",
  // );

  const css = builder1.compile().get("index.css");

  fs.mkdirSync("dist/css", { recursive: true });
  fs.writeFileSync("dist/css/index.css", css);
}
async function copy_to_python() {
  fs.mkdirSync("../airflow_config/ui/static", { recursive: true });
  cpy("dist/**/*", "../airflow_config/ui/static");
}

async function build_all() {
  await compile_css();
  await Promise.all(BUILD.map(build)).catch(() => process.exit(1));
  await copy_to_python();
}

build_all();
