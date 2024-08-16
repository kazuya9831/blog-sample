import os
import uuid

import boto3
from boto3.dynamodb.types import TypeDeserializer

TABLE_NAME = os.environ.get("TODO_TABLE")
dynamodb_client = boto3.client("dynamodb")


def dynamo_to_python(dynamo_object):
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamo_object.items()}


def get_item(args):
    if not args.get("todo_id"):
        return {}

    todo_id = args.get("todo_id")

    item = dynamodb_client.get_item(
        TableName=TABLE_NAME, Key={"TodoID": {"S": todo_id}}
    )["Item"]

    return dynamo_to_python(item)


def scan_items():
    items = []
    response = dynamodb_client.scan(TableName=TABLE_NAME)
    for dynamo_object in response["Items"]:
        items.append(dynamo_to_python(dynamo_object))

    return items


def put_item(form):
    todo_id = str(uuid.uuid4())
    title = form["title"]
    detail = form["detail"]
    status = form["status"]

    dynamodb_client.put_item(
        TableName=TABLE_NAME,
        Item={
            "TodoID": {"S": todo_id},
            "Title": {"S": title},
            "Detail": {"S": detail},
            "TodoStatus": {"S": status},
        },
    )


def update_item(form):
    todo_id = form["todo_id"]
    title = form["title"]
    detail = form["detail"]
    status = form["status"]

    dynamodb_client.update_item(
        TableName=TABLE_NAME,
        Key={"TodoID": {"S": todo_id}},
        UpdateExpression="SET Title=:title, Detail=:detail, TodoStatus=:satus",
        ExpressionAttributeValues={
            ":title": {"S": title},
            ":detail": {"S": detail},
            ":satus": {"S": status},
        },
    )


def delete_item(todo_id):
    dynamodb_client.delete_item(TableName=TABLE_NAME, Key={"TodoID": {"S": todo_id}})
