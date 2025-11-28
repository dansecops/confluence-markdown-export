# Confluence Page Exporter

A Python script to export Confluence pages to Markdown format.

## Features

- ✅ Export single pages to Markdown
- ✅ Recursively export pages with all children
- ✅ Simple HTML to Markdown conversion
- ✅ Secure credential management via environment variables or command-line args
- ✅ No external dependencies (uses only Python stdlib)

## Setup

### Step 1: Get Your API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "Confluence Exporter")
4. Copy the token immediately (you won't see it again)

### Step 2: Configure Credentials

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   ```bash
   CONFLUENCE_USERNAME=your-email@company.com
   CONFLUENCE_API_TOKEN=your-api-token-here
   CONFLUENCE_BASE_URL=https://your-company.atlassian.net/wiki
   ```

3. That's it! The script will automatically load credentials from the `.env` file.

**Alternative:** You can also set environment variables directly:
```bash
export CONFLUENCE_USERNAME="your-email@company.com"
export CONFLUENCE_API_TOKEN="your-api-token-here"
export CONFLUENCE_BASE_URL="https://your-company.atlassian.net/wiki"
```

## Usage

Make sure you've completed the setup steps above before running the script.

### Export a Single Page

```bash
# Export to a file
python3 export_confluence.py 4818731035 output.md

# Print to stdout
python3 export_confluence.py 4818731035
```

### Export a Page with All Children

```bash
# Export page and all children to a directory
python3 export_confluence.py 4818731035 output_dir --with-children

# Export to default directory (confluence-export/)
python3 export_confluence.py 4818731035 --with-children
```

### Advanced Options

```bash
# Limit recursion depth
python3 export_confluence.py 4818731035 output_dir --with-children --max-depth 5

# Use a different .env file
python3 export_confluence.py 4818731035 output.md --env-file /path/to/.env

# Get help
python3 export_confluence.py --help
```

## Finding Page IDs

The page ID is in the URL when viewing a Confluence page:

```
https://company.atlassian.net/wiki/spaces/SPACE/pages/4818731035/Page+Title
                                                          ^^^^^^^^^^
                                                          This is the page ID
```

## Security Best Practices

⚠️ **Important:**
- **Never commit `.env` to git** - it contains your credentials (already in `.gitignore`)
- **API tokens grant full access** to your Confluence account - treat them like passwords
- **Don't share your `.env` file** or paste credentials in chat/email
- **Use environment variables in CI/CD** instead of committing credentials
- **Rotate tokens regularly** - create new tokens periodically and revoke old ones
- **Use read-only tokens if possible** - though Confluence API tokens have full access by default

### What Changed in This Version

This tool now follows security best practices:
- ✅ No credentials in command-line arguments (not visible in process lists or shell history)
- ✅ Credentials loaded from `.env` file or environment variables
- ✅ Centralized authentication logic
- ✅ Better error messages without exposing credentials

## Output Structure

When using `--with-children`, the script creates a directory structure mirroring the Confluence page hierarchy:

```
output_dir/
├── Parent Page.md
└── Parent Page/
    ├── Child Page 1.md
    ├── Child Page 2.md
    └── Child Page 2/
        └── Grandchild Page.md
```

## Project Structure

The codebase is organized for maintainability and security:

- `export_confluence.py` - Main script with export logic and CLI
- `config.py` - Configuration management and .env file parsing
- `auth.py` - Authentication handling (HTTP Basic Auth)
- `api_client.py` - Confluence REST API client
- `.env` - Your credentials (not committed to git)
- `.env.example` - Template for credentials

This separation of concerns makes the code easier to test, maintain, and extend.

## Limitations

- Basic HTML to Markdown conversion (may not handle all Confluence macros)
- No image downloads (images remain as HTML links)
- No attachment handling
- Tables may not convert perfectly

## Troubleshooting

### "Configuration Error: Username is required"
Make sure you have:
1. Created a `.env` file (copy from `.env.example`), OR
2. Set environment variables (`CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN`, `CONFLUENCE_BASE_URL`)

### "401 Unauthorized" - Authentication Failed
- Check that your API token is valid and not expired
- Verify your username (email) is correct
- Make sure there are no extra spaces in your `.env` file
- Try regenerating your API token at https://id.atlassian.com/manage-profile/security/api-tokens

### "403 Forbidden" - Access Denied
- Ensure you have permission to view the page
- Check that you're using the correct Confluence base URL
- Verify the page isn't in a restricted space

### "404 Not Found" - Page Not Found
- Verify the page ID is correct (check the URL when viewing the page)
- Ensure the page exists and hasn't been deleted
- Check that you have access to view the page

### Configuration File Not Found
If you get an error about missing configuration, try:
```bash
# Check if .env file exists
ls -la .env

# If not, copy from example
cp .env.example .env

# Edit with your credentials
nano .env  # or use your preferred editor
```

## Examples

```bash
# Make sure you've set up your .env file first
# cp .env.example .env
# (edit .env with your credentials)

# Export a single page to a file
python3 export_confluence.py 123456 my-page.md

# Export a single page to stdout
python3 export_confluence.py 123456

# Export a page tree to a directory
python3 export_confluence.py 123456 my-docs --with-children

# Export with limited depth (prevents deep recursion)
python3 export_confluence.py 123456 my-docs --with-children --max-depth 3

# Use a different .env file
python3 export_confluence.py 123456 my-page.md --env-file ~/my-credentials/.env
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

This means you can freely use, modify, and distribute this script for any purpose, including commercial use.
