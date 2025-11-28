#!/usr/bin/env python3
"""
Configuration management for Confluence exporter.

Handles loading credentials from .env files and environment variables,
with proper validation and security.
"""

import os
import sys
import re
from typing import Optional, Dict


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class ConfluenceConfig:
    """
    Manages Confluence API configuration and credentials.
    
    Loads credentials from (in order of precedence):
    1. .env file in current directory
    2. Environment variables
    
    All credentials are validated before use.
    """
    
    def __init__(self, env_file: str = ".env"):
        """
        Initialize configuration by loading from .env file and environment.
        
        Args:
            env_file: Path to .env file (default: ".env")
        """
        self.base_url: Optional[str] = None
        self.username: Optional[str] = None
        self.api_token: Optional[str] = None
        
        # Load from .env file first (if it exists)
        env_vars = self._load_env_file(env_file)
        
        # Load configuration (env file takes precedence, then OS environment)
        self.base_url = env_vars.get('CONFLUENCE_BASE_URL') or os.getenv('CONFLUENCE_BASE_URL')
        self.username = env_vars.get('CONFLUENCE_USERNAME') or os.getenv('CONFLUENCE_USERNAME')
        self.api_token = env_vars.get('CONFLUENCE_API_TOKEN') or os.getenv('CONFLUENCE_API_TOKEN')
        
        # Validate configuration
        self._validate()
    
    def _load_env_file(self, env_file: str) -> Dict[str, str]:
        """
        Load environment variables from a .env file.
        
        Supports basic key=value format with comments and empty lines.
        Uses only Python stdlib for parsing.
        
        Args:
            env_file: Path to .env file
            
        Returns:
            Dictionary of environment variables
        """
        env_vars = {}
        
        if not os.path.exists(env_file):
            return env_vars
        
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    # Strip whitespace
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value
                    match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$', line)
                    if not match:
                        print(f"Warning: Skipping invalid line {line_num} in {env_file}: {line}", 
                              file=sys.stderr)
                        continue
                    
                    key, value = match.groups()
                    
                    # Remove quotes if present
                    value = value.strip()
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    env_vars[key] = value
        
        except IOError as e:
            print(f"Warning: Could not read {env_file}: {e}", file=sys.stderr)
        
        return env_vars
    
    def _validate(self):
        """
        Validate that all required configuration is present and valid.
        
        Raises:
            ConfigurationError: If configuration is missing or invalid
        """
        errors = []
        
        # Check required fields
        if not self.username:
            errors.append(
                "Username is required. Set CONFLUENCE_USERNAME in .env file or environment variable."
            )
        
        if not self.api_token:
            errors.append(
                "API token is required. Set CONFLUENCE_API_TOKEN in .env file or environment variable."
            )
        
        if not self.base_url:
            errors.append(
                "Base URL is required. Set CONFLUENCE_BASE_URL in .env file or environment variable."
            )
        
        # Validate base URL format if present
        if self.base_url:
            # Remove trailing slashes
            self.base_url = self.base_url.rstrip('/')
            
            # Check if it looks like a valid URL
            if not re.match(r'^https?://', self.base_url):
                errors.append(
                    f"Base URL must start with http:// or https://. Got: {self.base_url}"
                )
        
        # Validate email format for username if present
        if self.username and '@' not in self.username:
            print(
                f"Warning: Username '{self.username}' doesn't look like an email address. "
                "Confluence typically requires email addresses for authentication.",
                file=sys.stderr
            )
        
        if errors:
            error_msg = "Configuration errors:\n  - " + "\n  - ".join(errors)
            raise ConfigurationError(error_msg)
    
    def __repr__(self) -> str:
        """Return a safe string representation (without exposing credentials)."""
        return (
            f"ConfluenceConfig(base_url='{self.base_url}', "
            f"username='{self.username}', "
            f"api_token='***')"
        )

