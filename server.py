import traceback

from sanic import Sanic, json
from sanic_security.authentication import initialize_security
from tortoise.contrib.sanic import register_tortoise

from research_guard.blueprints.view import api, api_models
from research_guard.common.util import config

app = Sanic("research_guard")
app.blueprint(api)
app.static("/", "static", name="research_guard_static")


@app.exception(Exception)
async def exception_parser(request, e):
    traceback.print_exc()
    return json(
        {
            "data": e.__class__.__name__,
            "message": str(e),
        },
        e.status_code if hasattr(e, "status_code") else 500,
    )


app.config.PROXIES_COUNT = 2
register_tortoise(
    app,
    db_url=config.DATABASE_URL,
    modules={"models": api_models},
    generate_schemas=config.GENERATE_SCHEMAS,
)
initialize_security(app)
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, workers=1, debug=config.DEBUG)
