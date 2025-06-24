#!/bin/bash
set -e

# Set variables
AWS_REGION="us-east-1"
ECR_REPOSITORY_NAME="suo-aws-scraper"
IMAGE_TAG="latest"

# Configure AWS credentials (uncomment and modify if needed)
export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""
export AWS_SESSION_TOKEN=""
echo "Checking AWS credentials..."
aws sts get-caller-identity

echo "Creating ECR repository if it doesn't exist..."
aws ecr describe-repositories --repository-names ${ECR_REPOSITORY_NAME} --region ${AWS_REGION} || \
    aws ecr create-repository --repository-name ${ECR_REPOSITORY_NAME} --region ${AWS_REGION}

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}"

echo "Logging in to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPOSITORY_URI%/*}

echo "Building Docker image..."
docker build -t ${ECR_REPOSITORY_NAME}:${IMAGE_TAG} .

echo "Tagging image for ECR..."
docker tag ${ECR_REPOSITORY_NAME}:${IMAGE_TAG} ${ECR_REPOSITORY_URI}:${IMAGE_TAG}

echo "Pushing image to ECR..."
docker push ${ECR_REPOSITORY_URI}:${IMAGE_TAG}

echo "Successfully pushed ${ECR_REPOSITORY_URI}:${IMAGE_TAG} to ECR"