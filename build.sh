#!/bin/sh

pip install -e .[test] &&
python setup.py test

if [ $? -ne 0 ]; then
  echo "UNIT TESTS FAILED"
  exit 1
fi

python setup.py install build bdist_wheel
