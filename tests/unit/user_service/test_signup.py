import pytest

from user_service.signup import SignUp
from aws_lambda_powertools.event_handler.api_gateway import Response

from faker import Faker


fake = Faker()


@pytest.mark.parametrize(
    "body",
    [
        {
            "username": fake.name(),
            "password": fake.password(length=12)
        },
        {
            "username": fake.name(),
            "password": fake.password(length=12)
        },
        {
            "username": fake.name(),
            "password": fake.password(length=12)
        },
    ],
)
def test_execute_success(body):
    sign_up = SignUp(body=body)
    response = sign_up.execute()
    assert isinstance(response, Response)
    assert response.status_code == 201


@pytest.mark.parametrize(
    "body",
    [
        {
            "username": fake.name(),
            "password": fake.password(length=12)
        },
        {
            "username": fake.name(),
            "password": fake.password(length=12)
        },
        {
            "username": fake.name(),
            "password": fake.password(length=12)
        },
    ],
)
def test_get_dict_success(body):
    sign_up = SignUp(body=body)
    response = sign_up._get_dict()
    assert isinstance(response, dict)


@pytest.mark.parametrize(
    "body",
    [
        {
            "username": fake.name(),
            "password": fake.pyint()
        },
        {
            "username": fake.pyint(),
            "password": fake.pyint()
        },
        {
            "username": None,
            "password": fake.random.random()
        },
    ],
)
def test_execute_error(body):
    sign_up = SignUp(body=body)
    response = sign_up.execute()
    assert response.status_code == 400
