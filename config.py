"""Configuration module for the socket-based client-server application.

This module defines all configuration constants and settings used throughout
the application, providing a centralized place for configuration management.
All commented lines are not being used at the moment, but might be implemented in the future.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class NetworkConfig:
    """Network and connection configuration settings."""
    HOST: str = '127.0.0.1'
    PORT: int = 65432
    BUFFER_SIZE: int = 1024
    MAX_CONNECTIONS: int = 5
    CONNECTION_TIMEOUT: int = 30  # seconds


@dataclass(frozen=True)
class DatabaseConfig:
    """Database configuration settings."""
    DB_FILE: str = "db.json"
    MAX_INBOX_SIZE: int = 5


@dataclass(frozen=True)
class MessageConfig:
    """Message handling and validation configuration."""
    MAX_MESSAGE_LENGTH: int = 255
    
    # Valid message headers - using tuple for immutability
    # VALID_HEADERS: Tuple[str, ...] = (
    #     'Command', 'Authentication', 'Message', 'Error', 
    #     'Status', 'Acc_type', 'Authentication_answer', 
    #     'Account_type_update', 'Inbox_message', 'Stop'
    # )
    
    # # Valid commands
    # VALID_COMMANDS: Tuple[str, ...] = (
    #     '!message', '!inbox', '!info', '!uptime', 
    #     '!stop', '!help'
    # )
    
    # Valid account types
    VALID_ACCOUNT_TYPES = ('admin', 'user')


@dataclass(frozen=True)
class SecurityConfig:
    """Security related configuration."""
    PASSWORD_MIN_LENGTH: int = 4
    MAX_USERNAME_LENGTH: int = 15
    MIN_USERNAME_LENGTH: int = 3
    # SESSION_TIMEOUT_MINUTES: int = 30
    # MAX_LOGIN_ATTEMPTS: int = 3


@dataclass(frozen=True)
class UIConfig:
    """User interface configuration."""
    WELCOME_MESSAGE: str = "Welcome on our server. Please sign in or create new account."
    
    HELP_TEXT: str = (
        "Choose what you want to do:\n"
        "Send a message: Type !message\n"
        "Check your inbox: Type !inbox\n"
        "Access server information: Type !info\n"
        "Check uptime: Type !uptime\n"
        "Stop server: Type !stop\n"
        "Need help? Type !help"
    )
    
    # # Error messages
    # INVALID_COMMAND_MSG: str = "Wrong command, try again!"
    # EMPTY_LOGIN_MSG: str = "Empty login, try again."
    # EMPTY_PASSWORD_MSG: str = "Empty password, try again."
    # WRONG_ACCOUNT_TYPE_MSG: str = "Wrong account type. Please enter 'admin' or 'user'."


@dataclass(frozen=True)
class ServerConfig:
    """Server application configuration."""
    SERVER_VERSION: str = '1.2.0'


# Create a main config object that combines all configurations
@dataclass(frozen=True)
class AppConfig:
    """Main application configuration combining all config sections."""
    network: NetworkConfig = NetworkConfig()
    database: DatabaseConfig = DatabaseConfig()
    message: MessageConfig = MessageConfig()
    security: SecurityConfig = SecurityConfig()
    ui: UIConfig = UIConfig()
    server: ServerConfig = ServerConfig()
    
    def validate(self) -> None:
        """Validate configuration values for consistency and correctness."""
        # Network validation
        if not (1024 <= self.network.PORT <= 65535):
            raise ValueError(f"Invalid port number: {self.network.PORT}. Must be between 1024-65535")
        
        if self.network.BUFFER_SIZE <= 0:
            raise ValueError(f"Buffer size must be positive: {self.network.BUFFER_SIZE}")
        
        # Message validation
        if self.message.MAX_MESSAGE_LENGTH <= 0:
            raise ValueError("Max message length must be positive")
        
        if self.security.MIN_USERNAME_LENGTH >= self.security.MAX_USERNAME_LENGTH:
            raise ValueError("Min username length must be less than max username length")
        
        # Security validation
        if self.security.PASSWORD_MIN_LENGTH < 4:
            raise ValueError("Password minimum length too short (minimum 4 characters)")
        
        print("✅ Configuration validation passed")


# Global configuration instance
# This is the single source of truth for all configuration in your app
config = AppConfig()

# Validate configuration on import
config.validate()
