from os import environ
from unittest import mock

from boto3 import resource
from faker import Faker
from moto import mock_dynamodb2
from pytest import fixture

from layers import Auth, Date, Dynamodb, Encode

faker = Faker()
encode = Encode()
date = Date()
auth = Auth()


@fixture(autouse=True, scope="session")
def mock_env():
    environ["AWS_KEY"] = "testing"
    environ["AWS_SECRET"] = "testing"
    environ["REGION"] = "us-east-1"
    environ["AWS_ACCESS_KEY_ID"] = "testing"
    environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    environ["AWS_SECURITY_TOKEN"] = "testing"
    environ["AWS_SESSION_TOKEN"] = "testing"
    environ["ENVIRONMENT"] = "prod"
    environ["TABLE_NAME"] = "LoginServiceTable"
    environ["SECRET"] = "testing"


@fixture()
def mock_table():
    with mock_dynamodb2():
        dynamodb = resource("dynamodb", region_name="eu-west-2")
        dynamodb.create_table(
            AttributeDefinitions=[
                {"AttributeName": "pk", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"},
                {"AttributeName": "email", "AttributeType": "S"},
                {"AttributeName": "username", "AttributeType": "S"},
                {"AttributeName": "deleted", "AttributeType": "S"},
            ],
            TableName=environ["TABLE_NAME"],
            KeySchema=[
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "gsiEmail",
                    "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "gsiUsername",
                    "KeySchema": [{"AttributeName": "username", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "gsiDeletedUsers",
                    "KeySchema": [
                        {"AttributeName": "sk", "KeyType": "HASH"},
                        {"AttributeName": "deleted", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "gsiUsers",
                    "KeySchema": [
                        {"AttributeName": "sk", "KeyType": "HASH"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        table = dynamodb.Table(environ["TABLE_NAME"])
        yield table


@fixture()
def dynamodb(mock_get_table):
    with mock.patch.object(Dynamodb, "get_table", new=mock_get_table):
        dynamodb = Dynamodb(
            environment=environ["ENVIRONMENT"],
            table_name=environ["TABLE_NAME"],
            aws_key=environ["AWS_KEY"],
            region=environ["REGION"],
            aws_secret=environ["AWS_SECRET"],
        )
        create_user_test(dynamodb)
        yield dynamodb


@fixture()
def mock_get_table(mock_table):
    def get_table(self):
        self.table = mock_table

    return get_table


def create_user_test(dynamodb):
    encoded_password = encode.encode_string("test")
    password_hash = encode.get_hash(encoded_password)
    created_at = date.get_date_in_iso_format()
    user_id = "USER#28807c9c-6032-4464-98d7-ad2e0ac4e8c1"
    payload_to_jwt = auth.get_payload_to_jwt(aud=user_id)
    token = auth.generate_access_token(payload=payload_to_jwt, secret=environ["SECRET"])
    user = {
        "pk": user_id,
        "email": "test@gmail.com",
        "sk": "USER",
        "username": faker.name(),
        "token": token,
        "deleted": "false",
        "password": password_hash.decode("utf-8"),
        "created_at": created_at,
    }
    dynamodb.create(item=user)
    return user
