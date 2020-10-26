import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import pymysql
import os
import json
import datetime
import time

from main.src.utils import Request, Response, get_secret


def login_required(f):
    """
    Decorator to require user to have token and user in header
    :return: boolean for if they are logged in
    """
    def wrap(request: Request):
        if (not request.headers or 'token' not in request.headers
                or 'uid' not in request.headers):
            return Response(body={"error": "Not authorized"}, status_code=403)

        uid = request.headers['uid']
        token = request.headers['token']
        dynamo = DynamoDb()
        verified_session = dynamo.check_token(uid=uid, token=token)
        if verified_session:
            return f(request)
        return Response(body={"error": "Not authorized"}, status_code=403)
    return wrap


class DynamoDb:
    def __init__(self):
        self.db = boto3.resource('dynamodb', endpoint_url=os.environ.get("ENDPOINT_URL", None))
        self.token_table_name = os.environ["TOKEN_TABLE_NAME"]

    def check_token(self, uid: int, token: str) -> bool:
        """
        Checks dynamo to see if user exists in keys and if token matches
        :param uid: user id
        :param token: generated token on login
        :return: bool of whether the token matches
        """
        table = self.db.Table(self.token_table_name)
        epoch_time_now = int(time.time())
        try:
            response = table.query(
                KeyConditionExpression=Key('Uid').eq(uid),
                FilterExpression=Key('TimeToLive').gt(str(epoch_time_now))
            )
            if len(response.get('Items', [])) > 0 and response['Items'][0]['Token'] == token:
                return True
            return False
        except ClientError as e:
            return False

    def insert_token(self, uid: int, token: str):
        """
        Insert new token into dynamo table
        :param uid: user id
        :param token: token for session
        """
        table = self.db.Table(self.token_table_name)
        ttl = datetime.datetime.today() + datetime.timedelta(minutes=30)
        expiry_datetime = int(time.mktime(ttl.timetuple()))

        try:
            table.put_item(
                Item={
                    'Uid': uid,
                    'Token': token,
                    'TimeToLive': str(expiry_datetime)
                }
            )
        except Exception as e:
            print(e)


class MySql:
    def __init__(self):
        self.host = os.environ.get('MYSQL_HOST_URL')
        self.db = os.environ.get('MYSQL_DATABASE_NAME')
        creds = json.loads(get_secret("db-creds"))
        self.user = creds['username']
        self.password = creds['password']

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

    def multi_execute(self, sql: [str]):
        self.__connect__()
        statements = sql.split(";")[:-1]
        results = []
        for statement in statements:
            self.cur.execute(statement)
            self.con.commit()
            results.append(self.cur.fetchall())
        self.__disconnect__()
        return results
