import json
import requests
import os
import time
import uuid
import boto3

# Get environment variables
table_name = os.environ['TABLE']
region = os.environ['REGION']
aws_environment = os.environ['AWSENV']
dev_environment = os.environ['DEVENV']


def getTable():
    """Returns table dynamoDb object (boto3) depending of the given environment"""

    # Check if executing locally or on AWS, and configure DynamoDB connection accordingly.
    if aws_environment == "AWS_SAM_LOCAL":
        # SAM LOCAL
        if dev_environment == "OSX":
            # Environment ins Mac OSX
            table = boto3.resource('dynamodb', endpoint_url="http://docker.for.mac.localhost:8000/").Table(
                table_name)
        elif dev_environment == "Windows":
            # Environment is Windows
            table = boto3.resource('dynamodb', endpoint_url="http://docker.for.windows.localhost:8000/").Table(
                table_name)
        else:
            # Environment is Linux
            table = boto3.resource('dynamodb', endpoint_url="http://127.0.0.1:8000").Table(table_name)
    else:
        # AWS
        table = boto3.resource('dynamodb', region_name=region).Table(table_name)

    return table


def lambda_handler(event, context):
    # Gets IP
    try:
        ip = requests.get("http://checkip.amazonaws.com/")
    except requests.RequestException as e:
        # Send some context about this error to Lambda Logs
        print(e)
        raise e

    # Put item into DynamoDB table
    try:
        record = {
            'id': str(uuid.uuid4()),
            'ip': ip.text.replace("\n", ""),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        print(f"Putting record {record}")

        getTable().put_item(
            Item=record
        )
    except:
        print(f"Impossible to put item into table {table_name}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": f"Impossible to put item into table {table_name}"
            }),
        }

    # Finally send back a message
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"hello world saved into table {table_name}",
            "location": ip.text.replace("\n", "")
        }),
    }
