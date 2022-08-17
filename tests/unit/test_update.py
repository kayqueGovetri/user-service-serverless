from os import environ

import pytest
from faker import Faker

from user_service.update import Update

faker = Faker()


@pytest.mark.parametrize(
    "body",
    [
        {
            "id": "USER#28807c9c-6032-4464-98d7-ad2e0ac4e8c1",
            "password": "teste",
            "email": "teste@gmail.com",
        },
    ],
)
def test_update_execute_success(dynamodb, body):
    update = Update(body=body, dynamodb=dynamodb, secret=environ["SECRET"])
    response = update.execute()
    assert response.status_code == 201


@pytest.mark.parametrize(
    "body",
    [
        {
            "id": "USER#28807c9c-6032-4464-98d7-ad2e0ac4e8c",
            "password": "teste",
            "email": "teste@gmail.com",
        },
    ],
)
def test_update_execute_error(dynamodb, body):
    update = Update(body=body, dynamodb=dynamodb, secret=environ["SECRET"])
    response = update.execute()
    assert response.status_code == 400
