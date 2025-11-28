#!/usr/bin/env python3
"""
Confluence Page Exporter - Export Confluence pages to Markdown format

Copyright (c) 2025 dansecops
Licensed under the MIT License - see LICENSE file for details

This script exports Confluence pages to Markdown format, with support for
recursive export of page hierarchies. It uses only Python standard library
and requires Confluence API credentials.
"""

import sys
import re
import os
import argparse

# Import our new modules
from config import ConfluenceConfig, ConfigurationError
from auth import ConfluenceAuth
from api_client import ConfluenceClient, ConfluenceAPIError

def html_to_markdown(html):
    """Convert HTML to Markdown (basic conversion)"""
    text = html
    
    # Headers
    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n', text)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n', text)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n', text)
    text = re.sub(r'<h4[^>]*>(.*?)</h4>', r'#### \1\n', text)
    
    # Paragraphs
    text = re.sub(r'<p>(.*?)</p>', r'\1\n\n', text)
    text = re.sub(r'<p\s+[^>]*>(.*?)</p>', r'\1\n\n', text)
    
    # Emphasis
    text = re.sub(r'<em>(.*?)</em>', r'*\1*', text)
    text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', text)
    
    # Line breaks
    text = re.sub(r'<br\s*/?>', '\n', text)
    
    # Non-breaking space and special chars
    text = text.replace('&nbsp;', ' ')
    text = text.replace('\xa0', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('…', '...')
    
    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up multiple newlines
    text = re.sub(r'\n\n\n+', '\n\n', text)
    
    return text.strip()


def sanitize_filename(filename):
    """Sanitize filename for safe file creation"""
    # Replace invalid characters with underscore
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename

def export_page_to_markdown(client, page_id, output_file=None):
    """
    Export a Confluence page to Markdown.
    
    Args:
        client: ConfluenceClient instance
        page_id: Confluence page ID
        output_file: Optional output file path
        
    Returns:
        The markdown content as a string
    """
    page_data = client.get_page(page_id)
    
    title = page_data['title']
    html_content = page_data['body']['view']['value']
    
    markdown = html_to_markdown(html_content)
    
    output = f"# {title}\n\n{markdown}\n"
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"✅ Exported '{title}' to {output_file}")
    else:
        print(output)
    
    return output

def export_page_with_children(client, page_id, output_dir, depth=0, max_depth=10):
    """
    Recursively export a page and all its children.
    
    Args:
        client: ConfluenceClient instance
        page_id: Confluence page ID
        output_dir: Output directory for exported files
        depth: Current recursion depth
        max_depth: Maximum recursion depth
    """
    if depth > max_depth:
        print(f"⚠️  Max depth reached, skipping further children", file=sys.stderr)
        return
    
    # Get page data
    page_data = client.get_page(page_id)
    title = page_data['title']
    
    # Create output filename
    safe_title = sanitize_filename(title)
    output_file = os.path.join(output_dir, f"{safe_title}.md")
    
    # Export the page
    indent = "  " * depth
    print(f"{indent}📄 Exporting: {title}")
    export_page_to_markdown(client, page_id, output_file)
    
    # Get and export children
    children = client.get_child_pages(page_id)
    if children:
        print(f"{indent}   └─ Found {len(children)} child page(s)")
        
        # Create subdirectory for children
        child_dir = os.path.join(output_dir, safe_title)
        os.makedirs(child_dir, exist_ok=True)
        
        for child in children:
            child_id = child['id']
            export_page_with_children(client, child_id, child_dir, depth + 1, max_depth)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Export Confluence pages to Markdown format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export a single page (requires .env file or environment variables)
  python3 export_confluence.py 123456 output.md
  
  # Export a page with all children
  python3 export_confluence.py 123456 output_dir --with-children
  
  # Limit recursion depth
  python3 export_confluence.py 123456 output_dir --with-children --max-depth 5

Configuration:
  Credentials are loaded from .env file or environment variables:
    CONFLUENCE_USERNAME - Your Confluence username (email)
    CONFLUENCE_API_TOKEN - Your Confluence API token
    CONFLUENCE_BASE_URL - Your Confluence base URL (e.g., https://company.atlassian.net/wiki)
  
  See README.md for setup instructions.
        """
    )
    
    parser.add_argument('page_id', help='Confluence page ID to export')
    parser.add_argument('output', nargs='?', default=None,
                       help='Output file (single page) or directory (with children)')
    
    parser.add_argument('--with-children', action='store_true',
                       help='Export the page and all its descendant pages recursively')
    parser.add_argument('--max-depth', type=int, default=10,
                       help='Maximum depth for recursive export (default: 10)')
    parser.add_argument('--env-file', default='.env',
                       help='Path to .env file (default: .env)')
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = ConfluenceConfig(env_file=args.env_file)
    except ConfigurationError as e:
        print(f"❌ Configuration Error:\n{e}", file=sys.stderr)
        print("\nPlease create a .env file or set environment variables.", file=sys.stderr)
        print("See README.md for setup instructions.", file=sys.stderr)
        sys.exit(1)
    
    # Initialize authentication and API client
    auth = ConfluenceAuth(config)
    client = ConfluenceClient(config, auth)
    
    page_id = args.page_id
    
    try:
        if args.with_children:
            # Export with children
            output_dir = args.output if args.output else 'confluence-export'
            os.makedirs(output_dir, exist_ok=True)
            
            print(f"🚀 Starting export of page {page_id} and all children...")
            print(f"📁 Output directory: {output_dir}")
            print(f"🔐 Connecting to: {config.base_url}")
            print(f"👤 Username: {config.username}")
            print("")
            
            export_page_with_children(client, page_id, output_dir, max_depth=args.max_depth)
            
            print("")
            print(f"✨ Export complete! Check {output_dir}/")
        else:
            # Single page export
            output_file = args.output
            export_page_to_markdown(client, page_id, output_file)
    except ConfluenceAPIError as e:
        print(f"\n❌ Export failed: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Export interrupted by user", file=sys.stderr)
        sys.exit(130)
