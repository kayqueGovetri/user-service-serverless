from dataclasses import dataclass

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
    from layers import Auth, Date, Encode
    from layers.dynamodb import Dynamodb
    from layers.utils import exception_handler, response_handler

logger = Logger(service="LoginServiceSignup")


@dataclass
class Delete:
    body: dict
    dynamodb: Dynamodb
    date: Date = Date()
    encode: Encode = Encode()
    auth: Auth = Auth()

    def __post_init__(self):
        self.id = self.body.get("id")

    def delete_in_database(self) -> dict:
        user = self.get_user_in_database()
        user = {**user, "deleted": "true"}
        self.dynamodb.update(item=user)
        return user

    def get_user_in_database(self):
        key_condition_expression = Key("pk").eq(self.id) & Key("sk").eq("USER")
        response = self.dynamodb.query(KeyConditionExpression=key_condition_expression)

        if not response.get("Items"):
            raise Exception("User not exists")

        return response.get("Items")[0]

    def execute(self) -> Response:
        try:
            self._validate()
            user = self.delete_in_database()
            del user["password"]
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
