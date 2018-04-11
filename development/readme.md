# run unit tests
docker-compose run importer python -m pytest


aws dynamodb list-tables --endpoint-url http://localhost:8000