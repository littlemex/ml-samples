import asyncio
import sys
from typing import Optional
from llm_provider import LLMProvider, BedrockProvider
from server_connection import ServerConnection
from content_processor import ContentProcessor
from logging_config import setup_logging, get_logger
from config import config


class MCPClient:
    """Main MCP client that coordinates server connection, LLM, and content processing"""
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        # Initialize logging
        setup_logging()
        self.logger = get_logger('MCPClient')
        
        # Initialize components
        self.server = ServerConnection()
        self.llm_provider = llm_provider or BedrockProvider()
        self.content_processor = None  # Initialized after server connection
        
        self.logger.info('MCPClient initialized')
        
    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server"""
        tool_names = await self.server.connect(server_script_path)
        self.content_processor = ContentProcessor(self.server.session)
        print("\nConnected to server with tools:", tool_names)
        
    async def process_query(self, query: str) -> str:
        """Process a query using the LLM provider and available tools"""
        if len(query) > config.max_query_length:
            raise ValueError(f"Query exceeds maximum length of {config.max_query_length} characters")
            
        self.logger.info(f'Processing query: {query}')
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    }
                ]
            }
        ]

        # Get available tools for LLM
        response = await self.server.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        self.logger.debug('Sending request to LLM provider')
        try:
            response_body = await self.llm_provider.invoke(messages, available_tools)
            return await self.content_processor.process_response(response_body)
        except Exception as e:
            self.logger.error(f'Error processing query: {str(e)}')
            raise

    async def chat_loop(self):
        """Run an interactive chat loop"""
        self.logger.info('Starting chat loop')
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    self.logger.info('Received quit command, exiting chat loop')
                    break

                if not query:
                    print("Query cannot be empty")
                    continue

                response = await self.process_query(query)
                print("\n" + response)

            except ValueError as e:
                error_msg = f"Invalid input: {str(e)}"
                self.logger.warning(error_msg)
                print(f"\n{error_msg}")
            except Exception as e:
                error_msg = f"Error during chat loop: {str(e)}"
                self.logger.error(error_msg)
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        self.logger.info('Cleaning up resources')
        await self.server.cleanup()

async def main():
    logger = get_logger('main')
    if len(sys.argv) < 2:
        logger.error('No server script path provided')
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    except Exception as e:
        logger.error(f'Fatal error in main: {str(e)}')
        raise
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())