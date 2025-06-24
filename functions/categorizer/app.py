import json
import os
import logging
import boto3
import uuid
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from batch_inference import run_batch_inference
from url_categorizer import get_category_from_url

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# Get region from environment or default to us-east-1
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Initialize clients - create them only when needed
dynamodb = None
posts_table_name = os.environ.get('POSTS_TABLE', 'suo-aws-posts')
categories_table_name = os.environ.get('CATEGORIES_TABLE', 'suo-categories')
bedrock_runtime = None

# Bedrock model ID - using same model for both operations
GENAI_MODEL: bool = os.environ.get('GENAI_MODEL', False)

# AWS service categories
MANUAL_CATEGORIES = ["architecture", "mt", "gametech", "aws-insights", "awsmarketplace", "aws", "apn", "smb", "big-data", "business-intelligence", "business-productivity", "enterprise-strategy", "aws-cloud-financial-management", "compute", "containers", "database", "desktop-and-application-streaming", "developer", "devops", "mobile", "hpc", "ibm-redhat", "industries", "infrastructure-and-automation", "iot", "machine-learning", "media", "messaging-and-targeting", "modernizing-with-aws", "migration-and-modernization", "dotnet", "networking-and-content-delivery", "opensource", "publicsector", "quantum-computing", "robotics", "awsforsap", "security", "spatial", "startups", "storage", "supply-chain", "training-and-certification"]

def get_dynamodb_table(table_name):
    """Get DynamoDB table resource with lazy initialization"""
    global dynamodb
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', AWS_REGION)
    return dynamodb.Table(table_name)

def get_post(post_id=None, date=None):
    """Retrieve a post from DynamoDB by ID or scan for posts by date
    
    Args:
        post_id (str, optional): The ID of the post to retrieve
        date (str, optional): The date to scan for posts (format: YYYY-MM-DD)
        
    Returns:
        dict or list: A single post if post_id is provided, or a list of posts if date is provided
    """
    try:
        table = get_dynamodb_table(posts_table_name)
        
        if post_id:
            # Get a specific post by ID
            response = table.get_item(Key={'id': post_id})
            return response.get('Item')
        elif date:
            # Scan for posts with the given date
            response = table.scan(
                FilterExpression="begins_with(#date, :date_val) AND attribute_not_exists(#proc)",
                ExpressionAttributeNames={
                    '#date': 'date',
                    '#proc': 'processed'
                },
                ExpressionAttributeValues={
                    ':date_val': date
                }
            )
            return response.get('Items', [])
        else:
            logger.error("Either post_id or date must be provided")
            raise ValueError("Either post_id or date must be provided")
    except ClientError as e:
        error_msg = f"Error retrieving post(s): {str(e)}"
        logger.error(error_msg)
        raise

def update_post_single(post_id, category, summary):
    """Update a single post with category and summary"""
    try:
        table = get_dynamodb_table(posts_table_name)
        return table.update_item(
            Key={'id': post_id},
            UpdateExpression="set category=:c, summary=:s, #proc=:p",
            ExpressionAttributeValues={
                ':c': category,
                ':s': summary,
                ':p': True
            },
            ExpressionAttributeNames={
                '#proc': 'processed'
            },
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        logger.error(f"Error updating post {post_id}: {str(e)}")
        raise

def update_post_batch(posts_data):
    """Update multiple posts in batch with category and summary
    
    Args:
        posts_data (list): List of dictionaries containing post_id, category, and summary
    """
    if not posts_data:
        return []
    
    try:
        table = get_dynamodb_table(posts_table_name)
        
        # DynamoDB batch_writer can handle up to 25 items per batch
        batch_size = 25
        results = []
        
        for i in range(0, len(posts_data), batch_size):
            batch = posts_data[i:i + batch_size]
            
            with table.batch_writer() as batch_writer:
                for post_data in batch:
                    item = {
                        'id': post_data['id'],
                        'category': post_data['category'],
                        # 'summary': post_data['summary'],
                        'processed': True
                    }
                    
                    # Preserve existing data by getting the current item first
                    try:
                        current_item = table.get_item(Key={'id': post_data['id']})
                        if 'Item' in current_item:
                            item.update(current_item['Item'])
                            item['category'] = post_data['category']
                            # item['summary'] = post_data['summary']
                            item['processed'] = True
                    except Exception as e:
                        logger.warning(f"Could not retrieve existing data for {post_data['id']}: {str(e)}")

                    batch_writer.put_item(Item=item)
                    results.append(post_data['id'])

            logger.info(f"Updated batch of {len(batch)} posts")
            
        return results
        
    except ClientError as e:
        logger.error(f"Error in batch update: {str(e)}")
        raise

def update_post(post_id=None, category=None, summary=None, posts_data=None):
    """Update post(s) with category and summary - supports both single and batch operations
    
    Args:
        post_id (str, optional): Single post ID to update
        category (str, optional): Category for single post
        summary (str, optional): Summary for single post
        posts_data (list, optional): List of post data for batch update
    """
    if posts_data:
        # Batch update
        return update_post_batch(posts_data)
    elif post_id and category is not None and summary is not None:
        # Single update
        return update_post_single(post_id, category, summary)
    else:
        raise ValueError("Either provide post_id with category and summary, or provide posts_data for batch update")

# create a function that saves a list of categories for a day to category table called suo-category. with an id, date in this format mm/dd/yyyy, and categories as a list of strings

def save_categories_for_date(date, categories:list[str]):
    """Save categories for a specific date to the suo-category table"""
    try:
        table = get_dynamodb_table(categories_table_name)
        item = {
            'id': str(uuid.uuid4()),
            'date': date,
            'categories': categories
        }
        table.put_item(Item=item)
    except Exception as e:
        logger.error(f"Error saving categories for date {date}: {str(e)}")
        raise

def get_previous_date():
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%m/%d/%Y")

def lambda_handler(event, context):
    """Lambda handler function"""
    logger.info("Starting post categorization and summarization")
    
    try:
        # Check processing mode
        date = event.get('date') if not 'date' in event else get_previous_date()


        if GENAI_MODEL:
            print(f"Using GENAI model for batch inference: {GENAI_MODEL}")
            logger.info(f"Running batch inference for date: {date}")
            posts = run_batch_inference(date=date, limit=10)
            
            if not posts:
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': f'No unprocessed posts found for date {date}'})
                }
            
            return {
                'statusCode': 200,
                'body': json.dumps(posts, indent=2)
            }
        else:
            logger.info(f"Categorizing posts manually for date: {date}")
            posts = get_post(date=date)
            if not posts:
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': f'No unprocessed posts found for date {date}'})
                }
            update_post, categories = get_category_from_url(posts)
            save_categories_for_date(date, categories)
            update_post_batch(posts_data=update_post)
            return {
                'statusCode': 200,
                'body': json.dumps({'posts': update_post, 'categories': categories})
            }
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error processing post: {str(e)}'})
        }
    
# For local testing  
if __name__ == "__main__":
    # Test with a specific post ID
    # test_event_single = {
    #     'post_id': '09de2dd9-6414-48ed-8366-203160430b91'
    # }
    # print("Testing with single post ID:")
    # print(lambda_handler(test_event_single, None))
    
    # Test with a date
    test_event_date = {
        'date': '06/19/2025'  # Example date format
    }
    print("\nTesting with date:")
    print(lambda_handler(test_event_date, None))
