#!/usr/bin/env python3
"""
Authentication handling for Confluence API.

Provides secure authentication header creation without exposing credentials.
"""

import base64
import urllib.request
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config import ConfluenceConfig


class ConfluenceAuth:
    """
    Handles authentication for Confluence API requests.
    
    Uses HTTP Basic Authentication with username and API token.
    """
    
    def __init__(self, config: 'ConfluenceConfig'):
        """
        Initialize authentication with configuration.
        
        Args:
            config: ConfluenceConfig instance with credentials
        """
        self.config = config
        self._auth_header = self._create_auth_header()
    
    def _create_auth_header(self) -> str:
        """
        Create the Basic Authentication header value.
        
        Returns:
            Base64-encoded authentication string
        """
        credentials = f"{self.config.username}:{self.config.api_token}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return f"Basic {encoded_credentials}"
    
    def add_auth_headers(self, request: urllib.request.Request) -> urllib.request.Request:
        """
        Add authentication headers to a urllib Request object.
        
        Args:
            request: urllib.request.Request object
            
        Returns:
            The same request object with auth headers added
        """
        request.add_header('Authorization', self._auth_header)
        request.add_header('Content-Type', 'application/json')
        return request
    
    def create_authenticated_request(self, url: str) -> urllib.request.Request:
        """
        Create a new authenticated request for the given URL.
        
        Args:
            url: URL to create request for
            
        Returns:
            urllib.request.Request with authentication headers
        """
        request = urllib.request.Request(url)
        return self.add_auth_headers(request)

