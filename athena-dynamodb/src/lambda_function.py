import os
import time

import boto3

GLUE_DATABASE = os.environ.get("GLUE_DATABASE")
GLUE_TABLE = os.environ.get("GLUE_TABLE")
QUERY_OUTPUT_S3_BUCKET = os.environ.get("QUERY_OUTPUT_S3_BUCKET")

athena_client = boto3.client("athena")


def start_query_execution(query):
    query_execution_id = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": GLUE_DATABASE},
        ResultConfiguration={"OutputLocation": QUERY_OUTPUT_S3_BUCKET},
    )["QueryExecutionId"]

    return query_execution_id


def wait_query_execution(query_execution_id):
    while True:
        response = athena_client.get_query_execution(
            QueryExecutionId=query_execution_id
        )
        state = response["QueryExecution"]["Status"]["State"]
        if state != "QUEUED" and state != "RUNNING":
            return state
        time.sleep(3)


def lambda_handler(event, context):

    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    bucket_prefix = os.path.dirname(event["Records"][0]["s3"]["object"]["key"])
    print(f"s3://{bucket_name}/{bucket_prefix}")

    query = f"ALTER TABLE {GLUE_DATABASE}.{GLUE_TABLE} SET LOCATION 's3://{bucket_name}/{bucket_prefix}';"
    query_execution_id = start_query_execution(query)
    state = wait_query_execution(query_execution_id)
    print(f"""{state}: {query_execution_id}query: {query}""")
