
import json
import os
import sys
import time
import unittest
import uuid
from pprint import pprint

import boto3
import requests

sys.path.append("../..")  # Add application to path
sys.path.append("./layers/")  # Add layer to path

from shared import (
    generate_ttl,
    get_headers,
    HEADERS
)


class Tests(unittest.TestCase):
    """
    Example included to demonstrate how to run unit tests when using lambda layers.
    """

    def setUp(self):
        self.tableName = os.environ["TABLE_NAME"]
        self.dynamodb = boto3.client("dynamodb", endpoint_url="http://127.0.0.1:8000")

        self.event = json.loads("""{
              "body": "{\"client_id\": \"12345\"}",
              "resource": "/{proxy+}",
              "path": "/greetings",
              "httpMethod": "POST",
              "isBase64Encoded": false,
              "queryStringParameters": {},
              "pathParameters": {
                "proxy": "/path/to/resource"
              },
              "stageVariables": {
                "baz": "qux"
              },
              "headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, sdch",
                "Accept-Language": "en-US,en;q=0.8",
                "Cache-Control": "max-age=0",
                "CloudFront-Forwarded-Proto": "https",
                "CloudFront-Is-Desktop-Viewer": "true",
                "CloudFront-Is-Mobile-Viewer": "false",
                "CloudFront-Is-SmartTV-Viewer": "false",
                "CloudFront-Is-Tablet-Viewer": "false",
                "CloudFront-Viewer-Country": "US",
                "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Custom User Agent String",
                "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
                "X-Amz-Cf-Id": "cDehVQoZnx43VYQb9j2-nvCh-9z396Uhbp027Y2JvkCPNLmGJHqlaA==",
                "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
                "X-Forwarded-Port": "443",
                "X-Forwarded-Proto": "https"
              },
              "requestContext": {
                "accountId": "123456789012",
                "resourceId": "123456",
                "stage": "prod",
                "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
                "requestTime": "09/Apr/2015:12:34:56 +0000",
                "requestTimeEpoch": 1428582896000,
                "identity": {
                  "cognitoIdentityPoolId": null,
                  "accountId": null,
                  "cognitoIdentityId": null,
                  "caller": null,
                  "accessKey": null,
                  "sourceIp": "127.0.0.1",
                  "cognitoAuthenticationType": null,
                  "cognitoAuthenticationProvider": null,
                  "userArn": null,
                  "userAgent": "Custom User Agent String",
                  "user": null
                },
                "path": "/prod/path/to/resource",
                "resourcePath": "/{proxy+}",
                "httpMethod": "POST",
                "apiId": "1234567890",
                "protocol": "HTTP/1.1"
              }
            }""")

    def test_headers(self):
        self.assertEqual(self, HEADERS.get("Access-Control-Allow-Credentials"), True)

    def test_lambda_handler(self):
        """
        API Handler tester

        The API catch the request and builds a record in dynamodb
        for each request with sender's IP, build and id and timestamp

        """

        # Controls body
        try:
            request_payload = json.loads(self.event["body"])
        except KeyError or ValueError:
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
        ttl = str(generate_ttl(7))

        result = self.dynamodb.update_item(
            TableName=self.tableName,
            Key={
                "pk": {"S": pk},
                "sk": {"S": f"ip#{ip}"}
            },
            ExpressionAttributeNames={
                "#ip": "ip",
                "#ttl": "ttl",
                "#client_id": "client_id",
                "#timestamp": "timestamp"
            },
            ExpressionAttributeValues={
                ":ip": {"S": ip},
                ":ttl": {"N": ttl},
                ":client_id": {"S": client_id},
                ":timestamp": {"S": timestamp}
            },
            UpdateExpression="SET #ttl=:ttl, #client_id=:client_id, #timestamp=:timestamp",
            ReturnValues="ALL_NEW"
        )

        pprint(result)
        # metrics.add_metric(name="GreetingAdded", unit="Count", value=1)

        response = {
            "statusCode": 200,
            "headers": get_headers(pk),
            "body": json.dumps(
                {"client_id": client_id, "ip": ip, "message": "Greetings added !"}
            ),
        }

        pprint(response)

        self.assertEqual(response['statusCode'], 200)


if __name__ == "__main__":
    unittest.main()
