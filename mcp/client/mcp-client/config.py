import os
from typing import Dict, Any
from dotenv import load_dotenv

class Config:
    """Centralized configuration management"""
    
    def __init__(self):
        load_dotenv()
        
        # Logging configuration
        self.log_level = os.getenv('MCP_LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('MCP_LOG_FILE', 'mcp_client.log')
        self.log_max_bytes = int(os.getenv('MCP_LOG_MAX_BYTES', 10 * 1024 * 1024))
        self.log_backup_count = int(os.getenv('MCP_LOG_BACKUP_COUNT', 5))
        
        # Tool execution configuration
        self.tool_timeout = int(os.getenv('TOOL_TIMEOUT_SECONDS', '30'))
        self.max_query_length = int(os.getenv('MAX_QUERY_LENGTH', '4096'))
        
        # Server configuration
        self.server_env = {k: v for k, v in os.environ.items() if k.startswith('MCP_SERVER_')}
        
    @property
    def logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return {
            'level': self.log_level,
            'file': self.log_file,
            'max_bytes': self.log_max_bytes,
            'backup_count': self.log_backup_count
        }
        
    @property
    def server_environment(self) -> Dict[str, str]:
        """Get server environment variables"""
        return self.server_env.copy()

# Global configuration instance
config = Config()