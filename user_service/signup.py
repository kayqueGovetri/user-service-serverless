from dataclasses import dataclass
from re import compile, match

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
class SignUp:
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
        self.password = self.body.get("password")
        self.email = self.body.get("email")

    def get_email_in_database(self) -> list:
        key_condition_expression = Key("email").eq(self.email.lower())
        response = self.dynamodb.query(
            KeyConditionExpression=key_condition_expression, IndexName="gsiEmail"
        )
        return response.get("Items")

    def create_user_in_database(self, user: dict):
        response = self.dynamodb.create(item=user)
        return response

    def execute(self) -> Response:
        try:
            self._validate()
            if not self._validate_email():
                return exception_handler(status_code=400, error="Email está inválido.")
            response = self.get_email_in_database()
            if response:
                return exception_handler(
                    status_code=400,
                    error="Já existe um usuário na base com o mesmo nome.",
                )
            user_dict = self._get_dict()
            response = self.create_user_in_database(user=user_dict)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return response_handler(status_code=201, body=user_dict)
            return response_handler(status_code=201, body={})
        except ValidationError as error:
            return exception_handler(status_code=400, error=error.message)
        except Exception as error:
            return exception_handler(status_code=400, error=error)

    def _get_dict(self) -> dict:
        encoded_password = self.encode.encode_string(self.password)
        password_hash = self.encode.get_hash(encoded_password)
        created_at = self.date.get_date_in_iso_format()
        user_id = f"USER#{self.encode.get_id()}"
        payload_to_jwt = self.auth.get_payload_to_jwt(aud=user_id)
        token = self.auth.generate_access_token(
            payload=payload_to_jwt, secret=self.secret
        )
        return {
            "username": self.username,
            "email": self.email,
            "password": password_hash.decode("utf-8"),
            "created_at": created_at,
            "pk": user_id,
            "sk": "USER",
            "token": token,
            "deleted": "false",
        }

    def _validate(self) -> None:
        validate(self.body, self._get_schema())

    @staticmethod
    def _get_schema() -> dict:
        return {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"},
                "email": {"type": "string"},
            },
            "required": ["username", "password", "email"],
        }

    def _validate_email(self) -> bool:
        pattern = compile(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?")
        if match(pattern, self.email):
            return True
        return False
