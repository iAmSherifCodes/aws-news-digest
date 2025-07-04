import json
import os
import logging
import boto3
import time
from datetime import datetime
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

AWS_REGION = os.environ.get('AWS_REGION')

# Initialize clients
dynamodb = None
posts_table_name = os.environ.get('POSTS_TABLE')
bedrock = None
s3 = None

# Bedrock model ID for batch inference
NOVA_MODEL = os.environ.get('BEDROCK_MODEL_ID')

# S3 configuration
def get_bucket_name():
    """Generate a unique bucket name using account ID"""
    try:
        sts = boto3.client('sts', AWS_REGION)
        account_id = sts.get_caller_identity()['Account']
        base_name = os.environ.get('BATCH_BUCKET', 'aws-news-batch-inference')
        return f"{base_name}-{account_id}"
    except Exception:
        # Fallback to environment variable or default
        return os.environ.get('BATCH_BUCKET', 'aws-news-batch-inference-default')

BUCKET_NAME = get_bucket_name()
BATCH_PREFIX = os.environ.get('BATCH_PREFIX', 'batch-inference')

# AWS service categories
AWS_CATEGORIES = [
    "Serverless", "Storage", "Database", "Networking", "Security", 
    "AI/ML", "Analytics", "Compute", "Containers", "IoT",
    "Management Tools", "Developer Tools", "Mobile", "Media Services",
    "Integration", "Blockchain", "Business Applications", "End User Computing",
    "Game Development", "Quantum Computing"
]

def get_clients():
    """Initialize AWS clients with lazy loading"""
    global dynamodb, bedrock, s3
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', AWS_REGION)
    if not bedrock:
        bedrock = boto3.client('bedrock', AWS_REGION)
    if not s3:
        s3 = boto3.client('s3', AWS_REGION)
    return dynamodb, bedrock, s3

def get_posts_for_batch(date=None, limit=100):
    """Retrieve unprocessed posts for batch inference"""
    try:
        dynamodb, _, _ = get_clients()
        table = dynamodb.Table(posts_table_name)
        
        if date:
            response = table.scan(
                FilterExpression="begins_with(#date, :date_val) AND attribute_not_exists(#proc)",
                ExpressionAttributeNames={
                    '#date': 'date',
                    '#proc': 'processed'
                },
                ExpressionAttributeValues={
                    ':date_val': date
                },
                Limit=limit
            )
        else:
            response = table.scan(
                FilterExpression="attribute_not_exists(#proc)",
                ExpressionAttributeNames={
                    '#proc': 'processed'
                },
                Limit=limit
            )
        
        return response.get('Items', [])
    except ClientError as e:
        logger.error(f"Error retrieving posts: {str(e)}")
        raise

def create_batch_input_file(posts, job_name):
    """Create JSONL input file for batch inference"""
    categorization_file = f"{job_name}_categorization.jsonl"
    summarization_file = f"{job_name}_summarization.jsonl"
    
    # Create categorization batch input
    with open(categorization_file, 'w', encoding='utf-8') as cat_file:
        for post in posts:
            title = post.get('title', '')
            description = post.get('description', '')[:1000]  # Limit content size
            
            prompt = f"""You are an AWS expert. Analyze this AWS blog post and determine which AWS service categories it belongs to.
Choose from these categories: {', '.join(AWS_CATEGORIES)} only.
Each category should be relevant to the content of the post.
If the post does not fit any of these categories, return 'Uncategorized'.
If the post fits multiple categories, return the most relevant ones.
You can select multiple categories if applicable, but limit to the 3 most relevant ones.

Blog post title: {title}
Blog post content: {description}

Return only the category names separated by commas, nothing else."""
            
            message_list = [{
                "role": "user",
                "content": [{"text": prompt}]
            }]
            
            inf_params = {
                "max_new_tokens": 100,
                "top_p": 0.9,
                "top_k": 20,
                "temperature": 0
            }
            
            record = {
                "recordId": f"{post['id']}_cat",
                "modelInput": {
                    "schemaVersion": "messages-v1",
                    "messages": message_list,
                    "inferenceConfig": inf_params
                }
            }
            
            json.dump(record, cat_file, ensure_ascii=False)
            cat_file.write('\n')
    
    # Create summarization batch input
    with open(summarization_file, 'w', encoding='utf-8') as sum_file:
        for post in posts:
            title = post.get('title', '')
            description = post.get('description', '')[:2000]  # Limit content size
            
            prompt = f"""You are an AWS expert. Create a concise summary (maximum 5 sentences) of this AWS blog post.
Focus on the key announcements, features, or changes described.

Blog post title: {title}
Blog post content: {description}

Return only the summary, nothing else."""
            
            message_list = [{
                "role": "user",
                "content": [{"text": prompt}]
            }]
            
            inf_params = {
                "max_new_tokens": 300,
                "top_p": 0.9,
                "top_k": 20,
                "temperature": 0
            }
            
            record = {
                "recordId": f"{post['id']}_sum",
                "modelInput": {
                    "schemaVersion": "messages-v1",
                    "messages": message_list,
                    "inferenceConfig": inf_params
                }
            }
            
            json.dump(record, sum_file, ensure_ascii=False)
            sum_file.write('\n')
    
    return categorization_file, summarization_file

