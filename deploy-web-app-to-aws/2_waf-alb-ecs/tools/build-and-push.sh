#!/bin/bash

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGIN=$(aws configure get region)
ECS_REPOSITORY_NAME="web-app-on-waf-alb-ecs-dev-ecr-repository"

function build_and_push_docker_image() {
  local repository_name=$1
  echo "### ECRにログインします。${repository_name}"
  aws ecr get-login-password --region "${AWS_REGIN}" | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGIN}.amazonaws.com"

  echo "### コンテナイメージをビルドします。 ${repository_name}"
  docker build --no-cache -t "${repository_name}" .

  echo "### コンテナイメージにタグをつけます。${repository_name}"
  docker tag "${repository_name}:latest" "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGIN}.amazonaws.com/${repository_name}:latest"

  echo "### コンテナイメージをECRにプッシュします。${repository_name}"
  docker push "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGIN}.amazonaws.com/${repository_name}:latest"
}

function main() {
  cd ../ || exit
  build_and_push_docker_image ${ECS_REPOSITORY_NAME}
}

read -rp "ECS用のコンテナイメージをbuildし、ECRにpushしますか? (y/N): " answer

if [[ ${answer} == "y" ]]; then
  main
else
  echo " 処理を終了します。"
  exit 1
fi
