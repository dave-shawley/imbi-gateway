import contextlib
import typing as t
from collections import abc

import fastapi
import psycopg.rows
import psycopg_pool
import pydantic
import pydantic_settings

from imbi_gateway import lifespan


class PostgresSettings(pydantic_settings.BaseSettings):
    model_config: t.ClassVar[pydantic_settings.SettingsConfigDict] = {
        'env_prefix': 'POSTGRES_'
    }
    url: pydantic.PostgresDsn


RowType = psycopg.rows.DictRow
ConnectionType = psycopg.AsyncConnection[RowType]
CursorType = psycopg.AsyncCursor[RowType]
PoolType = psycopg_pool.AsyncConnectionPool[ConnectionType]


@contextlib.asynccontextmanager
async def lifespan_hook() -> abc.AsyncIterator[PoolType]:
    settings = PostgresSettings()  # type: ignore[call-arg]
    async with psycopg_pool.AsyncConnectionPool(
        settings.url.encoded_string(),
        open=False,
        configure=_configure_connection,
        connection_class=ConnectionType,
    ) as pool:
        await pool.open(wait=False)
        yield pool


@contextlib.asynccontextmanager
async def model_cursor[T: pydantic.BaseModel](
    conn: ConnectionType, cls: type[T]
) -> abc.AsyncIterator[psycopg.AsyncCursor[T]]:
    row_factory = conn.row_factory
    try:
        new_conn = t.cast('psycopg.AsyncConnection[T]', conn)
        new_conn.row_factory = psycopg.rows.class_row(cls)
        async with new_conn.cursor() as cursor:
            yield cursor
    finally:
        conn.row_factory = row_factory


async def _configure_connection(conn: ConnectionType) -> None: ...


async def _get_connection(
    context: lifespan.InjectLifespan,
) -> abc.AsyncIterator[ConnectionType]:
    pool = context.get_state(lifespan_hook)
    async with pool.connection() as conn:
        yield conn


@contextlib.asynccontextmanager
async def _get_cursor(
    context: lifespan.InjectLifespan,
) -> abc.AsyncIterator[CursorType]:
    pool = context.get_state(lifespan_hook)
    async with pool.connection() as conn, conn.cursor() as cursor:
        yield cursor


Connection = t.Annotated[ConnectionType, fastapi.Depends(_get_connection)]
Cursor = t.Annotated[CursorType, fastapi.Depends(_get_cursor)]
