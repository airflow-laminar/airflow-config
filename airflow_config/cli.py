import sys
from argparse import ArgumentParser
from importlib import import_module
from pathlib import Path

from airflow_config import load_config


def _parser() -> ArgumentParser:
    parser = ArgumentParser(description="Generate Airflow DAG files from an airflow-config YAML file.")
    parser.add_argument("config", type=Path, help="Path to the airflow-config YAML file")
    parser.add_argument("-o", "--output-dir", type=Path, required=True, help="Directory for generated DAG files")
    parser.add_argument("--airflow-version", type=int, choices=(2, 3), required=True, help="Target Airflow major version")
    parser.add_argument("--override", action="append", default=[], help="Hydra override; may be specified more than once")
    parser.add_argument(
        "--import",
        dest="imports",
        action="append",
        default=[],
        metavar="MODULE",
        help="Module to import before loading the config, e.g. to register OmegaConf resolvers; may be specified more than once",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.append(cwd)
    for module in args.imports:
        import_module(module)
    config_path = args.config.resolve()
    config = load_config(
        config_path.parent.name,
        config_path.name,
        overrides=args.override,
        basepath=str(config_path),
    )
    config.generate(args.output_dir, airflow_major_version=args.airflow_version)


if __name__ == "__main__":
    main()
