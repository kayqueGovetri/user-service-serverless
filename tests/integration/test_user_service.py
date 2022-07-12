import os

import boto3
import pytest

from moto import mock_cloudformation


@pytest.fixture(autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture()
def stack_name():
    yield "LoginServiceFunction"


@mock_cloudformation
@pytest.fixture()
def client_cloud_formation(stack_name):
    cloud_formation = boto3.client("cloudformation", region_name="us-east-2")
    cloud_formation.create_stack(
        StackName=stack_name
    )
    yield cloud_formation


@pytest.fixture()
def describe_stacks(stack_name, client_cloud_formation):
    yield client_cloud_formation.describe_stacks(StackName=stack_name)


@pytest.fixture()
def api_endpoint(describe_stacks):
    stacks = describe_stacks["Stacks"]

    stack_outputs = stacks[0]["Outputs"]
    api_outputs = [output for output in stack_outputs if output["OutputKey"] == "HelloWorldApi"]
    yield api_outputs


def test_example(describe_stacks):
    print(describe_stacks)