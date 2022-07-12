import boto3

from typing import Dict
from boto3.dynamodb.conditions import Attr, Or


class Dynamodb:
    def __init__(
            self, environment: str, region: str, table_name: str, aws_key="", aws_secret=""
    ):
        self.environment = environment
        self.region = region
        self.table_name = table_name
        self.table = None
        self.aws_key = aws_key
        self.aws_secret = aws_secret
        self.get_table()
        self.client = self.__get_client()

    def __get_client(self):
        if self.aws_secret and self.aws_key:
            return boto3.client('dynamodb',
                                region_name=self.region,
                aws_access_key_id=self.aws_key,
                aws_secret_access_key=self.aws_secret,)

    def scan(self, filter_expression):
        response = self.table.scan(FilterExpression=filter_expression)
        data = response.get("Items")
        while "LastEvaluatedKey" in response:
            response = self.table.scan(
                ExclusiveStartKey=response["LastEvaluatedKey"],
                FilterExpression=filter_expression,
            )
            data.extend(response["Items"])
        data = {"Items": data}
        return data

    def update(
            self,
            key: Dict,
            update_expression: str,
            expression_attribute_names: Dict,
            expression_attribute_values: Dict,
    ):
        response = self.table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW",
        )
        return response

    def create(self, item):
        response = self.table.put_item(Item=item, ReturnValues="ALL_OLD")
        return response

    def create_batch(self, items):
        if not isinstance(items, list):
            raise ValueError(f"O paramêtro itens não é uma lista. Itens: {items}'")
        with self.table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)

    def get_table(self):
        if self.environment == "AWS_SAM_LOCAL":
            dynamodb_table = boto3.resource(
                "dynamodb", endpoint_url="http://localhost:8000"
            )
        elif self.aws_key and self.aws_secret:
            dynamodb_table = boto3.resource(
                "dynamodb",
                region_name=self.region,
                aws_access_key_id=self.aws_key,
                aws_secret_access_key=self.aws_secret,
            )
        else:
            dynamodb_table = boto3.resource("dynamodb", region_name=self.region)

        self.table = dynamodb_table.Table(self.table_name)

    def query(self, **kwargs):
        """

        :param kwargs: Includes {
            KeyConditionExpression: The condition(s) a key(s) must meet.
            FilterExpression: The condition(s) an attribute(s) must meet.
            ConsistentRead: Determines the read consistency model: If set to true , then the operation uses strongly
                consistent reads; otherwise, the operation uses eventually consistent reads
            Limit: The maximum number of items to evaluate
            IndexName: The name of an index to query
            ExclusiveStartKey:  The primary key of the first item that this operation will evaluate. Use the value that
            was returned for LastEvaluatedKey in the previous operation.
            ReturnConsumedCapacity: Determines the level of detail about either provisioned or on-demand
            throughput consumption that is returned in the response:
            ProjectionExpression: string that identifies one or more attributes to retrieve from the table.
        }
        :return:
        """
        response = self.table.query(**kwargs)
        return response

    @staticmethod
    def create_batch_is_in(field_name: str, items, batch_size=100) -> Or:
        """
        :param items: Lista de itens para a criação da query
        :param field_name: Nome do campo pra ser utilizado no is_in
        :param batch_size: Tamanho do batch
        :return:
        """
        if not isinstance(batch_size, int):
            raise ValueError("O tipo do tamanho do lote tem que ser inteiro.")

        if batch_size < 1 or batch_size > 100:
            raise ValueError("Erro no tamanho do lote. Tem que ser um valor entre 0 e 100.")

        batches = [items[i: i + batch_size] for i in range(0, len(items), batch_size)]
        batches_is_in = Attr(field_name).is_in(batches[0])
        for b in batches[1:]:
            batches_is_in = batches_is_in | Attr(field_name).is_in(b)

        return batches_is_in
