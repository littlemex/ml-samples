import logging
from typing import Dict, Any, List, Optional, Callable, Awaitable
import asyncio
from response_parser import ResponseParser
from logging_config import get_logger
from config import config

class ContentProcessor:
    """Handles processing of LLM responses and tool executions"""
    
    def __init__(self, session):
        self.session = session
        self.logger = get_logger('ContentProcessor')
        
    async def _execute_tool_with_timeout(self, tool_name: str, tool_args: dict) -> dict:
        """Execute tool with timeout"""
        try:
            return await asyncio.wait_for(
                self.session.call_tool(tool_name, tool_args),
                timeout=config.tool_timeout
            )
        except asyncio.TimeoutError:
            error_msg = f"Tool execution timed out after {config.tool_timeout} seconds"
            self.logger.error(error_msg)
            raise TimeoutError(error_msg)
            
    async def process_response(self, response_body: Dict[str, Any]) -> str:
        """
        Process LLM response and execute any tool calls
        
        Args:
            response_body: The response body from LLM
            
        Returns:
            Processed response text
        """
        self.logger.debug(f'Processing response body: {response_body}')
        
        async def handle_tool_call(content: dict) -> Optional[str]:
            tool_call = content.get('tool_call', {})
            parsed_tool = ResponseParser.parse_tool_call(tool_call)
            if not parsed_tool:
                return None
                
            tool_name, tool_args = parsed_tool
            self.logger.info(f'Executing tool call: {tool_name} with args: {tool_args}')
            try:
                result = await self._execute_tool_with_timeout(tool_name, tool_args)
                return f"[Calling tool {tool_name} with args {tool_args}]"
            except Exception as e:
                self.logger.error(f'Error executing tool {tool_name}: {str(e)}')
                return f"[Error executing tool {tool_name}: {str(e)}]"

        content_handlers = {
            'text': lambda content: ResponseParser.extract_text_content(content),
            'tool_call': handle_tool_call
        }

        final_text = []
        for content in response_body.get("content", []):
            content_type = content.get('type')
            handler = content_handlers.get(content_type)
            if handler:
                if content_type == 'tool_call':
                    result = await handler(content)
                else:
                    result = handler(content)
                if result:
                    final_text.append(result)

        return "\n".join(final_text)