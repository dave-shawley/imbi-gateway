import fastapi


def instrument(app: fastapi.FastAPI) -> fastapi.FastAPI:
    """Add Prometheus instrumentation to the application.

    This function needs to be a wrapper instead of a lifespan
    hook since it adds a middleware to the application.

    Args:
        app: The application to instrument.
    Returns:
        The application with instrumentation added.
    """
    try:
        import prometheus_fastapi_instrumentator as p  # noqa: PLC0415
    except ImportError:  # pragma: no cover
        pass
    else:
        instrumentor = p.Instrumentator(excluded_handlers=['/metrics'])
        instrumentor.instrument(app)
        instrumentor.expose(app)
    return app
