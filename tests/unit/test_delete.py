import pytest
from faker import Faker

from user_service.delete import Delete

faker = Faker()


@pytest.mark.parametrize(
    "body",
    [
        {"id": "USER#28807c9c-6032-4464-98d7-ad2e0ac4e8c1"},
    ],
)
def test_delete_execute_success(dynamodb, body):
    delete = Delete(body=body, dynamodb=dynamodb)
    response = delete.execute()
    assert response.status_code == 200


@pytest.mark.parametrize(
    "body",
    [
        {"id": "USER#28807c9c-6032-4464-98d7-ad2e0ac4e8"},
        {},
        {"id": ""},
    ],
)
def test_delete_execute_error(dynamodb, body):
    update = Delete(body=body, dynamodb=dynamodb)
    response = update.execute()
    assert response.status_code == 400
