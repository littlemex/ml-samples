from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
import os
from typing import Optional
from litellm import completion

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
        # Bedrock configuration
        self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        self.max_tokens = int(os.getenv('BEDROCK_MAX_TOKENS', '1000'))
        self.anthropic_version = os.getenv('ANTHROPIC_VERSION', 'bedrock-2023-05-31')
        
        # Configure litellm with AWS credentials
        os.environ["AWS_REGION"] = os.getenv('AWS_REGION', 'us-east-1')
        
    async def invoke(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Invoke Bedrock model using litellm"""
        try:
            response = completion(
                model=self.model_id,
                messages=messages,
                tools=tools,
                max_tokens=self.max_tokens,
                api_base="bedrock",
                custom_llm_provider="bedrock",
                anthropic_version=self.anthropic_version
            )
            
            # Extract and return the response content
            return response.choices[0].message
            
        except Exception as e:
            # Re-raise the exception after logging if needed
            raise Exception(f"Error invoking Bedrock via litellm: {str(e)}")