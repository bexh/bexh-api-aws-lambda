import boto3
from botocore.exceptions import ClientError
import pymysql

from src.utils import Request, Response


def login_required(f):
    """
    Decorator to require user to have token and user in header
    :return: boolean for if they are logged in
    """
    def wrap(request: Request):
        if (not request.headers or 'token' not in request.headers
                or 'user' not in request.headers):
            return Response(body={"error": "Not authorized"}, status_code=403)

        user = request.headers['user']
        token = request.headers['token']
        dynamo = DynamoDb()
        verified_session = dynamo.check_token(user, token)
        if verified_session:
            return f(request)
        return Response(body={"error": "Not authorized"}, status_code=403)
    return wrap


class DynamoDb:
    # TODO: dependency injection on local vs aws
    db = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")

    def check_token(self, user: str, token: str) -> bool:
        """
        Checks dynamo to see if user exists in keys and if token matches
        :param user: username
        :param token: generated token on login
        :return: bool of whether the token matches
        """
        table = self.db.Table('Tokens')
        try:
            response = table.get_item(Key={'User': user})
        except ClientError as e:
            return False
        else:
            item = response['Item']
            # check if token matches
            if item['Token'] != token:
                return False
            return True


class MySql:
    def __init__(self):
        # TODO: dependency injection and best practice w credentials
        self.host = "127.0.0.1"
        self.user = "user"
        self.password = "password"
        self.db = "db"

    def __connect__(self):
        self.con = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            db=self.db,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cur = self.con.cursor()

    def __disconnect__(self):
        self.con.close()

    def fetch(self, sql):
        self.__connect__()
        self.cur.execute(sql)
        result = self.cur.fetchall()
        self.__disconnect__()
        return result

    def execute(self, sql):
        self.__connect__()
        self.cur.execute(sql)
        self.con.commit()
        self.__disconnect__()
