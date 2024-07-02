import json


def lambda_handler(event, context):

    print(f'LambdaがSQSから読み取ったデータ: {json.dumps(event)}')

    for i in event["Records"]:
        print(f'SQSに送信されたメッセージ: {i["body"]}')

    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}

