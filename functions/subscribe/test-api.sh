#!/bin/bash

# Test script for the subscription API

if [ -z "$1" ]; then
    echo "Usage: $0 <API_ENDPOINT>"
    echo "Example: $0 https://pn9va5qd7k.execute-api.us-east-1.amazonaws.com/prod/subscribe"
    exit 1
fi

API_ENDPOINT=$1

echo "Testing Subscription API: $API_ENDPOINT"
echo "========================================="

# Test 1: Valid request
echo "Test 1: Valid subscription request"
curl -X POST $API_ENDPOINT \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "categories": ["AI/ML", "Serverless"]
  }' \
  -w "\nStatus: %{http_code}\n\n"

# Test 2: Missing required field
echo "Test 2: Missing email field (should fail)"
curl -X POST $API_ENDPOINT \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Jane Doe",
    "categories": ["Database"]
  }' \
  -w "\nStatus: %{http_code}\n\n"

# Test 3: Invalid email format
echo "Test 3: Invalid email format (should fail)"
curl -X POST $API_ENDPOINT \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Bob Smith",
    "email": "invalid-email",
    "categories": ["Security"]
  }' \
  -w "\nStatus: %{http_code}\n\n"

# Test 4: Empty categories
echo "Test 4: Empty categories array (should fail)"
curl -X POST $API_ENDPOINT \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "categories": []
  }' \
  -w "\nStatus: %{http_code}\n\n"

# Test 5: CORS preflight
echo "Test 5: CORS preflight request"
curl -X OPTIONS $API_ENDPOINT \
  -H 'Origin: https://example.com' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: Content-Type' \
  -w "\nStatus: %{http_code}\n\n"

echo "Testing completed!"