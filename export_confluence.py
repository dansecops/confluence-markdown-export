#!/usr/bin/env python3
"""
Confluence Page Exporter - Export Confluence pages to Markdown format

Copyright (c) 2025 dansecops
Licensed under the MIT License - see LICENSE file for details

This script exports Confluence pages to Markdown format, with support for
recursive export of page hierarchies. It uses only Python standard library
and requires Confluence API credentials.
"""

import urllib.request
import urllib.error
import json
import sys
import re
import base64
import os
import argparse

# Global variables for configuration (set via arguments or env vars)
CONFLUENCE_BASE_URL = None
USERNAME = None
API_TOKEN = None

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

def get_page(page_id):
    """Get a Confluence page by ID"""
    url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}?expand=body.view,space"
    
    # Create auth header
    credentials = f"{USERNAME}:{API_TOKEN}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Basic {encoded_credentials}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"Error: {e.code}", file=sys.stderr)
        print(e.read().decode('utf-8'), file=sys.stderr)
        sys.exit(1)

def get_child_pages(page_id):
    """Get all child pages of a given page"""
    url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}/child/page"
    
    # Create auth header
    credentials = f"{USERNAME}:{API_TOKEN}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Basic {encoded_credentials}')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('results', [])
    except urllib.error.HTTPError as e:
        print(f"Error getting children: {e.code}", file=sys.stderr)
        return []

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

def export_page_to_markdown(page_id, output_file=None):
    """Export a Confluence page to Markdown"""
    page_data = get_page(page_id)
    
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

def export_page_with_children(page_id, output_dir, depth=0, max_depth=10):
    """Recursively export a page and all its children"""
    import os
    
    if depth > max_depth:
        print(f"⚠️  Max depth reached, skipping further children", file=sys.stderr)
        return
    
    # Get page data
    page_data = get_page(page_id)
    title = page_data['title']
    
    # Create output filename
    safe_title = sanitize_filename(title)
    output_file = os.path.join(output_dir, f"{safe_title}.md")
    
    # Export the page
    indent = "  " * depth
    print(f"{indent}📄 Exporting: {title}")
    export_page_to_markdown(page_id, output_file)
    
    # Get and export children
    children = get_child_pages(page_id)
    if children:
        print(f"{indent}   └─ Found {len(children)} child page(s)")
        
        # Create subdirectory for children
        child_dir = os.path.join(output_dir, safe_title)
        os.makedirs(child_dir, exist_ok=True)
        
        for child in children:
            child_id = child['id']
            export_page_with_children(child_id, child_dir, depth + 1, max_depth)

if __name__ == "__main__":
    import os
    
    parser = argparse.ArgumentParser(
        description='Export Confluence pages to Markdown format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export a single page
  python3 export_confluence.py 123456 -u user@example.com -t TOKEN -b https://company.atlassian.net/wiki
  
  # Export a page with all children
  python3 export_confluence.py 123456 --with-children -u user@example.com -t TOKEN -b https://company.atlassian.net/wiki
  
  # Use environment variables
  export CONFLUENCE_USERNAME="user@example.com"
  export CONFLUENCE_API_TOKEN="your-token"
  export CONFLUENCE_BASE_URL="https://company.atlassian.net/wiki"
  python3 export_confluence.py 123456 --with-children
        """
    )
    
    parser.add_argument('page_id', help='Confluence page ID to export')
    parser.add_argument('output', nargs='?', default=None,
                       help='Output file (single page) or directory (with children)')
    
    parser.add_argument('-u', '--username', 
                       help='Confluence username (email). Can also use CONFLUENCE_USERNAME env var')
    parser.add_argument('-t', '--token', '--api-token',
                       help='Confluence API token. Can also use CONFLUENCE_API_TOKEN env var')
    parser.add_argument('-b', '--base-url', '--url',
                       help='Confluence base URL (e.g., https://company.atlassian.net/wiki). Can also use CONFLUENCE_BASE_URL env var')
    
    parser.add_argument('--with-children', action='store_true',
                       help='Export the page and all its descendant pages recursively')
    parser.add_argument('--max-depth', type=int, default=10,
                       help='Maximum depth for recursive export (default: 10)')
    
    args = parser.parse_args()
    
    # Set configuration from arguments or environment variables
    CONFLUENCE_BASE_URL = args.base_url or os.getenv('CONFLUENCE_BASE_URL')
    USERNAME = args.username or os.getenv('CONFLUENCE_USERNAME')
    API_TOKEN = args.token or os.getenv('CONFLUENCE_API_TOKEN')
    
    # Validate required parameters
    if not USERNAME:
        print("❌ Error: Username is required. Use -u/--username or set CONFLUENCE_USERNAME environment variable", file=sys.stderr)
        sys.exit(1)
    if not API_TOKEN:
        print("❌ Error: API token is required. Use -t/--token or set CONFLUENCE_API_TOKEN environment variable", file=sys.stderr)
        sys.exit(1)
    if not CONFLUENCE_BASE_URL:
        print("❌ Error: Confluence base URL is required. Use -b/--base-url or set CONFLUENCE_BASE_URL environment variable", file=sys.stderr)
        sys.exit(1)
    
    # Remove trailing slashes from base URL
    CONFLUENCE_BASE_URL = CONFLUENCE_BASE_URL.rstrip('/')
    
    page_id = args.page_id
    
    if args.with_children:
        # Export with children
        output_dir = args.output if args.output else 'confluence-export'
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"🚀 Starting export of page {page_id} and all children...")
        print(f"📁 Output directory: {output_dir}")
        print(f"🔐 Connecting to: {CONFLUENCE_BASE_URL}")
        print(f"👤 Username: {USERNAME}")
        print("")
        
        export_page_with_children(page_id, output_dir, max_depth=args.max_depth)
        
        print("")
        print(f"✨ Export complete! Check {output_dir}/")
    else:
        # Single page export
        output_file = args.output
        export_page_to_markdown(page_id, output_file)
