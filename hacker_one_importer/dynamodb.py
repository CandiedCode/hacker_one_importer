import logging

import boto3
from botocore.exceptions import ClientError

from hacker_one_importer.config import get_config

logger = logging.getLogger()

config = get_config()

dynamodb = boto3.resource('dynamodb', endpoint_url=config.DYNAMODB_ENDPOINT_URL)
table = dynamodb.Table(config.TABLE_NAME)


def create_table():
    try:
        logger.info("Creating DynamoDB table %s at %s" % (config.TABLE_NAME, config.DYNAMODB_ENDPOINT_URL))

        # Create the DynamoDB table.
        table = dynamodb.create_table(
            TableName=config.TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'Project',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'Project',
                    'AttributeType': 'S'
                }

            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        # Wait until the table exists.
        table.meta.client.get_waiter('table_exists').wait(TableName=config.TABLE_NAME)
    except Exception as e:
        logger.warning(e)


def delete_table():
    try:
        logger.info("Deleting DynamoDB table %s at %s" % (config.TABLE_NAME, config.DYNAMODB_ENDPOINT_URL))
        table.delete()

        # Wait until the table exists.
        table.meta.client.get_waiter('table_not_exists').wait(TableName=config.TABLE_NAME)
    except Exception as e:
        print(str(e))


def put_last_activity_date(last_activity_date):
    response = table.put_item(
        Item={
            'Project': config.JIRA_PROJECT,
            'info': {
                'LastActivityDate': last_activity_date.isoformat(),
            }
        }
    )

    return response


def get_last_activity_date():
    try:
        response = table.get_item(
            Key={
                'Project': config.JIRA_PROJECT,
            }
        )
    except ClientError as e:
        raise e
    else:
        logging.debug("Getting the LastActivityDate from dynamodb")
        if 'Item' in response:
            return response['Item']['info']['LastActivityDate']


if __name__ == "__main__":
    # delete_table()
    print(config.DYNAMODB_ENDPOINT_URL)
    create_table()
    # day_ago = datetime.now(timezone.utc) - timedelta(days=30)
    # print(day_ago)
    # put_last_activity_date(day_ago)
    # item = get_last_activity_date()
    # print(item)
