#!/bin/bash
set -e

# Set variables
AWS_REGION="us-east-1"
ECR_REPOSITORY_NAME="suo-aws-scraper"
IMAGE_TAG="latest"
LAMBDA_FUNCTION_NAME="suo-aws-scraper"
LAMBDA_ROLE_NAME="suo-aws-scraper-role"
LAMBDA_TIMEOUT=300
LAMBDA_MEMORY=1024

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}:${IMAGE_TAG}"

# Create IAM role for Lambda if it doesn't exist
echo "Creating IAM role for Lambda..."
ROLE_ARN=$(aws iam get-role --role-name ${LAMBDA_ROLE_NAME} --query 'Role.Arn' --output text 2>/dev/null || echo "")

if [ -z "$ROLE_ARN" ]; then
  echo "Creating new IAM role..."
  TRUST_POLICY='{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }'
  
  ROLE_ARN=$(aws iam create-role \
    --role-name ${LAMBDA_ROLE_NAME} \
    --assume-role-policy-document "$TRUST_POLICY" \
    --query 'Role.Arn' \
    --output text)
    
  # Attach policies to the role
  aws iam attach-role-policy \
    --role-name ${LAMBDA_ROLE_NAME} \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    
  aws iam attach-role-policy \
    --role-name ${LAMBDA_ROLE_NAME} \
    --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
    
  # Wait for role to propagate
  echo "Waiting for IAM role to propagate..."
  sleep 10
fi

echo "Using role ARN: ${ROLE_ARN}"

# Check if Lambda function exists
FUNCTION_EXISTS=$(aws lambda list-functions --query "Functions[?FunctionName=='${LAMBDA_FUNCTION_NAME}'].FunctionName" --output text)

if [ -z "$FUNCTION_EXISTS" ]; then
  # Create Lambda function
  echo "Creating Lambda function..."
  aws lambda create-function \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --package-type Image \
    --code ImageUri=${ECR_REPOSITORY_URI} \
    --role ${ROLE_ARN} \
    --timeout ${LAMBDA_TIMEOUT} \
    --memory-size ${LAMBDA_MEMORY}
else
  # Update Lambda function
  echo "Updating Lambda function..."
  aws lambda update-function-code \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --image-uri ${ECR_REPOSITORY_URI}
fi

echo "Lambda function ${LAMBDA_FUNCTION_NAME} deployed successfully!"