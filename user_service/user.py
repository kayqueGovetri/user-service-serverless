from dataclasses import dataclass

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.api_gateway import Response
from boto3.dynamodb.conditions import Key
from jsonschema import ValidationError, validate

try:
    from dynamodb import Dynamodb
    from utils import exception_handler, response_handler
except ImportError:
    from layers.dynamodb import Dynamodb
    from layers.utils import exception_handler, response_handler

logger = Logger(service="LoginServiceSignup")


@dataclass
class User:
    body: dict
    dynamodb: Dynamodb

    def __post_init__(self):
        self.id = self.body.get("id")

    def get_user_in_database(self):
        key_condition_expression = Key("pk").eq(f"{self.id}") & Key("sk").eq("USER")
        response = self.dynamodb.query(KeyConditionExpression=key_condition_expression)

        if not response.get("Items"):
            raise Exception("User not exists")

        return response.get("Items")[0]

    def execute(self) -> Response:
        try:
            self._validate()
            user = self.get_user_in_database()
            return response_handler(status_code=200, body=user)
        except ValidationError as error:
            return exception_handler(status_code=400, error=error.message)
        except Exception as error:
            return exception_handler(status_code=400, error=error)

    def _validate(self) -> None:
        validate(self.body, self._get_schema())

    @staticmethod
    def _get_schema() -> dict:
        return {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
            },
            "required": ["id"],
        }
