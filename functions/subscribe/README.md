# Subscription Service

This directory contains two approaches for handling user subscriptions:

## 1. Direct API Gateway to DynamoDB Integration (Recommended)

**Files:**
- `api-gateway-dynamodb.yaml` - CloudFormation template
- `deploy-direct-integration.sh` - Deployment script

**Benefits:**
- Lower latency (no Lambda cold start)
- Lower cost (no Lambda execution charges)
- Built-in request validation
- Automatic scaling

**Use this approach when:**
- Simple CRUD operations
- No complex business logic needed
- Cost optimization is important

### Deploy Direct Integration:
```bash
./deploy-direct-integration.sh
```

## API Usage

Both approaches expose the same API endpoint:

### Request Format:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "categories": ["AI/ML", "Serverless", "Database"]
}
```

### Response Format:
```json
{
  "message": "Subscription created successfully",
  "subscription_id": "uuid-here",
  "email": "john@example.com"
}
```

### Test the API:
```bash
curl -X POST https://your-api-endpoint/subscribe \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "categories": ["AI/ML", "Serverless"]
  }'
```

## DynamoDB Table Structure

The `aws-suo-users` table will have:
- `id` (String) - Primary key (UUID)
- `name` (String) - User name
- `email` (String) - User email
- `categories` (String Set) - Subscribed categories
- `created_at` (String) - ISO timestamp
- `active` (Boolean) - Subscription status

## Request Validation

Both approaches validate:
- Required fields: name, email, categories
- Email format validation
- Categories must be non-empty array
- JSON schema validation

## CORS Support

Both APIs include CORS headers for web browser compatibility.
