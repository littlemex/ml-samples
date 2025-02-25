import argparse
import asyncio
import importlib.util
import logging
import os
import sys
from pathlib import Path
from contextlib import AsyncExitStack
from typing import List, Dict, Any, Optional

from logging_config import setup_logging
from server_connection import ServerConnection
from content_processor import ContentProcessor
from llm_provider import BedrockProvider
from response_parser import ResponseParser
from config import Config

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

class MCPClient:
    """MCP Client for interacting with MCP servers and LLMs"""
    
    def __init__(self):
        """Initialize the MCP client"""
        self.exit_stack = AsyncExitStack()
        self.server_connection = None
        
        # Check if we should use mock responses instead of real API calls
        use_mock = os.getenv('USE_MOCK_RESPONSE', 'false').lower() == 'true'
        if use_mock:
            logger.info("Using mock responses instead of real API calls")
            
        # Initialize the LLM provider
        try:
            self.llm_provider = BedrockProvider()
        except Exception as e:
            logger.error(f"Error initializing BedrockProvider: {e}")
            logger.warning("Setting USE_MOCK_RESPONSE=true to use mock responses")
            os.environ['USE_MOCK_RESPONSE'] = 'true'
            self.llm_provider = BedrockProvider()
            
        self.content_processor = ContentProcessor()
        self.response_parser = ResponseParser()
        self.session = None
        
    async def connect_to_server(self, server_path: str) -> List[str]:
        """Connect to an MCP server"""
        try:
            self.server_connection = ServerConnection(server_path)
            tool_names = await self.server_connection.connect()
            self.session = self.server_connection.session
            self.content_processor.session = self.session
            return tool_names
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            raise
    
    async def process_query(self, query: str) -> str:
        """Process a query using LLM and available tools"""
        if not self.session:
            raise ValueError("Not connected to any MCP server")
            
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        # Get available tools
        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # Initial LLM API call
        llm_response = await self.llm_provider.invoke(messages, available_tools)

        # Process response and handle tool calls
        tool_results = []
        final_text = []
        # FIXME:  この処理は response_parser で処理すべき部分があれば response_parser  にメソッドを作りましょう
        assistant_message_content = []
        for content in llm_response.get("content", []):
            if content.get("type") == "text":
                final_text.append(content.get("text", ""))
                assistant_message_content.append(content)
            elif content.get("type") == "tool_call":
                tool_name, tool_args = self.response_parser.parse_tool_call(content.get("tool_call", {}))
                if tool_name and tool_args:
                    # Execute tool call
                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                    result = await self.session.call_tool(tool_name, tool_args)
                    tool_results.append({"call": tool_name, "result": result})
                    final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                    assistant_message_content.append(content)
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message_content
                    })
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content.get("id", ""),
                                "content": result.content
                            }
                        ]
                    })

                    # Get next response from LLM
                    llm_response = await self.llm_provider.invoke(messages, available_tools)
                    if llm_response.get("content"):
                        for next_content in llm_response.get("content", []):
                            if next_content.get("type") == "text":
                                final_text.append(next_content.get("text", ""))

        return "\n".join(final_text)
        
    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                logger.error(f"Error processing query: {e}", exc_info=True)
                print(f"\nError: {str(e)}")
                
    async def cleanup(self):
        """Clean up resources"""
        if self.server_connection:
            await self.server_connection.cleanup()
        await self.exit_stack.aclose()

async def main():
    """Main function to run the client."""
    parser = argparse.ArgumentParser(description="MCP Client")
    parser.add_argument("server_path", help="Path to the server module")
    args = parser.parse_args()
    
    client = MCPClient()
    try:
        await client.connect_to_server(args.server_path)
        await client.chat_loop()
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())