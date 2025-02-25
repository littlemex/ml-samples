import logging
import asyncio
from typing import Optional, Tuple, List
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from config import config
from logging_config import get_logger

class ServerConnection:
    """Handles MCP server connection and communication"""
    
    def __init__(self, server_module: str):
        self.server_module = server_module
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.logger = get_logger('ServerConnection')
        self.stdio = None
        self.write = None
        self._connected = False
        
    async def connect(self) -> List[str]:
        """
        Connect to an MCP server
        
        Args:
            server_script_path: Path to the server script (.py or .js)
            
        Returns:
            List of available tool names
        """
        self.logger.info(f'Attempting to connect to server: {self.server_module}')
        
        # Validate script type
        self.logger.debug(f'Validating script type for path: {self.server_module}')
        is_python = self.server_module.endswith('.py')
        is_js = self.server_module.endswith('.js')
        if not (is_python or is_js):
            self.logger.error(f'Invalid server script type: {self.server_module}')
            raise ValueError("Server script must be a .py or .js file")

        self.logger.debug(f'Script type validation passed: {"Python" if is_python else "JavaScript"}')
        # Use Python interpreter from virtual environment
        import sys
        command = sys.executable if is_python else "node"
        
        self.logger.debug(f'Preparing server parameters with command: {command}')
        self.logger.debug(f'Environment variables: {config.server_environment}')
        # Configure communication between server and client via standard I/O
        server_params = StdioServerParameters(
            command=command,
            args=[self.server_module],
            env=config.server_environment
        )

        try:
            # Make sure we're in the same task for all async context operations
            self.logger.debug(f'Creating stdio transport with params: {server_params}')
            # Use a new task for the stdio client to avoid task cancellation issues
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.logger.debug('stdio transport created successfully')
            
            self.stdio, self.write = stdio_transport
            self.logger.debug('stdio and write handlers extracted from transport')
            
            self.logger.debug('Creating ClientSession...')
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
            self.logger.debug('ClientSession created successfully')

            self.logger.debug('Initializing session...')
            await self.session.initialize()
            self.logger.debug('Session initialized successfully')
            self._connected = True
        except Exception as e:
            self.logger.error(f'Error during server connection setup: {str(e)}', exc_info=True)
            await self.cleanup()  # Clean up resources on error
            raise

        # List available tools
        response = await self.session.list_tools()
        tool_names = [tool.name for tool in response.tools]
        self.logger.info(f'Successfully connected to server. Available tools: {tool_names}')
        
        return tool_names
        
    async def cleanup(self):
        """Clean up server connection resources"""
        self.logger.info('Cleaning up server connection resources')
        try:
            # Make sure we're cleaning up in the same task context
            await self.exit_stack.aclose()
            self._connected = False
            self.session = None
            self.stdio = None
            self.write = None
        except Exception as e:
            self.logger.error(f'Error during cleanup: {str(e)}', exc_info=True)
        
    def is_connected(self) -> bool:
        """Check if connected to server"""
        return self._connected and self.session is not None