#!/bin/sh
set -e

pip install -e .[dev,test]
python setup.py develop build bdist_wheel install


exec "$@"