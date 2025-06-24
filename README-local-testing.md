# Local Testing Guide for SUO-AWS

This guide explains how to test the SUO-AWS application locally using the AWS SAM CLI.

## Prerequisites

1. AWS SAM CLI installed
2. Docker installed and running
3. AWS CLI installed
4. Local DynamoDB (optional, for full testing)

## Setup for Local Testing

### 1. Start Local DynamoDB (Optional)

If you want to test with a local DynamoDB instance:

```bash
docker run -p 8000:8000 amazon/dynamodb-local
```

### 2. Environment Variables

The application uses environment variables that are defined in `env.json`. These are automatically loaded when using the `--env-vars` option with `sam local invoke`.

## Testing Individual Functions

### Test the Scraper Function

```bash
sam local invoke ScraperFunction --event events/scraper-event.json --env-vars env.json
```

This will invoke the scraper function with an empty event. The function will scrape the AWS blog and return the results.

For local testing without making actual HTTP requests, you can temporarily replace `app.py` with `app_local.py` which uses mock data.

### Test the Categorizer Function

```bash
sam local invoke CategorizerFunction --event events/categorizer-event.json --env-vars env.json
```

This requires a valid post ID in the event. For local testing, you'll need to:

1. Run the scraper function first to get a post ID
2. Update the `categorizer-event.json` with the post ID
3. Run the categorizer function

### Test the Notifier Function

```bash
sam local invoke NotifierFunction --event events/notifier-event.json --env-vars env.json
```

This also requires a valid post ID that has been categorized.

## Testing the Complete Workflow

To test the complete workflow locally:

```bash
# Make the test script executable
chmod +x local-test.sh

# Run the test script
./local-test.sh
```

This script will:
1. Set up environment variables
2. Create local DynamoDB tables
3. Add a test user to the users table
4. Test each function in sequence

## Mocking External Services

For local testing, you may want to mock external services:

- **Amazon Bedrock**: The categorizer function uses Amazon Bedrock, which is not available locally. For testing, you can modify the function to return mock categories and summaries.
- **Amazon SNS**: The notifier function uses SNS to send emails. For local testing, you can modify the function to log the emails instead of sending them.

## Debugging

To enable step-through debugging:

```bash
sam local invoke ScraperFunction --event events/scraper-event.json --env-vars env.json --debug-port 5858
```

Then connect your IDE debugger to port 5858.