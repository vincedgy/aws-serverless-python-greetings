import json
import boto3
import os

from aws_lambda_powertools import Metrics, Logger, Tracer

logger = Logger()
tracer = Tracer()
metrics = Metrics()

tableName = os.environ["TABLE_NAME"]
if os.environ['ENV'] == 'dev':
    dynamodb = boto3.client("dynamodb", endpoint_url="http://127.0.0.1:8000")
else:
    dynamodb = boto3.client("dynamodb")

@metrics.log_metrics(capture_cold_start_metric=True)
@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    """
    API Handler

    The API catch the request and sends record from dynamodb

    """
    logger.info(event)
    logger.info(f"Table is {tableName}")

    # Finally send back a message
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"comming soon"
        }),
    }
