import pytest
from faker import Faker

from user_service.users import Users

faker = Faker()


@pytest.mark.parametrize(
    "body",
    [
        {"page": "1", "limit": "100"},
    ],
)
def test_users_execute_success(dynamodb, body):
    users = Users(body=body, dynamodb=dynamodb)
    response = users.execute()
    assert response.status_code == 200


@pytest.mark.parametrize(
    "body",
    [
        {"page": "0", "limit": "100"},
    ],
)
def test_users_execute_error(dynamodb, body):
    user = Users(body=body, dynamodb=dynamodb)
    response = user.execute()
    assert response.status_code == 400