def ensure_bucket_exists(bucket_name):
    """Create S3 bucket if it doesn't exist"""
    try:
        _, _, s3_client = get_clients()
        
        # Check if bucket exists
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            logger.info(f"Bucket {bucket_name} already exists")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    if AWS_REGION == 'us-east-1':
                        # us-east-1 doesn't need LocationConstraint
                        s3_client.create_bucket(Bucket=bucket_name)
                    else:
                        s3_client.create_bucket(
                            Bucket=bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
                        )
                    logger.info(f"Created bucket {bucket_name}")
                    return True
                except Exception as create_error:
                    logger.error(f"Error creating bucket {bucket_name}: {create_error}")
                    return False
            else:
                logger.error(f"Error checking bucket {bucket_name}: {e}")
                return False
    except Exception as e:
        logger.error(f"Error ensuring bucket exists: {e}")
        return False

def upload_to_s3(file_path, bucket_name, s3_key):
    """Upload file to S3"""
    try:
        # Ensure bucket exists first
        if not ensure_bucket_exists(bucket_name):
            return False
            
        _, _, s3_client = get_clients()
        s3_client.upload_file(file_path, bucket_name, s3_key)
        logger.info(f"Successfully uploaded {file_path} to s3://{bucket_name}/{s3_key}")
        return True
    except Exception as e:
        logger.error(f"Error uploading {file_path} to S3: {e}")
        return False

def create_service_role():
    """Create IAM service role for Bedrock batch inference"""
    try:
        iam = boto3.client('iam', AWS_REGION)
        sts = boto3.client('sts', AWS_REGION)
        account_id = sts.get_caller_identity()['Account']
        
        role_name = os.environ.get('BATCH_ROLE_NAME', 'AWSNewsBatchInferenceRole')
        
        # Check if role exists
        try:
            existing_role = iam.get_role(RoleName=role_name)
            logger.info(f"Role '{role_name}' already exists")
            return existing_role['Role']['Arn']
        except iam.exceptions.NoSuchEntityException:
            pass
        
        # Trust relationship
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "bedrock.amazonaws.com"},
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {"aws:SourceAccount": account_id},
                    "ArnEquals": {"aws:SourceArn": f"arn:aws:bedrock:{AWS_REGION}:{account_id}:model-invocation-job/*"}
                }
            }]
        }
        
        # S3 permissions
        s3_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                "Resource": [f"arn:aws:s3:::{BUCKET_NAME}", f"arn:aws:s3:::{BUCKET_NAME}/*"],
                "Condition": {"StringEquals": {"aws:ResourceAccount": account_id}}
            }]
        }
        
        # Create role
        create_response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Service role for AWS News Batch Inference"
        )
        
        # Attach policy
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName="BatchInferenceS3Policy",
            PolicyDocument=json.dumps(s3_policy)
        )
        
        logger.info(f"Created role: {create_response['Role']['Arn']}")
        return create_response['Role']['Arn']
        
    except Exception as e:
        logger.error(f"Error creating service role: {str(e)}")
        raise

def submit_batch_job(input_s3_uri, output_s3_uri, job_name, role_arn):
    """Submit batch inference job to Bedrock"""
    try:
        _, bedrock_client, _ = get_clients()
        
        input_config = {
            "s3InputDataConfig": {"s3Uri": input_s3_uri}
        }
        
        output_config = {
            "s3OutputDataConfig": {"s3Uri": output_s3_uri}
        }
        
        response = bedrock_client.create_model_invocation_job(
            roleArn=role_arn,
            modelId=NOVA_MODEL,
            jobName=job_name,
            inputDataConfig=input_config,
            outputDataConfig=output_config
        )
        
        logger.info(f"Submitted batch job: {response['jobArn']}")
        return response['jobArn']
        
    except Exception as e:
        logger.error(f"Error submitting batch job: {str(e)}")
        raise

def monitor_batch_job(job_arn, max_wait_minutes=60):
    """Monitor batch job status"""
    try:
        _, bedrock_client, _ = get_clients()
        
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        
        while True:
            response = bedrock_client.get_model_invocation_job(jobIdentifier=job_arn)
            status = response['status']
            
            logger.info(f"Job status: {status}")
            
            if status == 'Completed':
                return True
            elif status == 'Failed':
                logger.error(f"Job failed: {response}")
                return False
            
            # Check timeout
            if time.time() - start_time > max_wait_seconds:
                logger.warning(f"Job monitoring timeout after {max_wait_minutes} minutes")
                return False
            
            time.sleep(60)  # Wait 1 minute between checks
            
    except Exception as e:
        logger.error(f"Error monitoring batch job: {str(e)}")
        return False

