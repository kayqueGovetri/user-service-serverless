from dataclasses import dataclass
from typing import Any, Dict

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.api_gateway import Response
from boto3.dynamodb.conditions import Key
from jsonschema import ValidationError, validate

try:
    from auth import Auth
    from date import Date
    from dynamodb import Dynamodb
    from encode import Encode
    from utils import exception_handler, response_handler
except ImportError:
    from layers import Auth, Date, Dynamodb, Encode
    from layers.utils import exception_handler, response_handler

logger = Logger(service="UserServiceLogin")


@dataclass
class Login:
    body: dict
    dynamodb: Dynamodb
    _email: str = ""
    _date: Date = Date()
    _encode: Encode = Encode()
    _auth: Auth = Auth()

    def __post_init__(self):
        self._email = self.body.get("email")
        self._password = self.body.get("password")
        logger.info(f"Body in login: {self.body}")

    def get_user_to_email(self) -> Dict[Any, Any]:
        key_condition_expression = Key("email").eq(self._email.lower())
        response = self.dynamodb.query(
            KeyConditionExpression=key_condition_expression, IndexName="gsiEmail"
        )
        if response.get("Items"):
            return response.get("Items")[0]
        return {}

    def execute(self) -> Response:
        try:
            self._validate()
            user = self.get_user_to_email()
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
        except Exception as error:
            return exception_handler(status_code=400, error=str(error))

    def _validate(self) -> None:
        validate(self.body, self._get_schema())

    def _get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "password": {"type": "string"},
            },
            "required": [
                "email",
                "password",
            ],
        }
