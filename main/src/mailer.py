import boto3
import os
from json import dumps


class Mailer:
    def __init__(self):
        self.client = boto3.client('sns', endpoint_url=os.environ.get("ENDPOINT_URL", None))

    def send_verification_email(self, email: str, first_name: str, uid: int, token: str):
        message = {
            'email': email,
            'first_name': first_name,
            'uid': uid,
            'token': token
        }

        topic_arn = os.environ.get('VERIFICATION_EMAIL_SNS_TOPIC_ARN')
        self.client.publish(
            TargetArn=topic_arn,
            Message=dumps(message)
        )

    def send_social_bet_accepted_email(self, payload: dict):
        topic_arn = os.environ.get('BET_STATUS_CHANGE_EMAIL_SNS_TOPIC_ARN')
        self.client.publish(
            TargetArn=topic_arn,
            Message=dumps(payload),
            Subject="BET_ACCEPTED"
        )

    def send_social_bet_declined_email(self, payload: dict):
        topic_arn = os.environ.get('BET_STATUS_CHANGE_EMAIL_SNS_TOPIC_ARN')
        self.client.publish(
            TargetArn=topic_arn,
            Message=dumps(payload),
            Subject="BET_ACCEPTED"
        )
