import json
import os
import logging
import boto3
import uuid
import asyncio
from datetime import datetime, timedelta

from manual_extractor import BlogScraper

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# Initialize clients
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
posts_table = dynamodb.Table(os.environ.get('POSTS_TABLE', 'suo-aws-posts'))
# Ensure the POSTS_TABLE environment variable is set
if not posts_table:
    raise ValueError("Environment variable 'POSTS_TABLE' is not set. Please set it to your DynamoDB table name.")


# Add logging to help debug
logger.info(f"Using DynamoDB table: {posts_table}")



AWS_BLOG_URL = "https://aws.amazon.com/blogs/?awsf.blog-master-category=*all&awsf.blog-master-learning-levels=*all&awsf.blog-master-industry=*all&awsf.blog-master-analytics-products=*all&awsf.blog-master-artificial-intelligence=*all&awsf.blog-master-aws-cloud-financial-management=*all&awsf.blog-master-blockchain=*all&awsf.blog-master-business-applications=*all&awsf.blog-master-compute=*all&awsf.blog-master-customer-enablement=*all&awsf.blog-master-customer-engagement=*all&awsf.blog-master-database=*all&awsf.blog-master-developer-tools=*all&awsf.blog-master-devops=*all&awsf.blog-master-end-user-computing=*all&awsf.blog-master-mobile=*all&awsf.blog-master-iot=*all&awsf.blog-master-management-governance=*all&awsf.blog-master-media-services=*all&awsf.blog-master-migration-transfer=*all&awsf.blog-master-migration-solutions=*all&awsf.blog-master-networking-content-delivery=*all&awsf.blog-master-programming-language=*all&awsf.blog-master-sector=*all&awsf.blog-master-security=*all&awsf.blog-master-storage=*all"

async def get_blog_posts_for_date(target_date: str, url: str) -> list[dict[str, str]]:
    async with BlogScraper(target_date=target_date) as scraper:
        return await scraper.get_blog_posts_for_date(url)

def get_posts_by_date(date: str) -> list[dict[str, str]]:
    response = posts_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr('date').eq(date)
    )
    return response.get('Items', [])

def save_posts_to_dynamodb(posts):
    with posts_table.batch_writer() as batch:
        for post in posts:
            try:
                # Add ID if not present
                if 'id' not in post:
                    post['id'] = str(uuid.uuid4())
                batch.put_item(Item=post)
                logger.info(f"Saved post: {post['title']}")
            except Exception as e:
                logger.error(f"Error saving post to DynamoDB: {str(e)}")

def get_previous_date():
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%m/%d/%Y")

def lambda_handler(event, context):
    """Lambda handler function"""
    logger.info("Starting AWS Blog scraper")
    
    try:
        # Scrape AWS Blog
        # get the date from event object if not available use current date
        target_date = event['target_date'] if 'target_date' in event else None
        if target_date:
            logger.info(f"Target date provided: {target_date}")
        else:
            logger.info("No target date provided, using previous date")
            target_date = get_previous_date()
        
        existing_posts = get_posts_by_date(target_date)
        if existing_posts:
            logger.info(f"Found {len(existing_posts)} existing posts for the target date: {target_date}")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': f'Found {len(existing_posts)} existing posts for the target date: {target_date}',
                    'posts': existing_posts
                })
            }
        blog_posts = asyncio.run(get_blog_posts_for_date(target_date=target_date, url=AWS_BLOG_URL))
        logger.info("Finished AWS Blog scraper")
        if not blog_posts:
            logger.warning(f"No blog posts found for the target date: {target_date}")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': f'No blog posts found for the target date: {target_date}'
                })
            }
        
        # Save posts to DynamoDB
        save_posts_to_dynamodb(blog_posts)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully scraped {len(blog_posts)} AWS blog posts',
                'posts': blog_posts
            })
        }
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error scraping AWS blog: {str(e)}'
            })
        }
