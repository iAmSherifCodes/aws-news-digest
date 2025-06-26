#!/bin/bash

# Deploy API Gateway direct integration with DynamoDB
# This is the recommended approach for simple CRUD operations

set -e

STACK_NAME="subscription-api-direct"
TEMPLATE_FILE="api-gateway-dynamodb.yaml"
REGION="us-east-1"

echo "Deploying API Gateway direct integration with DynamoDB..."

# Deploy CloudFormation stack
aws cloudformation deploy \
    --template-file $TEMPLATE_FILE \
    --stack-name $STACK_NAME \
    --capabilities CAPABILITY_IAM \
    --region $REGION \
    --parameter-overrides \
        DynamoDBTableName=aws-suo-users

# Get the API endpoint
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text)

echo "Deployment completed successfully!"
echo "API Endpoint: $API_ENDPOINT"
echo ""
echo "Test the API with:"
echo "curl -X POST $API_ENDPOINT \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"name\":\"John Doe\",\"email\":\"cashstocksng@gmail.com\",\"categories\":[\"AI/ML\",\"Serverless\"]}'"