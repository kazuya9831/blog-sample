#!/bin/bash

set -e  # エラーが発生したらスクリプトを停止

ENV_FILE="./.env"

MAIN_REGION="ap-northeast-1"
MAIN_STACK_NAME="GenerativeAiUseCasesStack"
RAG_STACK_NAME=RagKnowledgeBaseStack

USER_POOL_ID=$(aws cloudformation describe-stacks \
    --stack-name "${MAIN_STACK_NAME}" \
    --query "Stacks[].Outputs[?OutputKey=='UserPoolId'].[OutputValue]" \
    --output text \
    --region ${MAIN_REGION}
)
echo "VITE_APP_AUTH_USER_POOL_ID=${USER_POOL_ID}" > $ENV_FILE

USER_POOL_CLIENT_ID=$(aws cloudformation describe-stacks \
    --stack-name "${MAIN_STACK_NAME}" \
    --query "Stacks[].Outputs[?OutputKey=='UserPoolClientId'].[OutputValue]" \
    --output text \
    --region ${MAIN_REGION}
)
echo "VITE_APP_AUTH_USER_POOL_CLIENT_ID=${USER_POOL_CLIENT_ID}" >> $ENV_FILE

ID_POOL_ID=$(aws cloudformation describe-stacks \
    --stack-name "${MAIN_STACK_NAME}" \
    --query "Stacks[].Outputs[?OutputKey=='IdPoolId'].[OutputValue]" \
    --output text \
    --region ${MAIN_REGION}
)
echo "VITE_APP_AUTH_IDENTITY_POOL_ID=${ID_POOL_ID}" >> $ENV_FILE


RAG_REGION=$(aws cloudformation describe-stacks \
    --stack-name "${MAIN_STACK_NAME}" \
    --query "Stacks[].Outputs[?OutputKey=='ModelRegion'].[OutputValue]" \
    --output text \
    --region ${MAIN_REGION}
)

echo "VITE_APP_STORAGE_AWS_REGION=${RAG_REGION}" >> $ENV_FILE

KNOWLEDGE_BASE_ID=$(aws cloudformation describe-stack-resources \
    --stack-name ${RAG_STACK_NAME} \
    --logical-resource-id KnowledgeBase \
    --query "StackResources[].PhysicalResourceId" \
    --output text \
    --region "${RAG_REGION}"
)

DATA_SOURCE_ID=$(aws bedrock-agent list-data-sources \
    --knowledge-base-id "${KNOWLEDGE_BASE_ID}" \
    --query "dataSourceSummaries[].dataSourceId" \
    --output text \
    --region "${RAG_REGION}"
)

STORAGE_BUCKET_NAME=$(aws bedrock-agent get-data-source \
    --data-source-id "${DATA_SOURCE_ID}" \
    --knowledge-base-id "${KNOWLEDGE_BASE_ID}" \
    --query "dataSource.dataSourceConfiguration.s3Configuration.bucketArn" \
    --output text \
    --region "${RAG_REGION}" \
    | awk -F: '{print $NF}'
)

echo "VITE_APP_STORAGE_BUCKET_NAME=${STORAGE_BUCKET_NAME}" >> $ENV_FILE
