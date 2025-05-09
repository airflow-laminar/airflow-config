import { NodeModulesExternal } from "@finos/perspective-esbuild-plugin/external.js";
import { build } from "@finos/perspective-esbuild-plugin/build.js";
import { BuildCss } from "@prospective.co/procss/target/cjs/procss.js";
import { getarg } from "./tools/getarg.mjs";
import fs from "fs";
import cpy from "cpy";
import path_mod from "path";

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

async function compile_css() {
  const process_path = (path) => {
    const outpath = path.replace("src/less", "dist/css");
    fs.mkdirSync(outpath, { recursive: true });

    fs.readdirSync(path).forEach((file_or_folder) => {
      if (file_or_folder.endsWith(".less")) {
        const outfile = file_or_folder.replace(".less", ".css");
        const builder = new BuildCss("");
        builder.add(
          `${path}/${file_or_folder}`,
          fs
            .readFileSync(path_mod.join(`${path}/${file_or_folder}`))
            .toString(),
        );
        fs.writeFileSync(
          `${path.replace("src/less", "dist/css")}/${outfile}`,
          builder.compile().get(outfile),
        );
      } else {
        process_path(`${path}/${file_or_folder}`);
      }
    });
  };
  // recursively process all less files in src/less
  process_path("src/less");
  cpy("src/css/*", "dist/css/");
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
