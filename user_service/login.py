import json
import os
from dataclasses import dataclass
from typing import Any, Dict

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.api_gateway import Response
from boto3.dynamodb.conditions import Key
from jsonschema import ValidationError, validate

try:
    from abstract_class import AbstractClass
    from auth import Auth
    from date import Date
    from dynamodb import Dynamodb
    from encode import Encode
except ImportError:
    from abstract_class import AbstractClass

    from layers import Auth, Date, Encode
    from layers.dynamodb import Dynamodb

logger = Logger(service="LoginServiceSignup")


def exception_handler(status_code, error):
    body = {
        "status_code": status_code,
        "headers": {"Content-Type": "application/json"},
        "message": str(error),
    }
    return Response(
        status_code=status_code, content_type="application/json", body=json.dumps(body)
    )


def response_handler(body: dict, status_code=200):
    return Response(
        status_code=status_code, content_type="application/json", body=json.dumps(body)
    )


@dataclass
class Login(AbstractClass):
    body: dict
    _username: str = ""
    _secret: str = os.getenv("SECRET_USER_SERVICE")
    _date: Date = Date()
    _encode: Encode = Encode()
    _auth: Auth = Auth()
    _dynamodb: Dynamodb = Dynamodb(
        table_name=os.getenv("TABLE_NAME_DYNAMODB"),
        environment=os.getenv("ENVIRONMENT"),
        region=os.getenv("TABLE_NAME_REGION"),
        aws_secret=os.getenv("AWS_SECRET"),
        aws_key=os.getenv("AWS_KEY"),
    )

    def __post_init__(self):
        self._username = self.body.get("username")
        self._password = self.body.get("password")

    def get_user_to_username(self) -> Dict[Any, Any]:
        key_condition_expression = Key("username").eq(self._username.lower())
        response = self._dynamodb.query(KeyConditionExpression=key_condition_expression)
        if response.get("Items"):
            return response.get("Items")[0]
        return {}

    def execute(self) -> Response:
        try:
            self._validate()
            user = self.get_user_to_username()
            if not user:
                return exception_handler(
                    status_code=400, error="As credenciais estão incorretas."
                )
            password_in_db = self._encode.encode_string(user.get("password"))
            password = self._encode.encode_string(self._password)
            password_is_valid = self._encode.check_password(password, password_in_db)
            if password_is_valid:
                return response_handler(
                    status_code=200, body={"token": user.get("token")}
                )
            return exception_handler(
                status_code=400, error="As credenciais estão incorretas."
            )
        except ValidationError as error:
            return exception_handler(status_code=400, error=error.message)

    def _validate(self) -> None:
        validate(self.body, self._get_schema())

    def _get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"},
            },
            "required": [
                "username",
                "password",
            ],
        }
