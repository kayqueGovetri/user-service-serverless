from json import dumps

from aws_lambda_powertools.event_handler import Response


def exception_handler(status_code, error):
    body = {
        "status_code": status_code,
        "headers": {"Content-Type": "application/json"},
        "message": str(error),
    }
    return Response(
        status_code=status_code,
        content_type="application/json",
        body=dumps(body, default=str),
    )


def response_handler(body: dict, status_code=200):
    return Response(
        status_code=status_code, content_type="application/json", body=dumps(body)
    )
