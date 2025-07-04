#!/bin/bash

ECR_REGION="us-east-1"
ECR_ACCOUNT_ID=343218220735  # Replace with your AWS account ID
ECR_REPOSITORY_NAME="container-playwright"
IMAGE_TAG="latest"
IMAGE_URI="$ECR_ACCOUNT_ID.dkr.ecr.$ECR_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG"
LAMBDA_FUNCTION_NAME="scraper_lambda"
LAMBDA_ROLE_ARN="arn:aws:iam::$ECR_ACCOUNT_ID:role/LambdaScraperRole"

docker build --platform linux/amd64 -t docker-image:test .

aws ecr get-login-password --region $ECR_REGION | docker login --username AWS --password-stdin $ECR_ACCOUNT_ID.dkr.ecr.$ECR_REGION.amazonaws.com

REPO_EXISTS=$(aws ecr describe-repositories --region $ECR_REGION --repository-names $ECR_REPOSITORY_NAME 2>&1 || true)
if [[ $REPO_EXISTS == *"RepositoryNotFoundException"* ]]; then
    echo "Creating ECR repository..."
    aws ecr create-repository --repository-name $ECR_REPOSITORY_NAME --region $ECR_REGION --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
else
    echo "ECR repository already exists. Updating image..."
fi

docker tag docker-image:test $IMAGE_URI

docker push $IMAGE_URI

LAMBDA_EXISTS=$(aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME 2>&1 || true)
if [[ $LAMBDA_EXISTS == *"ResourceNotFoundException"* ]]; then
    echo "Creating Lambda function..."
    aws lambda create-function \
      --function-name $LAMBDA_FUNCTION_NAME \
      --memory-size 1024 \
      --timeout 900 \
      --package-type Image \
      --code ImageUri=$IMAGE_URI \
      --role $LAMBDA_ROLE_ARN
    echo "Lambda function created successfully!"
else
    echo "Lambda function exists. Updating code..."
    aws lambda update-function-code \
      --function-name $LAMBDA_FUNCTION_NAME \
      --image-uri $IMAGE_URI
    echo "Lambda function updated successfully!"
fi