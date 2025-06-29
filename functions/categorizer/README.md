# AWS Blog Categorizer Function

## Overview

The Categorizer function processes scraped AWS blog posts and assigns them to relevant AWS service categories. It supports both URL-based categorization (fast, rule-based) and AI-powered categorization using Amazon Bedrock (intelligent, context-aware).

### AWS Services
- AWS Lambda (Python runtime)
- Amazon Bedrock (Nova Pro model)
- Amazon S3 (batch processing)
- Amazon DynamoDB (data storage)
- AWS IAM (service roles)
- Amazon CloudWatch (monitoring and logging)

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   DynamoDB      │───▶│ Categorizer      │───▶│   DynamoDB      │
│  (Posts Table)  │    │    Lambda        │    │ (Updated Posts) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Amazon Bedrock │
                       │  ( Nova Pro )   │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Amazon S3     │
                       │ (Batch Files)   │
                       └─────────────────┘
```

## Files

### `app.py`
Main Lambda handler that orchestrates the categorization process.

**Key Functions:**
- `lambda_handler(event, context)` - Main entry point with mode selection
- `get_post(post_id, date)` - Retrieve posts from DynamoDB
- `update_post(post_id, category, summary, posts_data)` - Update posts with results
- `save_categories_for_date(date, categories)` - Store daily category summary

**Environment Variables:**
- `POSTS_TABLE` - DynamoDB table for blog posts
- `CATEGORIES_TABLE` - DynamoDB table for category summaries
- `GENAI_MODEL` - Enable AI categorization (true/false)
- `BEDROCK_MODEL_ID` - Bedrock model identifier
- `BATCH_BUCKET` - S3 bucket for batch inference
- `AWS_BLOGS_BASE_URL` - Base URL for AWS blogs

### `url_categorizer.py`
Fast, rule-based categorization using URL patterns.

**Key Functions:**
- `get_category_from_url(posts)` - Extract categories from blog URLs
- URL pattern matching against known AWS service categories
- Fallback to 'unknown' category for unmatched URLs

**Supported Categories:**
- `compute`, `serverless`, `containers`
- `database`, `storage`, `networking-and-content-delivery`
- `security`, `machine-learning`, `analytics`
- `developer`, `devops`, `mobile`, `iot`
- And 40+ other AWS service categories

### `batch_inference.py` (IAM issue: Account needed to raise a support ticket)
AI-powered categorization using Amazon Bedrock batch inference.

**Key Functions:**
- `run_batch_inference(date, limit)` - Main batch processing orchestrator
- `get_posts_for_batch(date, limit)` - Retrieve unprocessed posts
- `create_batch_input_file(posts, job_name)` - Generate JSONL input files
- `submit_batch_job(input_s3_uri, output_s3_uri, job_name, role_arn)` - Submit to Bedrock
- `monitor_batch_job(job_arn, max_wait_minutes)` - Monitor job progress
- `download_and_parse_results(job_arn, output_s3_prefix)` - Process results
- `update_posts_with_results(results)` - Update DynamoDB with AI results

**AI Capabilities:**
- Intelligent categorization based on content analysis
- Multi-category assignment for complex posts
- Content summarization (up to 5 sentences)
- Batch processing for cost efficiency

## Features

### Dual Processing Modes

**URL-Based Categorization (Default)**
- Fast processing using URL pattern matching
- No external API calls or costs
- Reliable for standard AWS blog structure
- Immediate results

**AI-Powered Categorization (Optional)**
- Context-aware categorization using Amazon Bedrock
- Content summarization capabilities
- Handles complex or ambiguous content
- Batch processing for cost optimization

### Batch Processing
- Processes multiple posts simultaneously
- Automatic S3 bucket creation and management
- IAM role creation for Bedrock access
- Job monitoring with timeout handling
- Result parsing and DynamoDB updates

### Error Handling
- Graceful fallback between processing modes
- Comprehensive logging and error tracking
- Automatic retry mechanisms
- Resource cleanup on failures

## Usage

### Manual Invocation

 Please refer to the README.md file
- **[TEST ReadMe file](../../Test_README.md)** - For manual testing guide.

**URL-Based Categorization:**
```bash
aws lambda invoke \
  --function-name suo-aws-categorizer \
  --payload '{"target_date": "12/15/2024"}' \
  response.json
