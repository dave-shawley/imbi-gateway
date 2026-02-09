import datetime
import os
import typing as t

import fastapi
import pydantic
import typer
from imbi_common import server

import imbi_gateway
from imbi_gateway import integrations, lifespan, postgres


class Status(pydantic.BaseModel):
    environment: t.Annotated[
        str,
        pydantic.Field(
            description='Operating environment', examples=['production']
        ),
    ]
    service: t.Annotated[
        str, pydantic.Field(description='Service instance name')
    ] = 'imbi-gateway'
    status: t.Literal['ok', 'failing']
    version: t.Annotated[
        str,
        pydantic.Field(description='Application version', examples=['0.0.0']),
    ]
    started_at: datetime.datetime
    postgres: dict[str, int]


def create_app() -> fastapi.FastAPI:
    app = fastapi.FastAPI(
        lifespan=lifespan.Lifespan(postgres.lifespan_hook),
        version=imbi_gateway.version,
        started_at=datetime.datetime.now(datetime.UTC),
    )
    app.include_router(integrations.router)
    app.add_api_route('/status', status_endpoint, summary='Operational status')
    return app


def status_endpoint(
    *,
    request: fastapi.Request,
    context: lifespan.InjectLifespan,
) -> Status:
    pool = context.get_state(postgres.lifespan_hook)
    return Status(
        environment=os.environ.get('ENVIRONMENT', 'development'),
        status='ok',
        version=request.app.version,
        started_at=request.app.extra['started_at'],
        postgres=pool.get_stats(),
    )


cli = typer.Typer(no_args_is_help=True)
cli.command('serve')(server.bind_entrypoint('imbi_gateway.app:create_app'))


@cli.callback()
def _callback() -> None:  # pyright: ignore[reportUnusedFunction]
    """Imbi Gateway CLI"""
    # Providing an empty callback forces typer to require a command
    # name - https://typer.tiangolo.com/tutorial/commands/one-or-multiple/
    # This is only necessary since we only have one command.
