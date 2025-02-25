import json
import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

class ResponseParser:
    """Generic parser for MCP response handling"""
    
    @staticmethod
    def parse_tool_call(tool_call: dict) -> Optional[Tuple[str, dict]]:
        """
        Parse a tool call content and return the tool name and arguments.
        
        Args:
            tool_call: The tool call dictionary containing function details
            
        Returns:
            Tuple of (tool_name, tool_args) if parsing successful, None otherwise
        """
        function = tool_call.get('function', {})
        if not function:
            logger.error(f'Invalid tool call format: missing function data')
            return None
            
        tool_name = function.get('name')
        if not tool_name:
            logger.error(f'Invalid tool call format: missing tool name')
            return None
            
        try:
            tool_args = json.loads(function.get('arguments', '{}'))
            return tool_name, tool_args
        except json.JSONDecodeError as e:
            logger.error(f'Invalid tool arguments JSON: {e}')
            return None

    @staticmethod
    def extract_text_content(content: dict) -> Optional[str]:
        """
        Extract text from a content item.
        
        Args:
            content: The content dictionary containing text data
            
        Returns:
            The text content if present, None otherwise
        """
        if content.get('type') == 'text':
            return content.get('text')
        return None

    @staticmethod
    def process_response_content(
        response_body: dict,
        content_handlers: Dict[str, Any]
    ) -> List[str]:
        """
        Process response content using provided handlers.
        
        Args:
            response_body: The complete response body to process
            content_handlers: Dictionary of content type handlers
                Expected format: {
                    'text': callable that handles text content,
                    'tool_call': callable that handles tool calls
                }
                
        Returns:
            List of processed content strings
        """
        final_text = []
        
        for content in response_body.get("content", []):
            content_type = content.get('type')
            handler = content_handlers.get(content_type)
            
            if handler:
                try:
                    result = handler(content)
                    if result:
                        final_text.append(result)
                except Exception as e:
                    logger.error(f'Error processing {content_type} content: {str(e)}')
                    
        return final_text