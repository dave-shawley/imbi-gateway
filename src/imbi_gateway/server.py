import pathlib
import tomllib
import typing as t
from importlib import resources

import typer
import uvicorn

cli = typer.Typer()


class ServerParams(t.TypedDict):
    dev: t.NotRequired[bool]
    env_file: t.NotRequired[pathlib.Path]
    host: t.NotRequired[str]
    log_config: t.NotRequired[pathlib.Path]
    port: t.NotRequired[int]
    verbose: t.NotRequired[bool]


class _UvicornRunParams(t.TypedDict):
    """Typed parameters for uvicorn.run()"""

    env_file: pathlib.Path | None
    factory: bool
    host: str
    log_config: dict[str, t.Any]
    port: int
    reload: t.NotRequired[bool]


@cli.command()
def serve(  # noqa: PLR0913 - too many arguments
    entrypoint: str,
    *,
    dev: bool = False,
    env_file: pathlib.Path | None = None,
    host: str = '127.0.0.1',
    log_config: pathlib.Path | None = None,
    port: int = 8000,
    verbose: bool = False,
) -> None:
    config_data = None
    if log_config is not None:
        config_data = tomllib.loads(log_config.read_text())
    else:
        config_data = tomllib.loads(
            resources.read_text('imbi_common', 'log-config.toml')
        )
    if verbose:
        package_name = entrypoint.partition(':')[0]
        root_module = package_name.partition('.')[0]
        loggers = t.cast(
            'dict[str,dict[str,object]]', config_data.setdefault('loggers', {})
        )
        logger_cfg = loggers.setdefault(root_module, {})
        logger_cfg['level'] = 'DEBUG'
        logger_cfg = loggers.setdefault('imbi_common', {})
        logger_cfg['level'] = 'DEBUG'

    args: _UvicornRunParams = {
        'env_file': env_file,
        'factory': True,
        'host': host,
        'log_config': config_data,
        'port': port,
    }
    if dev:
        args['reload'] = True
    uvicorn.run(entrypoint, **args)
