import json
import re
from dataclasses import dataclass

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
class SignUp(AbstractClass):
    body: dict
    _username: str = ""
    _password: str = ""
    _email: str = ""
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
        self._email = self.body.get("email")

    def get_username_in_database(self) -> list:
        key_condition_expression = Key("username").eq(self._username.lower())
        response = self._dynamodb.query(KeyConditionExpression=key_condition_expression)
        return response.get("Items")

    def create_user_in_database(self, user: dict):
        response = self._dynamodb.create(item=user)
        return response

    def execute(self) -> Response:
        try:
            self._validate()
            if not self._validate_email():
                return exception_handler(status_code=400, error="Email está inválido.")
            response = self.get_username_in_database()
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

    def _get_dict(self) -> dict:
        encoded_password = self._encode.encode_string(self._password)
        password_hash = self._encode.get_hash(encoded_password)
        created_at = self._date.get_date_in_iso_format()
        user_id = self._encode.get_id()
        payload_to_jwt = self._auth.get_payload_to_jwt(aud=user_id)
        token = self._auth.generate_access_token(
            payload=payload_to_jwt, secret=self._secret
        )
        return {
            "username": self._username,
            "email": self._email,
            "password": password_hash.decode("utf-8"),
            "created_at": created_at,
            "id": user_id,
            "token": token,
        }

    def _validate(self) -> None:
        validate(self.body, self._get_schema())

    def _get_schema(self) -> dict:
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
        pattern = re.compile(r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?")
        if re.match(pattern, self._email):
            return True
        return False
