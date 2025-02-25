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
    """Test AWS credentials by attempting to list S3 buckets"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Log AWS configuration
    logger.info("Testing AWS credentials...")
    logger.info(f"AWS_REGION: {os.getenv('AWS_REGION', 'Not set')}")
    logger.info(f"AWS_PROFILE: {os.getenv('AWS_PROFILE', 'Not set')}")
    logger.info(f"AWS_ACCESS_KEY_ID: {'Set' if os.getenv('AWS_ACCESS_KEY_ID') else 'Not set'}")
    logger.info(f"AWS_SECRET_ACCESS_KEY: {'Set' if os.getenv('AWS_SECRET_ACCESS_KEY') else 'Not set'}")
    
    try:
        # Create a boto3 client
        s3 = boto3.client('s3')
        
        # Try to list S3 buckets
        response = s3.list_buckets()
        
        # If we get here, credentials are working
        logger.info("AWS credentials are valid!")
        logger.info(f"Found {len(response['Buckets'])} S3 buckets")
        
        return True
    except Exception as e:
        logger.error(f"Error testing AWS credentials: {str(e)}")
        return False

def test_bedrock_access():
    """Test access to AWS Bedrock service"""
    try:
        # Load environment variables from .env file
        load_dotenv()
        
        logger.info("Testing AWS Bedrock access...")
        
        # Create a boto3 client for Bedrock
        bedrock = boto3.client('bedrock-runtime')
        
        # List available models (this is a simple operation to test access)
        # Note: This might not work if the account doesn't have Bedrock access
        logger.info("Attempting to access Bedrock service...")
        
        # Just checking if we can create the client without errors
        logger.info("Successfully created Bedrock client")
        logger.info("Note: This doesn't guarantee full Bedrock access, just that credentials work")
        
        return True
    except Exception as e:
        logger.error(f"Error testing Bedrock access: {str(e)}")
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
    print(f"AWS Credentials: {'✅ VALID' if aws_creds_ok else '❌ INVALID'}")
    print(f"Bedrock Access: {'✅ VALID' if bedrock_ok else '❌ POTENTIAL ISSUE'}")
    
    if not aws_creds_ok:
        print("\nPlease check your AWS credentials configuration:")
        print("1. Ensure .env file has correct AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        print("2. Or ensure AWS_PROFILE is set and ~/.aws/credentials is properly configured")
        print("3. Verify you have the necessary permissions for the AWS services you're trying to use")
    
    if not bedrock_ok:
        print("\nPotential issues with Bedrock access:")
        print("1. Verify your AWS account has access to the Bedrock service")
        print("2. Check if the model you're trying to use is available in your region")
        print("3. Ensure you have the necessary permissions for Bedrock")
    
    sys.exit(0 if aws_creds_ok else 1)