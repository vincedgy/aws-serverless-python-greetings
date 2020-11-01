import sys
import json
import requests
import datetime
import time
import uuid
import os
import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer

sys.path.append("..")  # Add application to path
sys.path.append("../layers")  # Add layer to path
from shared import (
    generate_ttl,
    get_headers,
)

logger = Logger()
tracer = Tracer()
metrics = Metrics()

tableName = os.environ["TABLE_NAME"]
if os.environ['ENV'] == 'dev':
    dynamodb = boto3.client("dynamodb", endpoint_url="http://dynamodb-local:8000")
else:
    dynamodb = boto3.client("dynamodb")


@metrics.log_metrics(capture_cold_start_metric=True)
@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    """
    API Handler

    The API catch the request and builds a record in dynamodb
    for each request with sender's IP, build and id and timestamp

    """
    logger.info(event)
    logger.info(f"Table is {tableName}")

    # Controls body
    try:
        request_payload = json.loads(event["body"])
    except:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "No Request payload"}),
        }

    # Controls payload : clientId is mandatory`
    client_id = ""
    try:
        client_id = request_payload["client_id"]
    except KeyError:
        return {
            "statusCode": 400,
            "headers": get_headers(client_id),
            "body": json.dumps({"message": "No client_id in payload ?"}),
        }
    # Build the record

    ip = requests.get("http://checkip.amazonaws.com/").text.replace("\n", "")
    pk = str(uuid.uuid4())
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    week = datetime.datetime.today() + datetime.timedelta(days=7)
    expiry_date_time = int(time.mktime(week.timetuple()))

    try:
        result = dynamodb.put_item(
            TableName=tableName,
            Item={
                'pk': {'S': pk},
                'sk': {'S': ip},
                'client_id': {'S': client_id},
                'timestamp': {'S': timestamp},
                'ttl': {'N': str(expiry_date_time)}
            })
        print(result)
    except Exception as e:
        logger.error(e)

    # result = table.update_item(
    #     Key={
    #         "pk": {"S": pk}
    #     },
    #     ExpressionAttributeValues={
    #         ":ip": {"S": ip},
    #         ":ttl": {"N": ttl},
    #         ":client_id": {"S": client_id},
    #         ":timestamp": {"S": timestamp}
    #     },
    #     UpdateExpression="SET sk=:ip, ttl=:ttl, client_id=:client_id, timestamp=:timestamp",
    #     ReturnValues="ALL_NEW"
    # )

    # metrics.add_metric(name="GreetingAdded", unit="Count", value=1)


    return {
        "statusCode": 200,
        "headers": get_headers(pk),
        "body": json.dumps(
            {"client_id": client_id, "ip": ip, "message": "Greetings added !"}
        ),
    }
