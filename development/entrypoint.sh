#!/bin/sh
set -e

pip install -e .[dev,test]
python setup.py develop build bdist_wheel install
python hacker_one_importer/dynamodb.py > /dev/null 2>&1


exec "$@"