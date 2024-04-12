import csv
import sys

import boto3

client = boto3.client("cognito-idp")

GROUP_LIST = ["admin", "general"]


class Cognito:
    def __init__(self, user_pool_id):
        self.user_pool_id = user_pool_id

    def is_group_exist(self, group_name):
        """グループが存在するか確認する関数"""
        response = client.list_groups(
            UserPoolId=self.user_pool_id,
        )

        if group_name in response["Groups"]:
            return True

        return False

    def create_group(self, group_name):
        """グループを作成する関数"""
        try:
            client.create_group(
                UserPoolId=self.user_pool_id,
                GroupName=group_name,
            )
            print(f"Group {group_name} created")
        except client.exceptions.GroupExistsException:
            print(f"Group {group_name} already exists")

    def create_user(self, user_name):
        """ユーザーを作成する関数"""
        try:
            client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=user_name,
                # UserAttributes=[
                #     {
                #         "Name": "email",
                #         "Value": user_name,
                #     },
                #     {
                #         "Name": "email_verified",
                #         "Value": "true",
                #     },
                # ],
                MessageAction="SUPPRESS",
            )
            print(f"User {user_name} created")

        except client.exceptions.UsernameExistsException:
            print(f"User {user_name} already exists")

    def set_user_password(self, user_name):
        """ユーザーのパスワードを設定する関数"""
        client.admin_set_user_password(
            UserPoolId=self.user_pool_id,
            Username=user_name,
            Password=user_name,
        )

    def add_user_to_group(self, user_name, group_name):
        """ユーザーをグループに追加する関数"""
        client.admin_add_user_to_group(
            UserPoolId=self.user_pool_id,
            Username=user_name,
            GroupName=group_name,
        )


def main(user_pool_id, user_list_file):
    """メイン関数"""

    cognito = Cognito(user_pool_id)

    for group_name in GROUP_LIST:
        if not cognito.is_group_exist(group_name):
            cognito.create_group(group_name)

    with open(user_list_file, "r") as f:
        csv_reader = csv.reader(f)
        for i, row in enumerate(csv_reader, start=1):
            user_name = row[0].strip()
            group_name = row[1].strip()
            print(f"{i} {user_name} {group_name}")
            cognito.create_user(user_name)

            try:
                cognito.set_user_password(user_name)
                print(f"User {user_name} password set")
                cognito.add_user_to_group(user_name, group_name)
                print(f"User {user_name} added to group {group_name}")
            except Exception as e:
                print(e)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            f"""
Usage:
    {sys.argv[0]} [CognitoのユーザープールID] [ユーザーリストファイル]

Example:
    {sys.argv[0]} ap-northeast-1_xxxxxx cognito_user_and_group.csv
"""
        )

        sys.exit(1)

    user_pool_id = sys.argv[1]
    user_list_file = sys.argv[2]
    main(user_pool_id, user_list_file)
