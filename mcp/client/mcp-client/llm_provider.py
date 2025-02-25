from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
import os
import logging
from typing import Optional
import importlib.util

logger = logging.getLogger(__name__)

# Conditionally import litellm to handle the case where it's not installed
try:
    from litellm import completion
    LITELLM_AVAILABLE = True
except ImportError:
    logger.warning("litellm package not available. Will use mock provider.")
    LITELLM_AVAILABLE = False

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def invoke(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Invoke the LLM with messages and tools
        
        Args:
            messages: List of message dictionaries
            tools: List of available tools
            
        Returns:
            Response from the LLM
        """
        pass

class BedrockProvider(LLMProvider):
    """Amazon Bedrock implementation of LLMProvider using litellm"""
    
    def __init__(self):
        # Check if we should use mock responses
        self.use_mock = os.getenv('USE_MOCK_RESPONSE', 'false').lower() == 'true'
        
        if self.use_mock or not LITELLM_AVAILABLE:
            logger.info("Using mock provider instead of real Bedrock API")
            # Import the mock provider dynamically to avoid circular imports
            try:
                from mock_provider import MockProvider
                self.mock_provider = MockProvider()
            except ImportError:
                logger.warning("mock_provider.py not found, using internal mock implementation")
                self.mock_provider = None
            return
            
        # Bedrock configuration
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        self.max_tokens = int(os.getenv('BEDROCK_MAX_TOKENS', '1000'))
        self.anthropic_version = os.getenv('ANTHROPIC_VERSION', 'bedrock-2023-05-31')
        
        # Configure litellm with AWS credentials
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        os.environ["AWS_REGION"] = aws_region
        
        # Log configuration for debugging
        logger.info(f"Initialized BedrockProvider with model: {self.model_id}")
        logger.info(f"Using AWS region: {aws_region}")
        
        # Check if AWS credentials are available
        self._check_aws_credentials()
        
    def _check_aws_credentials(self):
        """Check if AWS credentials are properly configured"""
        access_key = os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        profile = os.getenv('AWS_PROFILE')
        aws_profile_name = os.getenv('AWS_PROFILE_NAME')
        
        if not (access_key and secret_key) and not profile and not aws_profile_name:
            logger.warning("AWS credentials not found in environment variables.")
            logger.warning("Make sure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set,")
            logger.warning("or AWS_PROFILE/AWS_PROFILE_NAME is set and ~/.aws/credentials is properly configured.")
        
        if aws_profile_name:
            logger.info(f"Using AWS profile name: {aws_profile_name}")
        
    async def invoke(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Invoke Bedrock model using litellm"""
        # Use mock provider if configured or if litellm is not available
        if self.use_mock or not LITELLM_AVAILABLE:
            if self.mock_provider:
                logger.info("Using external mock provider")
                return await self.mock_provider.invoke(messages, tools)
            else:
                logger.info("Using internal mock response")
                return self._get_mock_response(messages, tools)
        
        try:
            logger.debug(f"Invoking Bedrock model: {self.model_id}")
            
            # Get AWS profile name from environment variable
            aws_profile_name = os.getenv('AWS_PROFILE_NAME')
            
            # Prepare completion parameters
            completion_params = {
                "model": self.model_id,
                "messages": messages,
                "tools": tools,
                "max_tokens": self.max_tokens,
                "api_base": "bedrock",
                "custom_llm_provider": "bedrock",
                "anthropic_version": self.anthropic_version
            }
            
            # Add AWS profile name if specified
            if aws_profile_name:
                completion_params["aws_profile_name"] = aws_profile_name
                logger.debug(f"Using AWS profile name: {aws_profile_name}")
            
            response = completion(**completion_params)
            
            # Extract and return the response content
            logger.debug("Successfully received response from Bedrock")
            return response.choices[0].message
            
        except Exception as e:
            logger.error(f"Error invoking Bedrock: {str(e)}", exc_info=True)
            
            # Provide more helpful error message
            if "NoneType" in str(e) and "split" in str(e):
                logger.error("This error is likely due to missing or invalid AWS credentials.")
                logger.error("Please check your .env file and AWS configuration.")
                
                # Fall back to mock provider
                logger.info("Falling back to mock provider due to error")
                if self.mock_provider:
                    return await self.mock_provider.invoke(messages, tools)
                else:
                    return self._get_mock_response(messages, tools)
            
            # Re-raise the exception with more context
            raise Exception(f"Error invoking Bedrock via litellm: {str(e)}")
    
    def _get_mock_response(self, messages: List[Dict[str, Any]] = None, tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Return a mock response for testing purposes"""
        # Simple mock implementation if mock_provider.py is not available
        query = ""
        if messages:
            for message in reversed(messages):
                if message.get("role") == "user":
                    if isinstance(message.get("content"), str):
                        query = message.get("content", "").lower()
                        break
                    elif isinstance(message.get("content"), list):
                        for content_item in message.get("content", []):
                            if content_item.get("type") == "text":
                                query = content_item.get("text", "").lower()
                                break
        
        # Check if we should use a weather tool
        if tools and ("weather" in query or "alerts" in query or "forecast" in query):
            for tool in tools:
                if tool.get("name") in ["get_alerts", "get_forecast"]:
                    tool_name = tool.get("name")
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"I'll check the {tool_name.replace('get_', '')} for you."
                            },
                            {
                                "type": "tool_call",
                                "id": "mock_call_123",
                                "tool_call": {
                                    "name": tool_name,
                                    "arguments": json.dumps({
                                        "state": "CA" if "alerts" in query else None,
                                        "latitude": 37.7749 if "forecast" in query else None,
                                        "longitude": -122.4194 if "forecast" in query else None
                                    })
                                }
                            }
                        ]
                    }
        
        # Default response
        return {
            "content": [
                {
                    "type": "text",
                    "text": "This is a mock response for testing. The actual Bedrock API was not called. "
                            "Try asking about weather alerts or forecasts."
                }
            ]
        }