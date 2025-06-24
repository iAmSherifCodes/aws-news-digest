#!/bin/bash

# Set environment variables for local testing
export POSTS_TABLE=suo-aws-posts
export USERS_TABLE=suo-aws-users
export SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:suo-aws-news-notifications
export LOG_LEVEL=INFO

# Create local DynamoDB tables for testing
echo "Creating local DynamoDB tables..."
aws dynamodb create-table \
    --table-name $POSTS_TABLE \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --key-schema AttributeName=id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url http://localhost:8000 \
    --region us-east-1 || true

aws dynamodb create-table \
    --table-name $USERS_TABLE \
    --attribute-definitions AttributeName=email,AttributeType=S \
    --key-schema AttributeName=email,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url http://localhost:8000 \
    --region us-east-1 || true

# Add a test user to the users table
echo "Adding test user to DynamoDB..."
aws dynamodb put-item \
    --table-name $USERS_TABLE \
    --item '{"email": {"S": "test@example.com"}, "name": {"S": "Test User"}, "subscribed_categories": {"SS": ["Compute", "AI/ML", "Serverless"]}}' \
    --endpoint-url http://localhost:8000 \
    --region us-east-1

# Test the scraper function
echo "Testing scraper function..."
sam local invoke ScraperFunction \
    --event events/scraper-event.json \
    --env-vars env.json

# Test the categorizer function
echo "Testing categorizer function..."
sam local invoke CategorizerFunction \
    --event events/categorizer-event.json \
    --env-vars env.json

# Test the notifier function
echo "Testing notifier function..."
sam local invoke NotifierFunction \
    --event events/notifier-event.json \
    --env-vars env.json

echo "Testing complete!"