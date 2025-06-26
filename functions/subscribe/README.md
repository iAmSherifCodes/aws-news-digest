# AWS Blog Subscription API

## Overview

The Subscribe function provides a serverless API for managing user subscriptions to AWS blog categories. It uses API Gateway with direct DynamoDB integration (no Lambda required) for high performance and cost efficiency.

### AWS Services
- Amazon CloudFormation
- AWS Api Gateway (POST / Integration method)
- Amazon DynamoDB (data retrieval)
- AWS IAM (service roles)
- Amazon CloudWatch (monitoring and logging)

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Client    │───▶│   API Gateway    │───▶│   DynamoDB      │
│   (Frontend)    │    │ (Direct Integ.)  │    │ (Users Table)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Files

### `api-gateway-dynamodb.yaml`
CloudFormation template for serverless subscription API.

**Resources Created:**
- API Gateway REST API with CORS support
- DynamoDB table for user subscriptions
- IAM role for API Gateway to DynamoDB access
- Request validation and data transformation
- Error handling and response mapping

### `deploy-direct-integration.sh`
Deployment script for the subscription API infrastructure.

## Features

### Direct API Gateway Integration
- No Lambda function required (cost-effective)
- Sub-millisecond response times
- Automatic scaling with API Gateway
- Built-in request validation

### Request Validation
- JSON schema validation
- Email format validation
- Required field checking
- Category array validation

### CORS Support
- Cross-origin resource sharing enabled
- Preflight OPTIONS handling
- Configurable allowed origins
- Standard CORS headers

### Error Handling
- Structured error responses
- HTTP status code mapping
- Input validation errors
- DynamoDB operation errors

## API Specification

### Endpoint
```
POST /subscribe
```

### Request Format
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "categories": ["compute", "container", "storage"]
}
```

### Request Validation Rules
- `name`: Required string, minimum 1 character
- `email`: Required string, valid email format
- `categories`: Required array, minimum 1 item, string elements

### Response Format

**Success (201 Created):**
```json
{
  "message": "Subscription created successfully",
  "subscription_id": "request-uuid",
  "email": "john@example.com"
}
```

**Validation Error (400 Bad Request):**
```json
{
  "error": "Bad Request",
  "message": "Invalid request data"
}
```

**Server Error (500 Internal Server Error):**
```json
{
  "error": "Internal Server Error",
  "message": "Failed to create subscription"
}
```

## Usage Examples

### cURL
```bash
curl -X POST https://pn9va5qd7k.execute-api.us-east-1.amazonaws.com/prod/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "categories": ["compute", "machine-learning", "database"]
  }'
```

### JavaScript (Fetch)
```javascript
const response = await fetch('https://pn9va5qd7k.execute-api.us-east-1.amazonaws.com/prod/subscribe', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'John Doe',
    email: 'john@example.com',
    categories: ['compute', 'machine-learning', 'database']
  })
});

const result = await response.json();
console.log(result);
```

### Python (Requests)
```python
import requests

url = 'https://pn9va5qd7k.execute-api.us-east-1.amazonaws.com/prod/subscribe'
data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'categories': ['compute', 'serverless', 'database']
}

response = requests.post(url, json=data)
print(response.json())
```

## Data Storage

### DynamoDB Table Schema
```json
{
  "id": "string (UUID from request ID)",
  "name": "string",
  "email": "string",
  "categories": ["string array"],
  "created_at": "string (ISO timestamp)",
  "active": "boolean (true)"
}
```

### Global Secondary Index
- **Index Name**: `email-index`
- **Partition Key**: `email`
- **Projection**: All attributes
- **Purpose**: Email-based lookups and duplicate prevention

## Deployment

### Prerequisites
- AWS CLI configured
- CloudFormation permissions
- DynamoDB and API Gateway permissions

### Deployment Steps

1. **Navigate to subscribe directory:**
   ```bash
   cd functions/subscribe
   ```

2. **Make deployment script executable:**
   ```bash
   chmod +x deploy-direct-integration.sh
   ```

3. **Run deployment:**
   ```bash
   ./deploy-direct-integration.sh
   ```

4. **Note the API endpoint from outputs:**
   ```bash
   aws cloudformation describe-stacks \
     --stack-name subscription-api \
     --query 'Stacks[0].Outputs'
   ```

### Manual Deployment
```bash
aws cloudformation deploy \
  --template-file api-gateway-dynamodb.yaml \
  --stack-name subscription-api \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides DynamoDBTableName=aws-suo-users
```

## Configuration

### CloudFormation Parameters
| Parameter | Description | Default |
|-----------|-------------|---------|
| `DynamoDBTableName` | Name of the users table | `aws-suo-users` |

### API Gateway Settings
- **Stage**: `prod`
- **Endpoint Type**: Regional
- **Request Validation**: Enabled
- **CORS**: Enabled for all origins

### DynamoDB Settings
- **Billing Mode**: Pay-per-request
- **Partition Key**: `id` (String)
- **GSI**: `email-index` on `email` attribute

## Request Transformation

### Input Mapping Template
The API Gateway transforms incoming JSON to DynamoDB format:

```vtl
{
  "TableName": "${DynamoDBTableName}",
  "Item": {
    "id": {
      "S": "$context.requestId"
    },
    "name": {
      "S": "$input.path('$.name')"
    },
    "email": {
      "S": "$input.path('$.email')"
    },
    "categories": {
      "SS": [
        #foreach($category in $input.path('$.categories'))
          "$category"#if($foreach.hasNext),#end
        #end
      ]
    },
    "created_at": {
      "S": "$context.requestTime"
    },
    "active": {
      "BOOL": true
    }
  }
}
```

## Security

### IAM Permissions
The API Gateway execution role has minimal permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
      ],
      "Resource": [
        "arn:aws:dynamodb:region:account:table/aws-suo-users",
        "arn:aws:dynamodb:region:account:table/aws-suo-users/index/*"
      ]
    }
  ]
}
```

### Input Validation
- JSON schema validation prevents malformed requests
- Email regex validation ensures valid email format
- Required field validation prevents incomplete submissions
- Array validation ensures categories are provided

### Rate Limiting
Consider implementing:
- API Gateway throttling limits
- DynamoDB write capacity limits

## Monitoring

### CloudWatch Metrics
- API Gateway request count and latency
- Error rates (4xx, 5xx responses)
- DynamoDB write capacity consumption
- Request validation failures

### Alarms
Set up alarms for:
- High error rates (> 5%)
- Unusual traffic spikes
- DynamoDB throttling
- API Gateway latency increases

## Extensions

### Potential Enhancements
- Email verification workflow
- Subscription management (update/delete)
- Category preference weighting
- Subscription analytics

### Custom Dashboards
Create dashboards to monitor:
- Subscription creation rates
- Popular category selections
- Geographic distribution of requests
- Error patterns and trends
