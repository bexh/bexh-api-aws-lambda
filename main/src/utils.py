import json
from typing import Literal
import functools
import boto3
import base64
from botocore.exceptions import ClientError
import os
from decimal import Decimal
from datetime import datetime


class Request:
    def __init__(self, event: dict):
        self.path = event['path']
        self.http_method = event['httpMethod']
        self.body = event['body']
        self.headers = event['headers'] if 'headers' in event else None
        self.query_str_params = event['queryStringParameters'] if 'queryStringParameters' in event else None


class Response:
    def __init__(self, body: dict, status_code: int):
        self.body = body
        self.status_code = status_code

    def serialize(self):
        return {
            'statusCode': self.status_code,
            'body': json.dumps(self.body)
        }


Method = Literal["POST", "PUT", "GET", "DELETE", "PATCH"]


class Route:
    def __init__(self, func, methods: [Method] = None):
        self.func = func
        self.methods = methods

    def valid_method(self, method: Method):
        """
        Checks if method is in set of methods or if methods was None
        allowing all methods
        :param method:
        :return:
        """
        if not self.methods or method in self.methods:
            return True
        return False


def singleton(cls):
    """Make a class a Singleton class (only one instance)"""

    @functools.wraps(cls)
    def wrapper_singleton(*args, **kwargs):
        if not wrapper_singleton.instance:
            wrapper_singleton.instance = cls(*args, **kwargs)
        return wrapper_singleton.instance

    wrapper_singleton.instance = None
    return wrapper_singleton


def get_secret(secret_name: str):
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
        endpoint_url=os.environ.get("ENDPOINT_URL", None)
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret


def dec_to_float(decimal, precision: int = 2) -> float:
    if type(decimal) != Decimal:
        return decimal
    return float(round(decimal, precision))


def first(df):
    first_entry = next(iter(df), None)
    return {} if type(first_entry) != dict else first_entry


def datetime_to_display_format(dt) -> str:
    def suffix(d):
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')

    def custom_strftime(format, t):
        return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

    return custom_strftime("%A, %B {S}, %I:%M %p", dt)


def iso_format(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def transform_event_dtm_to_date(event: dict) -> dict:
    date = iso_format(event['dtm'])
    event['date'] = date
    del event['dtm']
    return event

