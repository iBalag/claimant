from aiohttp.web import Response, Request, Application, RouteTableDef, run_app, json_response
from aiohttp_swagger import setup_swagger


routes = RouteTableDef()


@routes.get("/hello", allow_head=False)
async def hello(request: Request):
    """
    ---
    description: This end-point allow to test that service is up.
    tags:
    - Health check
    produces:
    - application/json
    responses:
        "200":
            description: successful operation. Return "pong" text
        "405":
            description: invalid HTTP Method
    """
    data = {"a": 1, "b": 2}
    return json_response(data)


app: Application = Application()
app.add_routes(routes)

setup_swagger(app)
run_app(app)
