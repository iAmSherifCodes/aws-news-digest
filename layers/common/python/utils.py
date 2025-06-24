import json
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()

def get_dynamodb_item(table_name, key):
    """Get an item from DynamoDB"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    try:
        response = table.get_item(Key=key)
        return response.get('Item')
    except ClientError as e:
        logger.error(f"Error getting item from {table_name}: {str(e)}")
        return None

def put_dynamodb_item(table_name, item):
    """Put an item into DynamoDB"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    try:
        response = table.put_item(Item=item)
        return True
    except ClientError as e:
        logger.error(f"Error putting item into {table_name}: {str(e)}")
        return False

def update_dynamodb_item(table_name, key, update_expression, expression_values):
    """Update an item in DynamoDB"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    try:
        response = table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues="UPDATED_NEW"
        )
        return response
    except ClientError as e:
        logger.error(f"Error updating item in {table_name}: {str(e)}")
        return None

def send_sns_message(topic_arn, subject, message, message_attributes=None):
    """Send a message to an SNS topic"""
    sns = boto3.client('sns')
    
    try:
        params = {
            'TopicArn': topic_arn,
            'Message': message,
            'Subject': subject
        }
        
        if message_attributes:
            params['MessageAttributes'] = message_attributes
            
        response = sns.publish(**params)
        return response
    except ClientError as e:
        logger.error(f"Error sending message to SNS topic {topic_arn}: {str(e)}")
        return None