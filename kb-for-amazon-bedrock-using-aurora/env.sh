#!/bin/bash

##-------------------------------------
## 変数の設定
##-------------------------------------

export STACK_NAME=test-kb-using-aurora
export KNOWLEDGE_BASE_NAME=test-knowledge-base
export DATA_SOURCE_NAME=test-knowledge-base-data-source
export REGION=us-west-2
export EMBEDDING_MODEL_ARN="arn:aws:bedrock:${REGION}::foundation-model/amazon.titan-embed-text-v1"
export TEXT_MODEL_ARN="arn:aws:bedrock:${REGION}::foundation-model/anthropic.claude-v2:1"
export DATABASE_NAME="rag"
export TABLE_NAME="bedrock_integration.bedrock_kb"

## CloudFormationのスタックが存在する場合、処理を続行
check=$(aws cloudformation describe-stacks --region "${REGION}" | grep -wc ${STACK_NAME})
if [[ $check -eq 0 ]]; then
    return 1
fi

export RESOURCE_ARN=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --query "Stacks[].Outputs[?OutputKey=='TestAuroraClusterArn'].OutputValue" \
    --output text --region "${REGION}")

export ADMIN_SECRET_ARN=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --query "Stacks[].Outputs[?OutputKey=='TestAuroraAdminUserSecretArn'].OutputValue" \
    --output text --region "${REGION}")

export BEDROCK_SECRET_ARN=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --query "Stacks[].Outputs[?OutputKey=='TestAuroraBedrockUserSecretArn'].OutputValue" \
    --output text --region "${REGION}")

export ROLE_ARN=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --query "Stacks[].Outputs[?OutputKey=='TestIAMRoleForKnowledgeBase'].OutputValue" \
    --output text --region "${REGION}")

export S3_FOR_KNOWLEDGE_BASE_DATA_SOURCE=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --query "Stacks[].Outputs[?OutputKey=='TestS3Bucket'].OutputValue" \
    --output text --region "${REGION}")

## ナレッジベースが存在する場合、処理を続行
check=$(aws bedrock-agent list-knowledge-bases --region ${REGION} | grep -wc ${KNOWLEDGE_BASE_NAME})
if [[ $check -eq 0 ]]; then
    return 1
fi

export KNOWLEDGE_BASE_ID=$(aws bedrock-agent list-knowledge-bases \
    --query "knowledgeBaseSummaries[?name=='${KNOWLEDGE_BASE_NAME}'].knowledgeBaseId" \
    --output text \
    --region ${REGION})

export DATA_SOURCE_ID=$(aws bedrock-agent list-data-sources \
    --knowledge-base-id "${KNOWLEDGE_BASE_ID}" \
    --query "dataSourceSummaries[?name=='${DATA_SOURCE_NAME}'].dataSourceId" \
    --output text \
    --region "${REGION}")
