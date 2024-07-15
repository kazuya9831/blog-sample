#!/bin/bash

PATH=$PATH:$LAMBDA_TASK_ROOT/bin PYTHONPATH=$LAMBDA_TASK_ROOT:/opt/python exec python -m flask run --host=0.0.0.0 --port=8080
