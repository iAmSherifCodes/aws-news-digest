# SUO-AWS Documentation Overview

## 📚 Complete Documentation Structure

This document provides an overview of all documentation created for the SUO-AWS project. Each component has detailed README files with comprehensive explanations.

## 🏗️ Architecture Summary

SUO-AWS is a serverless AWS news subscription platform that:

1. **Scrapes** AWS blog posts daily using Playwright
2. **Categorizes** posts using URL patterns or AI (Amazon Bedrock - Amazon Nova Pro Model)
3. **Notifies** subscribed users via personalized emails (Google mail only- for now)
4. **Manages** subscriptions through a serverless API

## 📋 Documentation Files

### Main Documentation
- **[README.md](./README.md)** - Main project documentation with architecture overview, deployment instructions, and usage examples

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
| **Amazon SNS** | Error notifications | FIFO topic |

### Supporting Services
- **CloudWatch** - Logging and monitoring
- **IAM** - Permissions and roles
- **SES/SMTP** - Email delivery
- **EventBridge** - Scheduling (optional)

## 🚀 Quick Start Guide

### 1. Prerequisites
```bash
# Install required tools
npm install -g aws-sam-cli
pip install playwright
playwright install chromium
```

### 2. Deploy Infrastructure
```bash
# Build and deploy
sam build
sam deploy --guided

# Deploy subscription API (optional)
cd functions/subscribe
./deploy-direct-integration.sh
```

### 3. Configure Email
```bash
# Set email credentials
aws lambda update-function-configuration \
  --function-name suo-aws-notifier \
  --environment Variables='{
    EMAIL_USER=your-email@gmail.com,
    EMAIL_PASS=your-app-password,
    FROM_EMAIL=your-email@gmail.com
  }'
```

### 4. Test Functions
```bash
# Test scraper
aws lambda invoke --function-name suo-aws-scraper --payload '{}' response.json

# Test categorizer  
aws lambda invoke --function-name suo-aws-categorizer --payload '{}' response.json

# Test notifier
aws lambda invoke --function-name suo-aws-notifier --payload '{}' response.json
```

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
- **Type**: API Gateway + DynamoDB
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

### Common Issues & Solutions

**Scraper Issues:**
- Browser initialization failures → Increase memory
- Timeout errors → Check network connectivity
- Missing posts → Verify date format and URL patterns

**Categorizer Issues:**
- AI model access → Check Bedrock permissions
- Batch job failures → Review S3 bucket permissions
- URL categorization → Update category mappings

**Notifier Issues:**
- Email delivery failures → Verify SMTP credentials
- No emails sent → Check user subscription data
- Template errors → Review HTML/text formatting

**API Issues:**
- CORS errors → Verify OPTIONS method deployment
- Validation errors → Check JSON schema compliance
- DynamoDB errors → Review IAM permissions

## 💰 Cost Optimization

### Estimated Monthly Costs (100 daily posts, 1000 users)
- **Lambda**: $5-15 (execution time dependent)
- **DynamoDB**: $2-5 (on-demand billing)
- **API Gateway**: $1-3 (request volume)
- **Bedrock**: $10-30 (if AI mode enabled)
- **S3**: $1-2 (batch processing)
- **Total**: ~$20-55/month

### Cost Reduction Strategies
- Use URL categorization instead of AI for cost savings
- Implement user engagement tracking
- Archive old posts to reduce storage costs
- Optimize Lambda memory allocation
- Use reserved capacity for predictable workloads

## 🔒 Security Best Practices

### Implemented Security
- IAM roles with least privilege
- Input validation and sanitization
- HTTPS-only API endpoints
- Encrypted data at rest (DynamoDB)
- VTL template injection prevention

### Additional Recommendations
- Store email credentials in Secrets Manager
- Implement API rate limiting
- Add WAF protection for public APIs
- Enable CloudTrail for audit logging
- Use VPC endpoints for internal communication

## 🚀 Deployment Environments

### Development
- Single region deployment
- Reduced memory allocations
- Debug logging enabled
- Manual testing workflows

### Production
- Multi-region deployment (optional)
- Optimized resource allocation
- Error alerting configured
- Automated testing and deployment

## 📈 Scaling Considerations

### Current Limits
- Lambda concurrent executions: 1000 (default)
- DynamoDB throughput: On-demand (auto-scaling)
- API Gateway: 10,000 requests/second
- Bedrock: Model-specific quotas

### Scaling Strategies
- Implement reserved concurrency for critical functions
- Use DynamoDB Global Tables for multi-region
- Add CloudFront for API caching
- Consider Step Functions for complex workflows

## 🔄 Maintenance Tasks

### Regular Maintenance
- Monitor CloudWatch alarms
- Review and rotate access keys
- Update dependencies and runtime versions
- Archive old blog posts
- Clean up unused S3 objects

### Quarterly Reviews
- Analyze cost optimization opportunities
- Review user engagement metrics
- Update AWS service category mappings
- Performance optimization assessment
- Security audit and updates

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