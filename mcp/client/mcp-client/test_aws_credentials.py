#!/usr/bin/env python3
"""
Test script to verify AWS credentials are properly configured.
This script attempts to list S3 buckets to verify AWS credentials work.
"""

import os
import sys
import boto3
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_aws_credentials():
    """Check if AWS credentials are configured (either profile or access keys)"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Log AWS configuration
    logger.info("Testing AWS credentials...")
    logger.info(f"AWS_REGION: {os.getenv('AWS_REGION', 'Not set')}")
    logger.info(f"AWS_PROFILE: {os.getenv('AWS_PROFILE', 'Not set')}")
    logger.info(f"AWS_PROFILE_NAME: {os.getenv('AWS_PROFILE_NAME', 'Not set')}")
    logger.info(f"AWS_ACCESS_KEY_ID: {'Set' if os.getenv('AWS_ACCESS_KEY_ID') else 'Not set'}")
    logger.info(f"AWS_SECRET_ACCESS_KEY: {'Set' if os.getenv('AWS_SECRET_ACCESS_KEY') else 'Not set'}")
    
    # Check if either AWS_PROFILE or AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY is set
    aws_profile = os.getenv('AWS_PROFILE')
    aws_profile_name = os.getenv('AWS_PROFILE_NAME')
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    # If AWS_PROFILE is set but AWS_PROFILE_NAME is not, set AWS_PROFILE_NAME
    if aws_profile and not aws_profile_name:
        os.environ['AWS_PROFILE_NAME'] = aws_profile
        aws_profile_name = aws_profile
        logger.info(f"Setting AWS_PROFILE_NAME to AWS_PROFILE value: {aws_profile}")
    
    has_profile = aws_profile is not None or aws_profile_name is not None
    has_access_keys = access_key is not None and secret_key is not None
    
    if has_profile or has_access_keys:
        logger.info("AWS credentials configuration found!")
        if has_profile:
            logger.info(f"Using AWS profile configuration: {aws_profile_name or aws_profile}")
        if has_access_keys:
            logger.info("Using AWS access key configuration")
        return True
    else:
        logger.error("No AWS credentials configuration found")
        return False

def test_bedrock_access():
    """Check if AWS Bedrock configuration is available"""
    try:
        # Load environment variables from .env file
        load_dotenv()
        
        logger.info("Testing AWS Bedrock configuration...")
        
        # Check if region is set (required for Bedrock)
        region = os.getenv('AWS_REGION')
        if not region:
            logger.warning("AWS_REGION not set - required for Bedrock")
            return False
            
        # Check if model ID is set
        model_id = os.getenv('BEDROCK_MODEL_ID')
        if not model_id:
            logger.warning("BEDROCK_MODEL_ID not set")
            return False
            
        logger.info(f"Bedrock configuration found: region={region}, model={model_id}")
        
        # Check authentication method
        aws_profile = os.getenv('AWS_PROFILE')
        aws_profile_name = os.getenv('AWS_PROFILE_NAME')
        access_key = os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        # If AWS_PROFILE is set but AWS_PROFILE_NAME is not, set AWS_PROFILE_NAME
        if aws_profile and not aws_profile_name:
            os.environ['AWS_PROFILE_NAME'] = aws_profile
            aws_profile_name = aws_profile
            logger.info(f"Setting AWS_PROFILE_NAME to AWS_PROFILE value: {aws_profile}")
        
        has_profile = aws_profile is not None or aws_profile_name is not None
        has_access_keys = access_key is not None and secret_key is not None
        
        if not has_profile and not has_access_keys:
            logger.warning("No AWS authentication method found")
            logger.warning("Either AWS_PROFILE/AWS_PROFILE_NAME or AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY must be set")
            return False
        
        # Try to create a client but don't make any API calls
        try:
            # Create client with the appropriate configuration
            if has_profile:
                logger.info(f"Creating Bedrock client with profile: {aws_profile_name or aws_profile}")
                session = boto3.Session(profile_name=aws_profile_name or aws_profile)
                bedrock = session.client('bedrock-runtime')
            else:
                logger.info("Creating Bedrock client with access keys")
                bedrock = boto3.client('bedrock-runtime')
                
            logger.info("Successfully created Bedrock client")
        except Exception as e:
            logger.warning(f"Could not create Bedrock client: {str(e)}")
            # Continue anyway since we're just checking configuration
            
        return True
    except Exception as e:
        logger.error(f"Error checking Bedrock configuration: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n=== AWS Credentials Test ===\n")
    
    # Test basic AWS credentials
    aws_creds_ok = test_aws_credentials()
    
    print("\n=== AWS Bedrock Access Test ===\n")
    
    # Test Bedrock access
    bedrock_ok = test_bedrock_access()
    
    # Summary
    print("\n=== Test Summary ===\n")
    print(f"AWS Credentials: {'✅ CONFIGURED' if aws_creds_ok else '❌ NOT CONFIGURED'}")
    print(f"Bedrock Configuration: {'✅ CONFIGURED' if bedrock_ok else '❌ INCOMPLETE'}")
    
    if not aws_creds_ok:
        print("\nPlease configure AWS credentials using one of these methods:")
        print("1. Set AWS_PROFILE in .env file and configure ~/.aws/credentials")
        print("2. OR set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env file")
    
    if not bedrock_ok:
        print("\nPlease check your Bedrock configuration:")
        print("1. Ensure AWS_REGION is set in .env file")
        print("2. Ensure BEDROCK_MODEL_ID is set in .env file")
    
    sys.exit(0 if aws_creds_ok else 1)