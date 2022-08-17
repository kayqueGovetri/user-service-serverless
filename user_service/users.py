from dataclasses import dataclass
from math import ceil

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler.api_gateway import Response
from boto3.dynamodb.conditions import Key
from jsonschema import ValidationError

try:
    from dynamodb import Dynamodb
    from utils import exception_handler, response_handler
except ImportError:
    from layers.dynamodb import Dynamodb
    from layers.utils import exception_handler, response_handler

logger = Logger(service="LoginServiceSignup")


@dataclass
class Users:
    body: dict
    dynamodb: Dynamodb

    def __post_init__(self):
        self.last_evaluated_key = self.body.get("last_evaluated_key")
        self.limit = int(self.body.get("limit", 50))
        self.page = int(self.body.get("page"))

    def get_users_in_database(self):
        key_condition_expression = Key("sk").eq("USER")
        index_name = "gsiUsers"

        count = self.dynamodb.count(
            KeyConditionExpression=key_condition_expression,
            IndexName=index_name,
            TableName=self.dynamodb.table_name,
            Limit=self.limit,
        )

        pages = ceil(count / self.limit)
        if self.page > pages or self.page == 0:
            raise Exception("Page not exists")

        if self.last_evaluated_key:
            exclusive_start_key = {"pk": self.last_evaluated_key, "sk": "USER"}
            response = self.dynamodb.query(
                KeyConditionExpression=key_condition_expression,
                IndexName=index_name,
                TableName=self.dynamodb.table_name,
                Limit=self.limit,
                ExclusiveStartKey=exclusive_start_key,
            )
        else:
            response = self.dynamodb.query(
                KeyConditionExpression=key_condition_expression,
                IndexName=index_name,
                TableName=self.dynamodb.table_name,
                Limit=self.limit,
            )

        if not response.get("Items"):
            raise Exception("User not exists")

        last_evaluated_key = response.get("LastEvaluatedKey")

        users = {
            "users": response.get("Items"),
            "last_evaluated_key": last_evaluated_key.get("pk")
            if last_evaluated_key
            else "",
            "limit": self.limit,
            "count": count,
            "pages": pages,
            "page": self.page,
        }

        return users

    def execute(self) -> Response:
        try:
            users = self.get_users_in_database()
            logger.info(users)
            return response_handler(status_code=200, body=users)
        except ValidationError as error:
            return exception_handler(status_code=400, error=error.message)
        except Exception as error:
            return exception_handler(status_code=400, error=error)
