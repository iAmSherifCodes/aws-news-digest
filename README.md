# SUO-AWS: AWS News Subscription Platform

A serverless application that automatically scrapes AWS blog announcements, categorizes them using AI or URL-based logic, and emails subscribed users based on their selected AWS service categories.

## 🏗️ Architecture Overview

SUO-AWS (Stay Updated On AWS) is built using a serverless architecture with the following AWS services:

- **AWS Lambda** - Three main functions: scraper, categorizer, and notifier.
- **Amazon DynamoDB** - Three tables for storing blog posts, user subscriptions, and categories
- **Amazon Bedrock** - Optional AI-powered categorization and summarization using Nova Pro model
- **Amazon S3** - Batch inference input/output storage
- **Amazon SNS** - Error notifications
- **API Gateway** - Direct integration with DynamoDB for user subscription management
- **Amazon Step Function** - Orchestrate functions workflow
- **Amazon EventBridge Scheduler** - Recurring, cron-based scheduler that processes SUO-AWS daily by triggering the step-function workflow every 24 hours.
- **Amazon Q** - Documentation and Scripting.


## 📁 Project Structure

> **Note:** The Project structure is the combination of all functions, codes and scripts in one folder for documentation purpose. The SAM template is only used for deploying the Notifier Lambda function.

```
suo-aws/
├── functions/
│   ├── scraper/           # Web scraping AWS blogs
│   │   ├── app.py         # Main Lambda handler
│   │   ├── manual_extractor.py  # Playwright-based scraper
│   │   └── requirements.txt
│   ├── categorizer/       # AI/URL-based categorization
│   │   ├── app.py         # Main Lambda handler
│   │   ├── batch_inference.py   # Bedrock batch processing
│   │   ├── url_categorizer.py   # URL-based categorization
│   │   └── requirements.txt
│   ├── notifier/          # Email notifications
│   │   ├── app.js         # Main Lambda handler (Node.js)
│   │   ├── mail_setup.js  # Email configuration
│   │   └── package.json
│   └── subscribe/         # User subscription API
│       ├── api-gateway-dynamodb.yaml
│       └── deploy-direct-integration.sh
├── template.yaml          # SAM template
├── samconfig.toml         # SAM configuration
└── README.md
```

## 🚀 Deployment

### Prerequisites

- AWS SAM CLI installed
- AWS CLI configured with appropriate credentials
- Python 3.10+ installed
- Node.js 18+ installed
- Docker

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/iAmSherifCodes/suo-aws.git
   cd suo-aws
   ```

2. **Install Playwright dependencies (for scraper)**
   ```bash
   cd functions/scraper
   pip install playwright
   playwright install chromium
   cd ../..
   ```
3. **Deploy the scraper function**
   ```bash
    cd functions/scraper
    chmod +x create_iam_role.sh
    ./create_iam_role.sh
    chmod +x deploy.sh
    ./deploy.sh
   ```

4. **Build the SAM application**
   ```bash
   sam build
   ```

5. **Deploy the application**
   ```bash
   sam deploy --guided
   ```

6. **Deploy the subscription API (optional)**
   ```bash
   cd functions/subscribe
   ./deploy-direct-integration.sh
   ```
  
7. **Deploy the Categorizer Function directly from the Console**
   ```bash
   cd functions/categorizer
   ./deploy-direct-integration.sh
   ```

### Environment Variables

The application uses the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTS_TABLE` | DynamoDB table for blog posts | `suo-aws-posts` |
| `USERS_TABLE` | DynamoDB table for users | `aws-suo-users` |
| `CATEGORIES_TABLE` | DynamoDB table for categories | `suo-categories` |
| `GENAI_MODEL` | Enable AI categorization | `false` |
| `BEDROCK_MODEL_ID` | Bedrock model for AI | `amazon.nova-pro-v1:0` |
| `EMAIL_USER` | SMTP username | - |
| `EMAIL_PASS` | SMTP password | - |
| `FROM_EMAIL` | Sender email address | - |

## 🔧 How It Works

### 1. **Web Scraping (Scraper Function)**
- Uses Playwright to scrape AWS blogs
- Extracts posts for a specific date (default: previous day)
- Stores raw blog post data in DynamoDB
- Handles pagination and dynamic content loading

### 2. **Categorization (Categorizer Function)**
- **URL-based**: Extracts category from blog URL path
- **AI-powered(IAM issue: Account needed to raise a support ticket for CreateModelInvocationJob Authorization job )**: Uses Amazon Bedrock (Amazon Nova Pro Model) for intelligent categorization
- Supports batch processing for multiple posts using batch inference
- Updates posts with category information

### 3. **Notification (Notifier Function)**
- Retrieves categorized posts for a date
- Matches posts with user subscriptions
- Sends personalized emails using SMTP
- Handles error notifications via SNS

### 4. **Subscription Management**
- Direct API Gateway to DynamoDB integration
- RESTful API for user subscription management
- Input validation and CORS support

## 📊 Database Schema

### Posts Table (`suo-aws-posts`)
```json
{
  "id": "string (UUID)",
  "title": "string",
  "url": "string", 
  "author": "string",
  "date": "string (MM/DD/YYYY)",
  "description": "string",
  "category": "string",
  "summary": "string (optional)",
  "processed": "boolean"
}
```

### Users Table (`aws-suo-users`)
```json
{
  "id": "string (UUID)",
  "email": "string",
  "name": "string",
  "categories": ["string"],
  "active": "boolean",
  "created_at": "string"
}
```

### Categories Table (`suo-categories`)
```json
{
  "id": "string (UUID)",
  "date": "string (MM/DD/YYYY)",
  "categories": ["string"]
}
```

## 🔌 API Usage

### Subscribe to Categories
```bash
curl -X POST https://pn9va5qd7k.execute-api.us-east-1.amazonaws.com/prod/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com", 
    "categories": ["compute", "database", "machine-learning"]
  }'
```

### Manual Function Invocation

**Scraper Function:**
```bash
aws lambda invoke \
  --function-name suo-aws-scraper \
  --payload '{"target_date": "06/25/2025"}' \
  response.json
```

**Categorizer Function:**
```bash
aws lambda invoke \
  --function-name suo-aws-categorizer \
  --payload '{"target_date": "06/25/2025"}' \
  response.json
```

**Notifier Function:**
```bash
aws lambda invoke \
  --function-name suo-aws-notifier \
  --payload '{}' \
  response.json
```

## 🎯 AWS Service Categories

The system recognizes these AWS service categories:
- `architecture`, `mt`, `gametech`, `aws-insights`, `awsmarketplace`, `big-data`
- `compute`, `containers`, `database`, `desktop-and-application-streaming`, `developer`, `devops`, `mobile` 
- `networking-and-content-delivery`, `opensource`,`machine-learning`, `media`, `quantum-computing`, `robotics`
- `awsforsap`, `security`, `spatial`, `startups`, `storage`, `supply-chain`, `training-and-certification`
- And many more ...

## 🔍 Monitoring & Troubleshooting

### CloudWatch Logs
- Each Lambda function creates its own log group
- Log levels can be controlled via `LOG_LEVEL` environment variable

### Error Handling
- SNS notifications for critical errors
- Comprehensive error logging
- Graceful degradation for non-critical failures

### Performance Optimization
- DynamoDB on-demand billing
- Lambda memory optimization (128MB default)
- Batch processing for AI operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Repository

**Public Repository URL:** https://github.com/iAmSherifCodes/suo-aws.git

---

*Built with ❤️ using AWS Serverless technologies*
