# SUO-AWS Documentation Overview

## 📚 Complete Documentation Structure

This document provides an overview of all documentation created for the SUO-AWS project. Each component has detailed README files with comprehensive explanations.

## 🏗️ Architecture Summary

SUO-AWS is a serverless AWS news subscription platform that:

1. **Scrapes** AWS blog posts daily using Playwright
2. **Categorizes** posts using URL patterns or AI (Amazon Bedrock - Amazon Nova Pro Model)
3. **Notifies** subscribed users via personalized emails (Google mail only- for now)
4. **Manages** subscriptions through a serverless API

Visit the website here: [Link](https://suo-aws.vercel.app/)

## 📋 Documentation Files

### Main Documentation
- **[README.md](./README.md)** - Main project documentation with architecture overview, deployment instructions, and usage examples

## Testing Documentation
 Please refer to the README.md file
- **[./Manual_README.md](./Manual_README.md)** - Manual Testing guide


### Function Documentation
- **[functions/scraper/README.md](./functions/scraper/README.md)** - Web scraping function using Playwright
- **[functions/categorizer/README.md](./functions/categorizer/README.md)** - AI/URL-based categorization function
- **[functions/notifier/README.md](./functions/notifier/README.md)** - Email notification function
- **[functions/subscribe/README.md](./functions/subscribe/README.md)** - Subscription management API

## 🔧 AWS Services Used

### Core Services
| Service | Purpose | Configuration |
|---------|---------|---------------|
| **AWS Lambda** | Function execution | Python 3.10, Node.js 18.x |
| **Amazon DynamoDB** | Data storage | 3 tables, on-demand billing |
| **Amazon Bedrock** | AI categorization | Nova Lite model |
| **Amazon S3** | Batch processing | Auto-created buckets |
| **API Gateway** | REST API | Direct DynamoDB integration |
| **Amazon SNS** | Error notifications |
| **Amazon Step Function** | Orchestrate functions workflow  | 
| **Amazon EventBridge Scheduler** | Recurring, cron-based daily scheduler  | 
| **Amazon Q** | Documentation and Scripting.  | 

### Supporting Services
- **CloudWatch** - Logging and monitoring
- **IAM** - Permissions and roles
- **SMTP** - Email delivery
- **EventBridge** - Scheduling (optional)

## 📊 Function Details

### Scraper Function
- **Runtime**: Python 3.10
- **Memory**: 512MB
- **Timeout**: 5 minutes
- **Key Features**: Playwright automation, pagination handling, duplicate detection
- **Output**: Raw blog post data in DynamoDB

### Categorizer Function
- **Runtime**: Python 3.10
- **Memory**: 128MB (URL) / 256MB (AI)
- **Timeout**: 30 seconds (URL) / 15 minutes (AI)
- **Key Features**: Dual processing modes, batch AI inference, category mapping
- **Output**: Categorized posts with optional summaries

### Notifier Function
- **Runtime**: Node.js 18.x
- **Memory**: 128MB
- **Timeout**: 5 minutes
- **Key Features**: SMTP integration, personalized emails, error handling
- **Output**: Email notifications to subscribed users

### Subscribe API
- **Type**: Lambda Function Url + Lambda + DynamoDB
- **No Lambda**: Direct integration for cost efficiency
- **Key Features**: Request validation, CORS support, error handling
- **Output**: User subscription records

## 🔍 Monitoring & Troubleshooting

### CloudWatch Dashboards
Each function includes monitoring guidance for:
- Function performance metrics
- Error rates and patterns
- Resource utilization
- Custom business metrics

## 💰 Cost Optimization

### Estimated Monthly Costs (100 daily posts, 1000 users)
- **Lambda**: $5-15 (execution time dependent)
- **DynamoDB**: $2-5 (on-demand billing)
- **API Gateway**: $1-3 (request volume)
- **Bedrock**: $10-30 (if AI mode enabled)
- **S3**: $1-2 (batch processing)
- **Total**: ~$20-55/month

## 🚀 Deployment Environments

### Development
- Single region deployment
- Reduced memory allocations
- Debug logging enabled
- Manual testing workflows

### Production
- Multi-region deployment
- Optimized resource allocation
- Error alerting configured
- Automated testing and deployment

## 📈 Scaling Considerations

### Current Limits
- Lambda concurrent executions: 1000 (default)
- DynamoDB throughput: On-demand (auto-scaling)
- API Gateway: 10,000 requests/second
- Bedrock: Model-specific quotas

## 📞 Support & Troubleshooting

### Documentation Hierarchy
1. Function-specific README files (detailed technical docs)
2. Main README (architecture and deployment)
3. This overview (quick reference and summaries)
4. CloudWatch logs (runtime debugging)

### Getting Help
- Check function-specific README for detailed troubleshooting
- Review CloudWatch logs for error details
- Use AWS CLI for manual testing and validation
- Monitor CloudWatch metrics for performance insights

---

*This documentation provides comprehensive coverage of the SUO-AWS platform. Each function's README contains detailed technical information, while this overview provides quick reference and architectural understanding.*