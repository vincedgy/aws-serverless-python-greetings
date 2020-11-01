import calendar
import datetime
import os
from decimal import Decimal
from http.cookies import SimpleCookie

from aws_lambda_powertools import Tracer

tracer = Tracer()

HEADERS = {
    "Access-Control-Allow-Origin": os.environ.get("ALLOWED_ORIGIN"),
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Access-Control-Allow-Credentials": True,
}

@tracer.capture_method
def handle_decimal_type(obj):
    """
    json serializer which works with Decimal types returned from DynamoDB.
    """
    if isinstance(obj, Decimal):
        if float(obj).is_integer():
            return int(obj)
        else:
            return float(obj)
    raise TypeError


@tracer.capture_method
def generate_ttl(days=1):
    """
    Generate epoch timestamp for number days in future
    """
    future = datetime.datetime.utcnow() + datetime.timedelta(days=days)
    return calendar.timegm(future.utctimetuple())

@tracer.capture_method
def get_headers(clientId):
    """
    Get the headers to add to response data
    """
    headers = HEADERS
    cookie = SimpleCookie()
    cookie["greetingsId"] = clientId
    cookie["greetingsId"]["max-age"] = (60 * 60) * 24  # 1 day
    cookie["greetingsId"]["secure"] = True
    cookie["greetingsId"]["httponly"] = True
    cookie["greetingsId"]["samesite"] = "None"
    cookie["greetingsId"]["path"] = "/"
    headers["Set-Cookie"] = cookie["greetingsId"].OutputString()
    return headers