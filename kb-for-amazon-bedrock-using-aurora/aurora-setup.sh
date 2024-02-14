#!/bin/bash

## pgvectorのセットアップ
echo "pgvectorのセットアップを開始します"
aws rds-data execute-statement \
--resource-arn "${RESOURCE_ARN}" \
--database "${DATABASE_NAME}" \
--secret-arn "${ADMIN_SECRET_ARN}" \
--region "${REGION}" \
--sql "CREATE EXTENSION IF NOT EXISTS vector;"

## スキーマの作成
echo "スキーマの作成を開始します"
aws rds-data execute-statement \
--resource-arn "${RESOURCE_ARN}" \
--database "${DATABASE_NAME}" \
--secret-arn "${ADMIN_SECRET_ARN}" \
--region "${REGION}" \
--sql "CREATE SCHEMA bedrock_integration;"

## テーブル作成
echo "テーブルの作成を開始します"
aws rds-data execute-statement \
--resource-arn "${RESOURCE_ARN}" \
--database "${DATABASE_NAME}" \
--secret-arn "${ADMIN_SECRET_ARN}" \
--region "${REGION}" \
--sql "CREATE TABLE bedrock_integration.bedrock_kb (id uuid PRIMARY KEY, embedding vector(1536), chunks text, metadata json);"

## インデックスの作成
echo "インデックスの作成を開始します"
aws rds-data execute-statement \
--resource-arn "${RESOURCE_ARN}" \
--database "${DATABASE_NAME}" \
--secret-arn "${ADMIN_SECRET_ARN}" \
--region "${REGION}" \
--sql "CREATE INDEX on bedrock_integration.bedrock_kb USING hnsw (embedding vector_cosine_ops);"

## ロール(ユーザー)の作成
echo "ロール(ユーザー)の作成を開始します"
aws rds-data execute-statement \
--resource-arn "${RESOURCE_ARN}" \
--database "${DATABASE_NAME}" \
--secret-arn "${ADMIN_SECRET_ARN}" \
--region "${REGION}" \
--sql "CREATE ROLE bedrock_user WITH PASSWORD 'P@ssword123' LOGIN;"

## 権限設定
### スキーマに対する権限を付与
echo "スキーマに対する権限を付与します"
aws rds-data execute-statement \
--resource-arn "${RESOURCE_ARN}" \
--database "${DATABASE_NAME}" \
--secret-arn "${ADMIN_SECRET_ARN}" \
--region "${REGION}" \
--sql "GRANT ALL ON SCHEMA bedrock_integration to bedrock_user;"

### テーブルに対する権限を付与
echo "テーブルに対する権限を付与します"
aws rds-data execute-statement \
--resource-arn "${RESOURCE_ARN}" \
--database "${DATABASE_NAME}" \
--secret-arn "${ADMIN_SECRET_ARN}" \
--region "${REGION}" \
--sql "GRANT ALL ON TABLE bedrock_integration.bedrock_kb TO bedrock_user;"


