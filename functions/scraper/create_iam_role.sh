#!/bin/bash

# Variables
ROLE_NAME="LambdaScraperRole1"
POLICY_NAME="${ROLE_NAME}Policy"
AWS_REGION="us-east-1"
DYNAMODB_TABLE="suo-aws-posts"

echo "Creating IAM role for Lambda Scraper..."

# Trust policy for Lambda
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "lambda.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Lambda policy with only needed permissions
cat > lambda-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:BatchWriteItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/${DYNAMODB_TABLE}"
    }
  ]
}
EOF

# Check if role exists
if ! aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
  echo "Creating role: $ROLE_NAME"
  aws iam create-role \
    --role-name "$ROLE_NAME" \
    --assume-role-policy-document file://trust-policy.json
  sleep 5
else
  echo "Role $ROLE_NAME already exists."
fi

# Create policy (if not already exists)
aws iam create-policy \
  --policy-name "$POLICY_NAME" \
  --policy-document file://lambda-policy.json \
  --description "Minimal policy for AWS Blog scraper Lambda" \
  2>/dev/null || echo "Policy $POLICY_NAME already exists."

# Attach policies
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws iam attach-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/${POLICY_NAME}"

aws iam attach-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"

# Output the role ARN
ROLE_ARN=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)
echo "Role ARN: $ROLE_ARN"

# Cleanup
rm -f trust-policy.json lambda-policy.json

echo "IAM role setup completed successfully!"
