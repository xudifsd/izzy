#!/bin/bash

PYTHONPATH="$PYTHONPATH:src:py_gen"

export PYTHONPATH

has_error=0

for i in `find test -type f -regex ".*py"` ;
do
    python $i
    last_error=$?
    if [ $has_error -eq 0 ] ; then
        has_error=$last_error
    fi
done

exit $has_error
