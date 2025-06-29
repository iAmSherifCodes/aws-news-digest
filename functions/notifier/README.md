# AWS Blog Notifier Function

## Overview

The Notifier function is responsible for sending personalized email notifications to subscribed users based on their selected AWS service categories. It retrieves categorized blog posts, matches them with user preferences, and delivers formatted email notifications using SMTP.

### AWS Services
- AWS Serverless Application Model (AWS SAM)
- AWS Lambda (NodeJs runtime)
- Amazon DynamoDB (data retrieval)
- Amazon SNS (error notifications)
- AWS IAM (service roles)
- Amazon CloudWatch (monitoring and logging)

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   DynamoDB      │───▶│   Notifier       │───▶│   SMTP Server   │
│ (Posts/Users)   │    │    Lambda        │    │   (Gmail)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Amazon SNS    │
                       │ (Error Alerts)  │
                       └─────────────────┘
```

## Files

### `app.js`
Main Lambda handler (Node.js) that orchestrates the notification process.

**Key Functions:**
- `handler(event, context)` - Main entry point
- `getPostsByDate(date)` - Retrieve posts for specific date
- `getSubscribedUsers(categories)` - Get users subscribed to relevant categories
- `getCategoriesByDate(date)` - Retrieve daily category summary
- `sendCategorizedNewsToSubscribers(posts, subscribers)` - Send personalized emails
- `sendErrorNotification(error, context)` - Send error alerts via SNS
- `getPreviousDate()` - Date utility function

**Environment Variables:**
- `POSTS_TABLE` - DynamoDB table for blog posts
- `USERS_TABLE` - DynamoDB table for user subscriptions
- `CATEGORIES_TABLE` - DynamoDB table for category summaries
- `FROM_EMAIL` - Sender email address
- `SNS_TOPIC_ARN` - SNS topic for error notifications
- `EMAIL_SERVICE` - Email service provider (gmail, ses)
- `EMAIL_USER` - SMTP username
- `EMAIL_PASS` - SMTP password/app password

### `mail_setup.js`
Email configuration and sending functionality using Nodemailer.

**Key Functions:**
- `sendEmail(from_name, from_email, to_name, to_email, subject, text, html)` - Send email
- Nodemailer transporter configuration
- Support for multiple email providers (Gmail, SES, custom SMTP)

**Features:**
- HTML and plain text email support
- Configurable SMTP settings
- Error handling and logging
- Support for app passwords and OAuth

## Features

### Personalized Email Delivery
- Category-based content filtering
- User preference matching
- HTML and plain text email formats
- Personalized subject lines with date

### Multi-Provider Email Support
- Gmail SMTP integration
- Custom SMTP server configuration
- App password authentication

### Error Handling & Monitoring
- SNS error notifications
- Comprehensive logging
- Graceful failure handling
- User activity status checking

### Content Formatting
- Clean HTML email templates
- Plain text fallback
- Clickable links to original posts
- Organized by categories

## Usage

### Manual Invocation
```bash
aws lambda invoke \
  --function-name suo-aws-notifier \
  --payload '{}' \
  response.json
```

### Event Payload
```json
{
  // No payload required - uses previous day by default
}
```

### Response Format
```json
{
  "statusCode": 200,
  "body": {
    "message": "Found 5 posts and 3 subscribed users",
    "date": "12/15/2024"
  }
}
```

## Email Templates

### HTML Template
```html
<li>
  <strong>Post Title</strong><br>
  Post description text...<br>
  <a href="https://aws.amazon.com/blogs/...">Read more</a>
</li>
```

### Plain Text Template
```
• Post Title
Post description text...
```

### Subject Line Format
```
SUO-AWS Daily News: 12/15/2024
```

## User Subscription Matching

### Category Matching Logic
1. Retrieve posts for target date
2. Get daily category summary
3. Find users subscribed to any of the day's categories
4. Filter posts by user's category preferences
5. Group posts by category for each user
6. Send personalized email with matched content

### User Data Structure
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "name": "User Name",
  "categories": ["compute", "serverless", "ai-ml"],
  "active": true,
  "created_at": "2024-12-15T10:00:00Z"
}
```

## Dependencies

### Node.js Packages
```json
{
  "@aws-sdk/client-dynamodb": "^3.0.0",
  "@aws-sdk/lib-dynamodb": "^3.0.0",
  "@aws-sdk/client-sns": "^3.0.0",
  "nodemailer": "^6.9.0"
}
```

## Deployment Considerations

### Lambda Configuration
- **Runtime**: Node.js 18.x
- **Memory**: 128MB
- **Timeout**: 2 minutes
- **Architecture**: x86_64

### Permissions Required
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:Scan",
        "dynamodb:GetItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/suo-aws-posts",
        "arn:aws:dynamodb:*:*:table/aws-suo-users",
        "arn:aws:dynamodb:*:*:table/suo-categories"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:*:*:SuoAwsErrorNotifier*"
    }
  ]
}
```

### Security Considerations
- Store email credentials in AWS Secrets Manager
- Use IAM roles instead of hardcoded credentials
- Enable VPC endpoints for DynamoDB access
- Implement rate limiting for email sending

## Monitoring

### CloudWatch Metrics
- Function duration and memory usage
- Email delivery success/failure rates
- DynamoDB read capacity consumption
- SNS message publication counts

### Custom Metrics
- Number of emails sent per execution
- User engagement rates
- Category popularity
- Email bounce/complaint rates

### Alarms
- Function errors > 5% error rate
- Email delivery failures
- DynamoDB throttling events
- SNS delivery failures

*Built with ❤️ using AWS Serverless technologies*