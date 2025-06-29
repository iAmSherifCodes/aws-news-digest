#!/bin/bash

# Variables
FUNCTION_NAME="scraper_lambda_1"

echo "Invoking Lambda function..."
# Create the payload with formatted JSON
PAYLOAD=$(cat << EOF
{
}
EOF
)

# Invoke Lambda and save response
aws lambda invoke \
    --function-name $FUNCTION_NAME \
    --payload "$PAYLOAD" \
    --cli-binary-format raw-in-base64-out \
    response.json

# Check if invocation was successful
if [ $? -eq 0 ]; then
    echo "Lambda invoked successfully!"
    echo "Response saved to response.json"
    cat response.json
else
    echo "Error invoking Lambda function"
    exit 1
fi