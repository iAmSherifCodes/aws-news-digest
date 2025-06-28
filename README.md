# SUO-AWS: AWS News Subscription Platform

SUO-AWS is a serverless application that keeps curious minds in the loop with the latest updates, service news, and insights they care about from AWS, automatically and effortlessly.

## Architecture Diagram

![Architecture Diagram](https://github.com/user-attachments/assets/c8bb473d-1c67-44de-83f2-c3f7576a3ed5)


## 🏗️ Architecture Overview

SUO-AWS (Stay Updated On AWS) is built using a serverless architecture with the following AWS services:

- **AWS Lambda** - Four main functions: scraper, categorizer, notifier and subscriber.
- **Amazon DynamoDB** - Three tables for storing blog posts, user subscriptions, and categories
- **Amazon Bedrock** - Optional AI-powered categorization and summarization using Nova Pro model
- **Amazon S3** - Batch inference input/output storage
- **Amazon SNS** - Error notifications
- **API Gateway** - For testing purpose, Triggers Step-Function StartExecution state.
- **Amazon Step Function** - Orchestrate functions workflow
- **Amazon EventBridge Scheduler** - Recurring, cron-based scheduler that processes SUO-AWS daily by triggering the step-function workflow every 24 hours.
- **Amazon Q** - Documentation and Scripting.
 
## Manual Testing
 Please refer to the README.md file
- **[TEST ReadMe file](./Test_README.md)** - Manual Testing guide

## 📁 Project Structure

> **Note:** The Project structure is the combination of all functions, codes and scripts in one folder for documentation purpose. The SAM template is only used for deploying the Notifier Lambda function. Some functions are deployed using AWS CLI and some directly from the Console.

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
│   └── subscription/         # User subscription API
│       └── app.js
├── template.yaml          # SAM template
├── samconfig.toml         # SAM configuration  
├── README.md     
└── Test_README.md
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

6. **Deploy the subscription function directly from the Console(optional)**
   ```bash
   cd functions/subscription
   ```
  
7. **Deploy the Categorizer Function directly from the Console**
   ```bash
   cd functions/categorizer
   ```

### Environment Variables

The application uses the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTS_TABLE` | DynamoDB table for blog posts | - |
| `USERS_TABLE` | DynamoDB table for users | - |
| `CATEGORIES_TABLE` | DynamoDB table for categories | - |
| `GENAI_MODEL` | Enable AI categorization | `false` |
| `BEDROCK_MODEL_ID` | Bedrock model for AI | `amazon.nova-pro-v1:0` |
| `EMAIL_USER` | SMTP username | - |
| `EMAIL_PASS` | SMTP password | - |
| `FROM_EMAIL` | Sender email address | - |

## 🔧 How It Works

### 1. **Web Scraping (Scraper Lambda Function)**
- Uses Playwright to scrape AWS blogs
- Extracts posts for a specific date (default: previous day)
- Stores raw blog post data in DynamoDB
- Handles pagination and dynamic content loading

### 2. **Categorization (Categorizer Lambda Function)**
- **URL-based**: Extracts category from blog URL path
- **AI-powered(Not complete - IAM issue*: Account needed to raise a support ticket for CreateModelInvocationJob Authorization job )**: Uses Amazon Bedrock (Amazon Nova Pro Model) for intelligent categorization
- Supports batch processing for multiple posts using batch inference
- Updates posts with category information

### 3. **Notification (Notifier Lambda Function)**
- Retrieves categorized posts for a date
- Matches posts with user subscriptions
- Sends personalized emails using SMTP
- Handles error notifications via SNS

### 4. **Subscription Lambda Function**
- Exposes an API using Lambda Function URL with CORS enabled
- Validates input
- Stores subcriber data in DynamoDB

## 📊 DynamoDB Database Schema

### Posts Table
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

### Users Table
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

### Categories Table
```json
{
  "id": "string (UUID)",
  "date": "string (MM/DD/YYYY)",
  "categories": ["string"]
}
```

## 🔌 API Usage

### Subscribe to Categories

You can go through the website or use cURL.

#### Website
https://suo-aws.vercel.app/

#### Curl command
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

 Please refer to the README.md file
- **[TEST ReadMe file](./Test_README.md)** - For manual testing guide


## 🎯 AWS Service Categories

The system recognizes these AWS service categories:
- `architecture`, `mt`, `gametech`, `aws-insights`, `awsmarketplace`, `big-data`
- `compute`, `containers`, `database`, `desktop-and-application-streaming`, `developer`, `devops`, `mobile` 
- `networking-and-content-delivery`, `opensource`,`machine-learning`, `media`, `quantum-computing`, `robotics`
- `awsforsap`, `security`, `startups`, `storage`, `supply-chain`, `training-and-certification`
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


## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Repository

**Public Repository URL:** https://github.com/iAmSherifCodes/suo-aws.git

---

*Built with ❤️ using AWS Serverless technologies*
