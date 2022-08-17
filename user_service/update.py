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
class Update:
    body: dict
    dynamodb: Dynamodb
    secret: str
    username: str = ""
    password: str = ""
    email: str = ""
    date: Date = Date()
    encode: Encode = Encode()
    auth: Auth = Auth()

    def __post_init__(self):
        self.username = self.body.get("username")
        self.id = self.body.get("id")
        self.email = self.body.get("email")
        self.password = self.body.get("password")

    def update_in_database(self) -> dict:
        user = self.get_user_in_database()
        user = {**user, **self.body}
        self.dynamodb.update(item=user)
        return user

    def get_username_in_database(self):
        key_condition_expression = Key("username").eq(self.username.lower())
        response = self.dynamodb.query(
            KeyConditionExpression=key_condition_expression, IndexName="gsiUsername"
        )

        if response.get("Items"):
            raise Exception("Username exists")

        return {}

    def get_email_in_database(self):
        key_condition_expression = Key("email").eq(self.email.lower())
        response = self.dynamodb.query(
            KeyConditionExpression=key_condition_expression, IndexName="gsiEmail"
        )

        if response.get("Items"):
            raise Exception("Email exists")

        return {}

    def get_user_in_database(self):
        key_condition_expression = Key("pk").eq(self.id) & Key("sk").eq("USER")
        response = self.dynamodb.query(KeyConditionExpression=key_condition_expression)

        if not response.get("Items"):
            raise Exception("User not exists")

        return response.get("Items")[0]

    def get_password(self):
        if self.password:
            encoded_password = self.encode.encode_string(self.password)
            password_hash = self.encode.get_hash(encoded_password)
            user = self.get_user_in_database()
            payload_to_jwt = self.auth.get_payload_to_jwt(aud=user.get("id"))
            token = self.auth.generate_access_token(
                payload=payload_to_jwt, secret=self.secret
            )
            return {"password": password_hash.decode("utf-8"), "token": token}

    def execute(self) -> Response:
        try:
            self._validate()
            factory = self.factory_validate_update()
            del self.body["id"]
            for key in self.body.keys():
                func = factory.get(key)
                if not func:
                    return exception_handler(
                        status_code=400, error=f"Parameters {key} not exists"
                    )
                response = func()
                self.body = {**self.body, **response}
            user_updated = self.update_in_database()
            del user_updated["password"]
            return response_handler(status_code=201, body=user_updated)
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
                "password": {"type": "string"},
                "email": {"type": "string"},
                "username": {"type": "string"},
            },
            "required": ["id"],
        }

    def factory_validate_update(self):
        return {
            "username": self.get_username_in_database,
            "email": self.get_email_in_database,
            "password": self.get_password,
        }
