#!/bin/bash


## テーブルの削除
echo "テーブルの削除を開始します"
aws rds-data execute-statement \
--resource-arn "${RESOURCE_ARN}" \
--database "${DATABASE_NAME}" \
--secret-arn "${ADMIN_SECRET_ARN}" \
--region "${REGION}" \
--sql "DROP TABLE bedrock_integration.bedrock_kb;"

## スキーマの削除
echo "スキーマの削除を開始します"
aws rds-data execute-statement \
--resource-arn "${RESOURCE_ARN}" \
--database "${DATABASE_NAME}" \
--secret-arn "${ADMIN_SECRET_ARN}" \
--region "${REGION}" \
--sql "DROP SCHEMA bedrock_integration;"

## ロール(ユーザー)の削除
echo "ロール(ユーザー)の削除を開始します"
aws rds-data execute-statement \
--resource-arn "${RESOURCE_ARN}" \
--database "${DATABASE_NAME}" \
--secret-arn "${ADMIN_SECRET_ARN}" \
--region "${REGION}" \
--sql "DROP ROLE bedrock_user;"

## pgvectorの削除
echo "pgvectorの削除を開始します"
aws rds-data execute-statement \
--resource-arn "${RESOURCE_ARN}" \
--database "${DATABASE_NAME}" \
--secret-arn "${ADMIN_SECRET_ARN}" \
--region "${REGION}" \
--sql "DROP EXTENSION vector;"

