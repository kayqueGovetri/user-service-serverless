import pytest
from faker import Faker

from user_service.user import User

faker = Faker()


@pytest.mark.parametrize(
    "body",
    [
        {"id": "USER#28807c9c-6032-4464-98d7-ad2e0ac4e8c1"},
    ],
)
def test_users_execute_success(dynamodb, body):
    user = User(body=body, dynamodb=dynamodb)
    response = user.execute()
    assert response.status_code == 200


@pytest.mark.parametrize(
    "body",
    [
        {"id": "USER#28807c9c-6032-4464-98d7-ad2e0ac4e8"},
        {},
        {"id": ""},
    ],
)
def test_user_execute_error(dynamodb, body):
    user = User(body=body, dynamodb=dynamodb)
    response = user.execute()
    assert response.status_code == 400
