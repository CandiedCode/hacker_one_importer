import logging
import os
from datetime import datetime, timedelta, timezone

import boto3

logger = logging.getLogger()


class Config:
    _singleton = None

    Environment = 'Development'
    TABLE_NAME = 'JiraImporter'
    AWS_DEFAULT_REGION = 'us-east-1'
    DYNAMODB_ENDPOINT_URL = 'http://dynamodb:8000'
    H1_API_IDENTIFIER = 'candiedcode_jira'
    H1_PROGRAM = 'candiedcode_v2'
    JIRA_SERVER = 'https://jira2.candiedcode.com'
    JIRA_PROJECT = 'HT'
    MIN_START_DATETIME = datetime.now(timezone.utc) - timedelta(days=180)
    MAX_WORKER = 4

    def __init__(self):
        self.TOKEN = self.get_secret('TOKEN')
        self.USERNAME = self.get_secret('USERNAME')
        self.PASSWORD = self.get_secret('PASSWORD')

    def __new__(cls, *args, **kwargs):
        if not cls._singleton:
            cls._singleton = object.__new__(cls)
        return cls._singleton

    @staticmethod
    def get_secret(param):
        secret = os.getenv(param)

        if secret is None:
            ssm = boto3.client('ssm')

            response = ssm.get_parameters(
                Names=[param],
                WithDecryption=True
            )

            if len(response['InvalidParameters']) > 0:
                logger.info("failed finding parameter in ssm")
            else:
                secret = response['Parameters'][0]['Value']

        return secret


class DevelopmentConfig(Config):
    pass


class ProductionConfig(Config):
    DYNAMODB_ENDPOINT_URL = 'https://dynamodb.us-east-1.amazonaws.com'
    Environment = 'Production'


def get_config():
    environment = os.getenv('ENVIRONMENT', 'development')

    if environment == 'development':
        return DevelopmentConfig()
    else:
        return ProductionConfig()
