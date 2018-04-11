import boto3


def handler(event,context):
  client = boto3.client('ecs')
  response = client.run_task(
  cluster='${ECS_CLUSTER}', # name of the cluster
  launchType = 'FARGATE',
  taskDefinition='${ECS_TASK_DEFINITION}',
  count = 1,
  platformVersion='LATEST',
  networkConfiguration={
        'awsvpcConfiguration': {
            'subnets': ['${PRIVATE_SUBNET}'],
            'securityGroups': ['${SECURITY_GROUP}'],
            'assignPublicIp': 'DISABLED'
        }
    })

  return str(response)
