# SUO-AWS: AWS News Subscription Platform

A serverless application that automatically scrapes AWS blog announcements, categorizes and summarizes them using AI, and emails subscribed users based on their selected AWS service categories.

## Architecture

SUO-AWS uses the following AWS services:

- **AWS Lambda** - For running the scraper, categorizer, and notifier functions
- **Amazon DynamoDB** - For storing blog posts and user subscriptions
- **Amazon Bedrock** - For AI-powered categorization and summarization
- **Amazon SNS** - For sending email notifications
- **AWS Step Functions** - For orchestrating the workflow
- **Amazon EventBridge** - For scheduling daily execution

## Project Structure

```
suo-aws/
├── layers/
│   └── common/
│       ├── python/
│       │   └── utils.py
│       └── requirements.txt
├── functions/
│   ├── scraper/
│   │   ├── app.py
│   │   └── requirements.txt
│   ├── categorizer/
│   │   ├── app.py
│   │   └── requirements.txt
│   └── notifier/
│       ├── app.py
│       └── requirements.txt
├── statemachine/
│   └── news_processing.asl.json
├── template.yaml
└── README.md
```

## Deployment

### Prerequisites

- AWS SAM CLI installed
- AWS CLI configured with appropriate credentials
- Python 3.10 installed

### Steps

1. Clone the repository
2. Navigate to the project directory
3. Build the SAM application:

```bash
sam build
```

4. Deploy the application:

```bash
sam deploy --guided
```

5. Follow the prompts to complete the deployment

## Usage

### Adding Users

To add users to the subscription system, you can use the AWS CLI or AWS Console to add items to the DynamoDB users table:

```bash
aws dynamodb put-item \
    --table-name suo-aws-users \
    --item '{
        "email": {"S": "user@example.com"},
        "name": {"S": "John Doe"},
        "subscribed_categories": {"SS": ["Compute", "AI/ML", "Serverless"]}
    }'
```

### Testing the Workflow

You can manually trigger the Step Functions workflow using the AWS Console or AWS CLI:

```bash
aws stepfunctions start-execution \
    --state-machine-arn <state-machine-arn> \
    --input '{}'
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.# aws-news-digest
# aws-news-digest