def download_and_parse_results(job_arn, output_s3_prefix):
    """Download and parse batch inference results"""
    try:
        _, _, s3_client = get_clients()
        
        job_id = job_arn.split('/')[-1]
        
        # Download categorization results
        cat_key = f"{output_s3_prefix}/{job_id}/categorization.jsonl.out"
        sum_key = f"{output_s3_prefix}/{job_id}/summarization.jsonl.out"
        
        results = {}
        
        # Parse categorization results
        try:
            cat_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=cat_key)
            cat_content = cat_obj['Body'].read().decode('utf-8')
            
            for line in cat_content.strip().split('\n'):
                if line:
                    data = json.loads(line)
                    record_id = data['recordId']
                    post_id = record_id.replace('_cat', '')
                    
                    if post_id not in results:
                        results[post_id] = {}
                    
                    output_text = data['modelOutput']['output']['message']['content'][0]['text']
                    categories = [cat.strip() for cat in output_text.split(',')]
                    results[post_id]['categories'] = categories
                    
        except Exception as e:
            logger.error(f"Error parsing categorization results: {e}")
        
        # Parse summarization results
        try:
            sum_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=sum_key)
            sum_content = sum_obj['Body'].read().decode('utf-8')
            
            for line in sum_content.strip().split('\n'):
                if line:
                    data = json.loads(line)
                    record_id = data['recordId']
                    post_id = record_id.replace('_sum', '')
                    
                    if post_id not in results:
                        results[post_id] = {}
                    
                    summary = data['modelOutput']['output']['message']['content'][0]['text']
                    results[post_id]['summary'] = summary
                    
        except Exception as e:
            logger.error(f"Error parsing summarization results: {e}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error downloading results: {str(e)}")
        return {}

def update_posts_with_results(results):
    """Update DynamoDB posts with batch inference results"""
    try:
        dynamodb, _, _ = get_clients()
        table = dynamodb.Table(posts_table_name)
        
        updated_count = 0
        
        with table.batch_writer() as batch:
            for post_id, data in results.items():
                categories = data.get('categories', ['Uncategorized'])
                summary = data.get('summary', 'Summary not available.')
                
                # Get existing post data
                try:
                    existing = table.get_item(Key={'id': post_id})
                    if 'Item' in existing:
                        item = existing['Item']
                        item['category'] = ','.join(categories)
                        item['summary'] = summary
                        item['processed'] = True
                        
                        batch.put_item(Item=item)
                        updated_count += 1
                        
                except Exception as e:
                    logger.error(f"Error updating post {post_id}: {e}")
        
        logger.info(f"Updated {updated_count} posts with batch results")
        return updated_count
        
    except Exception as e:
        logger.error(f"Error updating posts: {str(e)}")
        return 0

def run_batch_inference(date=None, limit=100):
    """Main function to run batch inference process"""
    try:
        # Get posts for processing
        posts = get_posts_for_batch(date, limit)
        if not posts:
            logger.info("No unprocessed posts found")
            return {"processed_count": 0, "message": "No posts to process"}
        
        logger.info(f"Found {len(posts)} posts for batch processing")
        
        # Create job name with timestamp
        date_obj = datetime.strptime(date, "%m/%d/%Y")
        timestamp = int(date_obj.timestamp())
        job_name_base = f"aws-news-batch-{timestamp}"
        
        # Create input files
        cat_file, sum_file = create_batch_input_file(posts, job_name_base)
        
        # Upload to S3
        job_prefix = f"{BATCH_PREFIX}/{job_name_base}"
        cat_s3_key = f"{job_prefix}/{cat_file}"
        sum_s3_key = f"{job_prefix}/{sum_file}"
        
        upload_to_s3(cat_file, BUCKET_NAME, cat_s3_key)
        upload_to_s3(sum_file, BUCKET_NAME, sum_s3_key)
        
        # Create service role
        role_arn = create_service_role()
        
        # Submit batch jobs
        cat_job_arn = submit_batch_job(
            f"s3://{BUCKET_NAME}/{cat_s3_key}",
            f"s3://{BUCKET_NAME}/{job_prefix}/output/",
            f"{job_name_base}_categorization",
            role_arn
        )
        
        sum_job_arn = submit_batch_job(
            f"s3://{BUCKET_NAME}/{sum_s3_key}",
            f"s3://{BUCKET_NAME}/{job_prefix}/output/",
            f"{job_name_base}_summarization",
            role_arn
        )
        
        # Monitor jobs
        logger.info("Monitoring batch jobs...")
        cat_success = monitor_batch_job(cat_job_arn)
        sum_success = monitor_batch_job(sum_job_arn)
        
        if not (cat_success and sum_success):
            return {"error": "One or more batch jobs failed"}
        
        # Download and parse results
        results = download_and_parse_results(cat_job_arn, f"{job_prefix}/output")
        
        # Update posts
        updated_count = update_posts_with_results(results)
        
        # Cleanup local files
        os.remove(cat_file)
        os.remove(sum_file)
        
        return {
            "processed_count": updated_count,
            "categorization_job": cat_job_arn,
            "summarization_job": sum_job_arn
        }
        
    except Exception as e:
        logger.error(f"Error in batch inference: {str(e)}")
        return {"error": str(e)}

# if __name__ == "__main__":
#     # Test batch inference
#     result = run_batch_inference(date="06/19/2025", limit=10)
#     print(json.dumps(result, indent=2))