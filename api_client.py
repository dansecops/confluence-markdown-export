#!/usr/bin/env python3
"""
Confluence API client.

Provides methods to interact with Confluence REST API.
"""

import urllib.request
import urllib.error
import json
import sys
from typing import Dict, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from config import ConfluenceConfig
    from auth import ConfluenceAuth


class ConfluenceAPIError(Exception):
    """Raised when a Confluence API call fails."""
    pass


class ConfluenceClient:
    """
    Client for interacting with Confluence REST API.
    
    Handles all API requests with proper authentication and error handling.
    """
    
    def __init__(self, config: 'ConfluenceConfig', auth: 'ConfluenceAuth'):
        """
        Initialize the Confluence API client.
        
        Args:
            config: ConfluenceConfig instance
            auth: ConfluenceAuth instance
        """
        self.config = config
        self.auth = auth
        self.base_url = config.base_url
    
    def get_page(self, page_id: str) -> Dict[str, Any]:
        """
        Get a Confluence page by ID.
        
        Args:
            page_id: Confluence page ID
            
        Returns:
            Dictionary containing page data including title, body, and space info
            
        Raises:
            ConfluenceAPIError: If the API request fails
        """
        url = f"{self.base_url}/rest/api/content/{page_id}?expand=body.view,space"
        
        request = self.auth.create_authenticated_request(url)
        
        try:
            with urllib.request.urlopen(request) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            
            # Provide user-friendly error messages
            if e.code == 401:
                error_msg = (
                    "Authentication failed (401 Unauthorized). "
                    "Please check your username and API token."
                )
            elif e.code == 403:
                error_msg = (
                    f"Access forbidden (403). You may not have permission to view page {page_id}."
                )
            elif e.code == 404:
                error_msg = (
                    f"Page not found (404). Page ID {page_id} doesn't exist or you don't have access to it."
                )
            else:
                error_msg = f"API request failed with status {e.code}"
            
            print(f"❌ Error: {error_msg}", file=sys.stderr)
            if error_body:
                print(f"Response: {error_body}", file=sys.stderr)
            
            raise ConfluenceAPIError(error_msg) from e
        except urllib.error.URLError as e:
            error_msg = f"Network error: {e.reason}"
            print(f"❌ Error: {error_msg}", file=sys.stderr)
            raise ConfluenceAPIError(error_msg) from e
    
    def get_child_pages(self, page_id: str) -> List[Dict[str, Any]]:
        """
        Get all child pages of a given page.
        
        Args:
            page_id: Parent page ID
            
        Returns:
            List of child page dictionaries
            
        Raises:
            ConfluenceAPIError: If the API request fails
        """
        url = f"{self.base_url}/rest/api/content/{page_id}/child/page"
        
        request = self.auth.create_authenticated_request(url)
        
        try:
            with urllib.request.urlopen(request) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('results', [])
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"⚠️  Warning: Could not get children for page {page_id}: {e.code}", 
                  file=sys.stderr)
            if error_body:
                print(f"Response: {error_body}", file=sys.stderr)
            return []
        except urllib.error.URLError as e:
            print(f"⚠️  Warning: Network error getting children for page {page_id}: {e.reason}", 
                  file=sys.stderr)
            return []

