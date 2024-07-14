#!/bin/bash

RESOURCE_ARN=$(aws cloudformation describe-stacks \
    --stack-name "image-search" \
    --query "Stacks[].Outputs[?OutputKey=='AuroraResourceARN'].OutputValue" \
    --output text
)
ADMIN_SECRET_ARN=$(aws cloudformation describe-stacks \
    --stack-name "image-search" \
    --query "Stacks[].Outputs[?OutputKey=='AuroraAdminUserSecretArn'].OutputValue" \
    --output text
)

DATABASE_NAME="images"
REGION="ap-northeast-1"

SQL_COMMAND_BASE="aws rds-data execute-statement \
--resource-arn ${RESOURCE_ARN} \
--database ${DATABASE_NAME} \
--secret-arn ${ADMIN_SECRET_ARN} \
--region ${REGION}"

## pgvectorのセットアップ
echo "pgvectorのセットアップを開始します"
eval "${SQL_COMMAND_BASE} \
--sql 'CREATE EXTENSION IF NOT EXISTS vector;'"

## スキーマの作成
echo "スキーマの作成を開始します"
eval "${SQL_COMMAND_BASE} \
--sql 'CREATE SCHEMA bedrock_integration;'"

## テーブル作成
echo "テーブルの作成を開始します"
eval "${SQL_COMMAND_BASE} \
--sql 'CREATE TABLE bedrock_integration.bedrock_kb (id uuid PRIMARY KEY, embedding vector(1024), title text, image_path text);'"

## インデックスの作成
echo "インデックスの作成を開始します"
eval "${SQL_COMMAND_BASE} \
--sql 'CREATE INDEX on bedrock_integration.bedrock_kb USING hnsw (embedding vector_cosine_ops);'"

## ロール(ユーザー)の作成
echo "ロール(ユーザー)の作成を開始します"
${SQL_COMMAND_BASE} --sql "CREATE ROLE bedrock_user WITH PASSWORD 'P@ssword123' LOGIN;"

## 権限設定
### スキーマに対する権限を付与
echo "スキーマに対する権限を付与します"
eval "${SQL_COMMAND_BASE} \
--sql 'GRANT ALL ON SCHEMA bedrock_integration to bedrock_user;'"

### テーブルに対する権限を付与
echo "テーブルに対する権限を付与します"
eval "${SQL_COMMAND_BASE} \
--sql 'GRANT ALL ON TABLE bedrock_integration.bedrock_kb TO bedrock_user;'"

