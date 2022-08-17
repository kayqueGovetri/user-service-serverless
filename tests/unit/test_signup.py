from os import environ

import pytest
from faker import Faker

from user_service.signup import SignUp

faker = Faker()


@pytest.mark.parametrize(
    "body",
    [
        {
            "username": faker.name(),
            "password": faker.password(),
            "email": faker.email(),
        },
        {
            "username": faker.name(),
            "password": faker.password(),
            "email": faker.email(),
        },
        {
            "username": faker.name(),
            "password": faker.password(),
            "email": faker.email(),
        },
    ],
)
def test_signup_execute_success(dynamodb, body):
    signup = SignUp(body=body, secret=environ["SECRET"], dynamodb=dynamodb)
    response = signup.execute()
    assert response.status_code == 201


@pytest.mark.parametrize(
    "body",
    [
        {
            "username": faker.name(),
            "password": faker.password(),
            "email": "test@gmail.com",
        },
        {
            "username": faker.name(),
            "password": faker.password(),
            "email": "testgmail.com",
        },
        {"username": faker.name(), "password": faker.password()},
        {"password": faker.password(), "email": faker.email()},
        {"username": faker.name(), "email": faker.email()},
        {"username": faker.name(), "password": faker.password()},
    ],
)
def test_signup_execute_error(dynamodb, body):
    signup = SignUp(body=body, secret=environ["SECRET"], dynamodb=dynamodb)
    response = signup.execute()
    assert response.status_code == 400


@pytest.mark.parametrize(
    "body,expected",
    [
        (
            {
                "username": faker.name(),
                "password": faker.password(),
                "email": "test@gmail.com",
            },
            1,
        ),
        (
            {
                "username": faker.name(),
                "password": faker.password(),
                "email": faker.email(),
            },
            0,
        ),
    ],
)
def test_signup_get_email_in_database(dynamodb, body, expected):
    signup = SignUp(body=body, secret=environ["SECRET"], dynamodb=dynamodb)
    items = signup.get_email_in_database()
    assert len(items) == expected


@pytest.mark.parametrize(
    "body",
    [
        {
            "username": faker.name(),
            "password": faker.password(),
            "email": faker.email(),
        },
        {
            "username": faker.name(),
            "password": faker.password(),
            "email": faker.email(),
        },
        {
            "username": faker.name(),
            "password": faker.password(),
            "email": faker.email(),
        },
    ],
)
def test_signup_create_user_in_database(dynamodb, body):
    signup = SignUp(body=body, secret=environ["SECRET"], dynamodb=dynamodb)
    user = signup._get_dict()
    response = signup.create_user_in_database(user=user)
    assert response.get("ResponseMetadata").get("HTTPStatusCode") == 200
