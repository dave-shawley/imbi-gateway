import os

import fastapi
import httpx
import opentelemetry.trace
import yarl

from imbi_gateway import telemetry

api = fastapi.APIRouter()


def create_app() -> fastapi.FastAPI:
    app = fastapi.FastAPI()
    app.include_router(api)
    return telemetry.instrument(app)


@api.get('/request')
async def request(
    *, response: fastapi.Response
) -> dict[str, str]:  # pragma: no cover
    span = opentelemetry.trace.get_current_span()
    ctx = span.get_span_context()
    response.headers['trace-id'] = f'{ctx.trace_id:x}'

    try:
        peer_url = yarl.URL(os.environ['PEER_URL'])
    except KeyError:
        return {'message': 'Hello World'}

    url = peer_url / 'do-the-thing'
    async with httpx.AsyncClient() as client:
        rsp = await client.get(str(url))
        return rsp.json()  # type: ignore[no-any-return]
