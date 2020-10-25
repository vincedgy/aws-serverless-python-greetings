import json
import requests
import os
import time
import uuid

# Initialize dynamoDB client for the given table from parameters
import boto3
dynamodb = boto3.resource('dynamodb')
tableName = os.getenv('GREETING_TABLE')
table = dynamodb.Table(tableName)

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

        table.put_item(
            Item=record
        )
    except:
        print(f"Impossible to put item into table {tableName}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": f"Impossible to put item into table {tableName}"
            }),
        }

    # Finally send back a message
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"hello world saved into table {tableName}",
            "location": ip.text.replace("\n", "")
        }),
    }
