from os import getenv

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths

try:
    from delete import Delete
    from dynamodb import Dynamodb
    from login import Login
    from signup import SignUp
    from update import Update
    from user import User
    from users import Users
except ImportError:
    from delete import Delete
    from login import Login
    from signup import SignUp
    from update import Update
    from user import User
    from users import Users

    from layers import Dynamodb

logger = Logger(service="App")
tracer = Tracer()
metrics = Metrics()

app = APIGatewayRestResolver(strip_prefixes=["/api/v1"])

secret = getenv("SECRET_USER_SERVICE")
dynamodb = Dynamodb(
    table_name=getenv("TABLE_NAME_DYNAMODB"),
    environment=getenv("ENVIRONMENT"),
    region=getenv("TABLE_NAME_REGION"),
    aws_secret=getenv("AWS_SECRET"),
    aws_key=getenv("AWS_KEY"),
)


@tracer.capture_method
@app.post("/service/user/login")
def login():
    login = Login(body=app.current_event.json_body, dynamodb=dynamodb)
    return login.execute()


@tracer.capture_method
@app.post("/service/user/signup")
def signup():
    sign_up = SignUp(body=app.current_event.json_body, dynamodb=dynamodb, secret=secret)
    return sign_up.execute()


@tracer.capture_method
@app.get("/service/user/<user_id>")
def user(user_id):
    logger.info(user_id)
    user = User(body={"id": user_id}, dynamodb=dynamodb)
    return user.execute()


@tracer.capture_method
@app.get("/service/users")
def users():
    users = Users(body=app.current_event.query_string_parameters, dynamodb=dynamodb)
    return users.execute()


@tracer.capture_method
@app.put("/service/user")
def update():
    update = Update(body=app.current_event.json_body, dynamodb=dynamodb, secret=secret)
    return update.execute()


@tracer.capture_method
@app.delete("/service/user")
def delete():
    delete = Delete(body=app.current_event.json_body, dynamodb=dynamodb)
    return delete.execute()


@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_REST, log_event=True
)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context):
    try:
        logger.info(f"context: {context}")
        response = app.resolve(event, context)
        logger.info(response)
        return response
    except Exception as error:
        logger.exception(error)
        return error
