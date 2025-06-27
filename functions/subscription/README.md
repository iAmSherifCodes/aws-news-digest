# AWS Blog Subscription Lambda Function

## Overview

The subscription Lambda function provides a serverless API for managing user subscriptions to AWS blog categories. It uses Lambda Function URL with CORS enabled for direct HTTP access, validates user input, checks for duplicate emails, and stores subscription data in DynamoDB.

### AWS Services
- AWS Lambda (Node.js runtime with Function URL)
- Amazon DynamoDB (user data storage)
- AWS IAM (execution roles)
- Amazon CloudWatch (monitoring and logging)

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Function URL    │───▶│   Lambda         │───▶│   DynamoDB      │
│ (CORS enabled)  │    │   (app.js)       │    │ (Users Table)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Lambda Function URL

The function is accessible via Lambda Function URL with:
- **CORS enabled** for cross-origin requests
- **Direct HTTP access** without API Gateway
- **Simplified deployment** and management

## Files

### `app.js`
Lambda function handler for subscription management.

**Features:**
- Input validation for name, email, and categories
- Duplicate email checking via DynamoDB scan
- User subscription creation with timestamp
- Error handling and structured responses

## Function Details

### Handler Function
The main Lambda handler processes subscription requests and returns appropriate HTTP responses.

### Input Validation
- **Name**: Required non-empty string
- **Email**: Required valid email format
- **Categories**: Required non-empty array

### Duplicate Prevention
Uses DynamoDB scan with filter expression to check for existing email addresses before creating new subscriptions.

### Data Storage
Creates user records with:
- Unique ID (timestamp-based)
- Email, name, and categories
- Active status and creation timestamp

## API Specification

### Input Format
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "categories": ["compute", "container", "storage"]
}
```

### Success Response (200)
```json
{
  "message": "Subscription created successfully",
  "user": {
    "name": "John Doe",
    "email": "john@example.com",
    "categories": ["compute", "container", "storage"]
  }
}
```

### Error Response (400)
```json
{
  "error": "Valid email is required"
}
```

## Environment Variables

- `AWS_REGION`: AWS region for DynamoDB client
- `USERS_TABLE`: DynamoDB table name for user storage

## DynamoDB Schema

```json
{
  "id": "string (timestamp)",
  "email": "string",
  "name": "string", 
  "categories": ["array of strings"],
  "active": "boolean (true)",
  "createdAt": "string (ISO timestamp)"
}
```

## Error Handling

The function handles various error scenarios:
- Missing or invalid input fields
- Duplicate email addresses
- DynamoDB operation failures
- Validation errors with descriptive messages

## Dependencies

- `@aws-sdk/client-dynamodb`: DynamoDB client
- `@aws-sdk/lib-dynamodb`: Document client for simplified operations