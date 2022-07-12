from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths

try:
    from login import Login
    from signup import SignUp
except ImportError:
    from login import Login
    from signup import SignUp

logger = Logger(service="LoginServiceFunction")

app = APIGatewayRestResolver()


@app.post("/service/user/signup")
def signup():
    sign_up = SignUp(body=app.current_event.json_body)
    return sign_up.execute()


@app.get("/service/user/login")
def login():
    login = Login(body=app.current_event.json_body)
    return login.execute()


@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_REST, log_event=True
)
def lambda_handler(event, context):
    try:
        return app.resolve(event, context)
    except Exception as error:
        # TODO: Return response
        print(error)
