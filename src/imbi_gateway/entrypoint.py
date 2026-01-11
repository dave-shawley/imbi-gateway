import pathlib

import typer

from imbi_gateway import server  # will be moved to imbi-common

cli = typer.Typer()


@cli.command()
def serve(  # noqa: PLR0913 - too many arguments
    dev: bool = False,
    env_file: pathlib.Path | None = None,
    host: str = '127.0.0.1',
    log_config: pathlib.Path | None = None,
    port: int = 8000,
    verbose: bool = False,
) -> None:
    server.serve(
        'imbi_gateway.app:create_app',
        dev=dev,
        env_file=env_file,
        host=host,
        log_config=log_config,
        port=port,
        verbose=verbose,
    )
