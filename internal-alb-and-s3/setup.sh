#!/bin/bash

S3_VPC_ENDPOINT_ARN=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --query "Stacks[].Outputs[?OutputKey=='S3VpcEndpointId'].OutputValue" --output text
)

S3_VPC_ENDPOINT_IP=$(aws ec2 describe-network-interfaces \
--network-interface-ids "${S3_VPC_ENDPOINT_ARN}" \
--query "NetworkInterfaces[].PrivateIpAddresses[].PrivateIpAddress" \
--output text)

ELB_TARGET_GROUP_ARN=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --query "Stacks[].Outputs[?OutputKey=='ApplicationLoadBalancerTargetGroupArn'].OutputValue" --output text
)

aws elbv2 register-targets \
--target-group-arn "${ELB_TARGET_GROUP_ARN}" \
--targets Id="${S3_VPC_ENDPOINT_IP}",Port=443

S3_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --query "Stacks[].Outputs[?OutputKey=='S3Bucket'].OutputValue" --output text
)

aws s3api put-object \
--bucket "${S3_BUCKET}" \
--key index.html \
--body index.html \
--content-type text/html

EC2_INSTANCE_ID=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --query "Stacks[].Outputs[?OutputKey=='Ec2InstanceInstanceId'].OutputValue" --output text
)

INTERNAL_ALB_DNS_NAME=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --query "Stacks[].Outputs[?OutputKey=='ApplicationLoadBalancerDNSName'].OutputValue" --output text
)

aws ssm start-session \
--target "${EC2_INSTANCE_ID}" \
--document-name AWS-StartPortForwardingSessionToRemoteHost \
--parameters '{"portNumber":["80"],"localPortNumber":["10080"],"host":["'"${INTERNAL_ALB_DNS_NAME}"'"]}'