```

**AI-Powered Categorization:** (IAM issue: Account needed to raise a support ticket)
```bash
# Set environment variable first
aws lambda update-function-configuration \
  --function-name suo-aws-categorizer \
  --environment Variables='{GENAI_MODEL=true}'

aws lambda invoke \
  --function-name suo-aws-categorizer \
  --payload '{"date": "12/15/2024"}' \
  response.json
```

### Event Payload
```json
{
  "date": "12/15/2024"  // Optional, defaults to previous day
}
```

### Response Format

**URL-Based Response:**
```json
{
  "statusCode": 200,
  "body": {
    "posts": [
      {
        "id": "post-uuid",
        "category": "compute"
      }
    ],
    "categories": ["compute", "serverless", "database"]
  }
}
```

**AI-Powered Response:**

```json
{
  "statusCode": 200,
  "body": {
    "processed_count": 5,
    "categorization_job": "arn:aws:bedrock:...",
    "summarization_job": "arn:aws:bedrock:..."
  }
}
```


## Dependencies

### Python Packages
```
boto3>=1.34.0
aioboto3
asyncio
```

## Deployment Considerations

### Lambda Configuration
- **Runtime**: Python 3.10
- **Memory**: 128MB (URL-based) / 256MB (AI-powered)
- **Timeout**: 15 seconds (URL-based) / 15 minutes (AI-powered)
- **Architecture**: x86_64

### Permissions Required

**Basic Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:BatchWriteItem",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/suo-aws-posts",
        "arn:aws:dynamodb:*:*:table/suo-categories"
      ]
    }
  ]
}
```

**AI-Powered Additional Permissions:**
```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:*",
    "s3:*",
    "iam:CreateRole",
    "iam:GetRole",
    "iam:PutRolePolicy",
    "iam:PassRole",
    "sts:GetCallerIdentity"
  ],
  "Resource": "*"
}
```

## AI Categorization Details

### Prompt Engineering
The system uses carefully crafted prompts for optimal results:

**Categorization Prompt:**
```
You are an AWS expert. Analyze this AWS blog post and determine which AWS service categories it belongs to.
Choose from these categories: [list of 20 categories] only.
Each category should be relevant to the content of the post.
If the post does not fit any of these categories, return 'Uncategorized'.
If the post fits multiple categories, return the most relevant ones.
You can select multiple categories if applicable, but limit to the 3 most relevant ones.
```

**Summarization Prompt:**
```
You are an AWS expert. Create a concise summary (maximum 5 sentences) of this AWS blog post.
Focus on the key announcements, features, or changes described.
```

### Batch Processing Workflow
1. Retrieve unprocessed posts from DynamoDB
2. Create JSONL input files for categorization and summarization
3. Upload input files to S3
4. Create/verify IAM service role for Bedrock
5. Submit batch inference jobs to Bedrock
6. Monitor job progress (up to 60 minutes)
7. Download and parse results from S3
8. Update DynamoDB posts with AI-generated content

### Cost Optimization
- Batch processing reduces per-request costs
- Configurable batch size limits
- Automatic cleanup of temporary files
- On-demand processing only for new posts

## Monitoring

### CloudWatch Metrics
- Function duration and memory usage
- Bedrock API call counts and costs
- S3 storage usage for batch files
- DynamoDB read/write capacity consumption

### Custom Metrics
- Posts processed per execution
- AI categorization accuracy (manual validation)
- Batch job success/failure rates
- Processing time per post

### Alarms
- Batch job failures
- Function timeout errors
- Bedrock quota exceeded
- S3 access errors

## Performance Optimization

### URL-Based Mode
- Minimal memory requirements (128MB)
- Fast execution (< 10 seconds)
- No external API dependencies
- Cost-effective for high-volume processing

### AI-Powered Mode
- Higher memory allocation (256MB+)
- Longer execution time (5-15 minutes)
- Batch processing for efficiency
- Consider cost vs. accuracy trade-offs

### Hybrid Approach
- Use URL-based for standard posts
- Use AI-powered for complex or ambiguous content
- Implement confidence scoring for automatic mode selection

*Built with ❤️ using AWS Serverless technologies*