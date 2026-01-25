import fastapi

app = fastapi.FastAPI()


@app.get('/do-the-thing')
def do_the_thing() -> dict[str, str]:
    return {'operation': 'did-the-thing'}
