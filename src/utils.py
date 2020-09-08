import json
from typing import Literal


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
