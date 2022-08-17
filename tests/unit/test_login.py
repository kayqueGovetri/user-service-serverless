import pytest
from faker import Faker

from user_service.login import Login

faker = Faker()


@pytest.mark.parametrize(
    "body",
    [
        {"password": "test", "email": "test@gmail.com"},
    ],
)
def test_login_execute_success(dynamodb, body):
    login = Login(body=body, dynamodb=dynamodb)
    response = login.execute()
    assert response.status_code == 200


@pytest.mark.parametrize(
    "body",
    [
        {"password": faker.password(), "email": faker.email()},
        {"password": "teste", "email": "test@gmail.com"},
        {"password": faker.password()},
        {"email": faker.email()},
    ],
)
def test_login_execute_error(dynamodb, body):
    login = Login(body=body, dynamodb=dynamodb)
    response = login.execute()
    assert response.status_code == 400
