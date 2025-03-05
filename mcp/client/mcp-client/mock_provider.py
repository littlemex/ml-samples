"""
Mock LLM provider for testing without real API calls
"""

import logging
import json
from typing import Dict, Any, List
from llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class MockProvider(LLMProvider):
    """Mock implementation of LLMProvider for testing"""
    
    def __init__(self):
        logger.info("Initializing MockProvider")
    
    async def invoke(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Mock implementation that returns predefined responses based on the query
        
        Args:
            messages: List of message dictionaries
            tools: List of available tools
            
        Returns:
            Mock response
        """
        logger.info("MockProvider.invoke called")
        
        # Get the user's query from the last user message
        query = ""
        for message in reversed(messages):
            if message.get("role") == "user":
                if isinstance(message.get("content"), str):
                    query = message.get("content", "").lower()
                elif isinstance(message.get("content"), list):
                    for content_item in message.get("content", []):
                        if content_item.get("type") == "text":
                            query = content_item.get("text", "").lower()
                            break
                break
        
        logger.info(f"Processing query: {query}")
        
        # Check if we should use a tool
        if "weather" in query or "alerts" in query:
            # Find the weather tool
            weather_tool = None
            for tool in tools:
                if tool.get("name") == "get_alerts" and "alerts" in query:
                    weather_tool = tool
                    break
                elif tool.get("name") == "get_forecast":
                    weather_tool = tool
                    break
            
            if weather_tool:
                tool_name = weather_tool.get("name")
                logger.info(f"Using tool: {tool_name}")
                
                # Create a tool call response
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"I'll check the {tool_name.replace('get_', '')} for you."
                        },
                        {
                            "type": "tool_call",
                            "id": "call_123456",
                            "tool_call": {
                                "function": {
                                    "name": tool_name,
                                    "arguments": json.dumps({
                                        "state": "CA" if "alerts" in query else None,
                                        "latitude": 37.7749 if "forecast" in query else None,
                                        "longitude": -122.4194 if "forecast" in query else None
                                    })
                                }
                            }
                        }
                    ]
                }
        
        # Default response if no specific pattern matched
        return {
            "content": [
                {
                    "type": "text",
                    "text": "This is a mock response. I'm not actually connecting to any LLM API. "
                            "I can simulate basic tool usage for testing purposes. "
                            "Try asking about weather alerts or forecasts."
                }
            ]
        }