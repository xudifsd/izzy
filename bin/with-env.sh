#!/bin/bash

cd `dirname $0`/..
HOME=`pwd`

for i in `find lib -type f` ; do
    PYTHONPATH=${PYTHONPATH}:${i}
done
PYTHONPATH=${PYTHONPATH}:src:py_gen:lib

export PYTHONPATH

export FLASK_APP=src/web.py

exec $@
