# AWS Blog Scraper Function

## Overview

The Scraper function is responsible for automatically extracting AWS blog posts from the official AWS blogs website using web scraping techniques. It uses Playwright for robust browser automation and handles dynamic content loading

### AWS Services
- AWS Lambda (Python runtime)
- Amazon Lambda CLI
- Amazon DynamoDB (data storage)
- AWS IAM (service roles)
- Amazon CloudWatch (monitoring and logging)

## Architecture

```
┌──────────────────┐    ┌─────────────────┐
│  Scraper Lambda  │───▶│   DynamoDB      │
│  (Playwright)    │    │  (Posts Table)  │
└──────────────────┘    └─────────────────┘
```

## Files

### `app.py`
Main Lambda handler that orchestrates the scraping process.

**Key Functions:**
- `lambda_handler(event, context)` - Main entry point
- `get_blog_posts_for_date(target_date, url)` - Async scraper coordinator
- `save_posts_to_dynamodb(posts)` - Batch save to DynamoDB
- `get_previous_date()` - Date utility function

**Environment Variables:**
- `POSTS_TABLE` - DynamoDB table name for storing posts
- `LOG_LEVEL` - Logging level (INFO, DEBUG, ERROR)

### `manual_extractor.py`
Core web scraping logic using Playwright browser automation.

**Key Classes:**
- `BlogScraper` - Main scraper class with async context manager
- `BlogScraperError` - Custom exception for scraper errors

**Key Methods:**
- `__aenter__()/__aexit__()` - Async context manager for resource cleanup
- `_initialize_browser()` - Browser setup with optimized configuration
- `navigate_to_url(url)` - Navigate to target URL with error handling
- `extract_post_info(blog_element)` - Extract post data from DOM elements
- `process_blog_posts(existing_posts)` - Process all posts on current page
- `find_load_more_button()` - Locate pagination controls
- `click_load_more_button()` - Handle dynamic content loading
- `get_blog_posts_for_date(url)` - Main scraping orchestrator

## Features

### Robust Browser Configuration
- Headless Chrome with optimized arguments
- Custom user agent and HTTP headers
- Comprehensive error handling and timeouts
- Resource cleanup and memory management

### Dynamic Content Handling
- Automatic pagination through "Load More" buttons
- Multiple strategies for waiting for new content
- Duplicate detection and prevention
- Graceful handling of missing elements

### Data Extraction
- Post title, URL, author, date, and description
- Date-based filtering for targeted scraping
- Structured data output for downstream processing
- UUID generation for unique post identification

### Error Handling
- Custom exception types for different error scenarios
- Comprehensive logging with multiple levels
- Automatic retry mechanisms for transient failures
- Resource cleanup on errors

## Usage

### Manual Invocation
```bash
aws lambda invoke \
  --function-name scraper_lambdda \
  --payload '{"target_date": "12/15/2024"}' \
  response.json
```

### Event Payload
```json
{
  "target_date": "12/15/2024"  // Optional, defaults to previous day
}
```

### Response Format
```json
{
  "statusCode": 200,
  "body": {
    "message": "Successfully scraped 5 AWS blog posts",
    "posts": [
      {
        "id": "uuid-string",
        "title": "Post Title",
        "url": "https://aws.amazon.com/blogs/...",
        "author": "Author Name",
        "date": "12/15/2024",
        "description": "Post description..."
      }
    ]
  }
}
```

## Configuration

### Browser Settings
The scraper uses optimized Chrome arguments for Lambda environment:
- `--no-sandbox` - Required for Lambda
- `--single-process` - Memory optimization
- `--disable-dev-shm-usage` - Shared memory optimization
- `--disable-gpu` - GPU acceleration disabled

### Scraping Parameters
- `max_loads`: Maximum pagination iterations (default: 50)
- `timeout`: Page load timeout in milliseconds (default: 60000)
- `target_date`: Date to scrape posts for (MM/DD/YYYY format)

## Dependencies

### Python Packages
```
boto3>=1.34.0
playwright==1.45.0
```

### System Dependencies
- Chromium browser (installed via Playwright)
- Required system libraries for headless browsing

## Deployment Considerations

### Lambda Configuration
- **Runtime**: Python 3.10
- **Memory**: 512MB minimum (for Playwright)
- **Timeout**: 5 minutes
- **Architecture**: x86_64


### Permissions Required
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:BatchWriteItem"
      ],
      "Resource": "arn:aws:dynamodb:region:account:table/suo-aws-posts"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

## Monitoring

### CloudWatch Metrics
- Function duration and memory usage
- Error rates and success rates
- DynamoDB write capacity consumption

### Custom Metrics
- Number of posts scraped per execution
- Pagination iterations performed
- Browser initialization time

### Alarms
- Function errors > 5% error rate
- Function duration > 4 minutes
- DynamoDB throttling events
