#!/bin/bash

PATH=$PATH:$LAMBDA_TASK_ROOT/bin \
    PYTHONPATH=$LAMBDA_TASK_ROOT:/opt/python \
    exec python -m gunicorn -b=:8080 -w=1 views:app
