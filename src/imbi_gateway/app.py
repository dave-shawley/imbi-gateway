import fastapi

from imbi_gateway import telemetry


def create_app() -> fastapi.FastAPI:
    app = fastapi.FastAPI()
    return telemetry.instrument(app)
