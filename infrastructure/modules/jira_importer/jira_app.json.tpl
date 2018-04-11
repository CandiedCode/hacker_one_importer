[
  {
    "name": "jira-importer",
    "image": "${REPOSITORY_URL}:${DOCKER_TAG}",
    "networkMode": "awsvpc",
    "essential": true,
    "cpu": 256,
    "memory": 512,
    "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/jira-importer",
          "awslogs-region": "${AWS_REGION}",
          "awslogs-stream-prefix": "ecs"
        }
    },
    "environment": [
      {
          "name": "ENVIRONMENT",
          "value": "Production"
      }]
  }
]