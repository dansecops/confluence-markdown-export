# Confluence Page Exporter

A Python script to export Confluence pages to Markdown format.

## Features

- ✅ Export single pages to Markdown
- ✅ Recursively export pages with all children
- ✅ Simple HTML to Markdown conversion
- ✅ Secure credential management via environment variables or command-line args
- ✅ No external dependencies (uses only Python stdlib)

## Setup

### Option 1: Using Environment Variables (Recommended)

1. Copy `confluence_env.sh.example` to `confluence_env.sh`:
   ```bash
   cp confluence_env.sh.example confluence_env.sh
   ```

2. Edit `confluence_env.sh` with your credentials:
   ```bash
   export CONFLUENCE_USERNAME="your-email@company.com"
   export CONFLUENCE_API_TOKEN="your-api-token-here"
   export CONFLUENCE_BASE_URL="https://your-company.atlassian.net/wiki"
   ```

3. Source the file to load credentials:
   ```bash
   source confluence_env.sh
   ```

### Option 2: Command-Line Arguments

Pass credentials directly as arguments (see examples below).

## Usage

### Export a Single Page

```bash
# Using environment variables
source confluence_env.sh
python3 export_confluence.py 4818731035 output.md

# Using command-line arguments
python3 export_confluence.py 4818731035 output.md \
  -u "user@example.com" \
  -t "YOUR_API_TOKEN" \
  -b "https://company.atlassian.net/wiki"
```

### Export a Page with All Children

```bash
# Using environment variables
source confluence_env.sh
python3 export_confluence.py 4818731035 output_dir --with-children

# Using command-line arguments
python3 export_confluence.py 4818731035 output_dir --with-children \
  -u "user@example.com" \
  -t "YOUR_API_TOKEN" \
  -b "https://company.atlassian.net/wiki"
```

### Advanced Options

```bash
# Limit recursion depth
python3 export_confluence.py 4818731035 output_dir --with-children --max-depth 5

# Get help
python3 export_confluence.py --help
```

## How to Get Your API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "Confluence Exporter")
4. Copy the token immediately (you won't see it again)

## Finding Page IDs

The page ID is in the URL when viewing a Confluence page:

```
https://company.atlassian.net/wiki/spaces/SPACE/pages/4818731035/Page+Title
                                                          ^^^^^^^^^^
                                                          This is the page ID
```

## Security Notes

⚠️ **Important:**
- Never commit `confluence_env.sh` to git (it's in `.gitignore`)
- API tokens grant full access to your Confluence account
- Treat them like passwords

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

## Limitations

- Basic HTML to Markdown conversion (may not handle all Confluence macros)
- No image downloads (images remain as HTML links)
- No attachment handling
- Tables may not convert perfectly

## Troubleshooting

### "Error: Username is required"
Make sure you've either:
- Sourced the `confluence_env.sh` file, OR
- Provided `-u`, `-t`, and `-b` arguments

### "403 Forbidden" or "401 Unauthorized"
- Check that your API token is valid and not expired
- Verify your username (email) is correct
- Ensure you have permission to view the page

### "404 Not Found"
- Verify the page ID is correct
- Check that the Confluence base URL is correct
- Ensure the page exists and you have access to it

## Examples

```bash
# Load credentials
source confluence_env.sh

# Export a single page
python3 export_confluence.py 123456 my-page.md

# Export a page tree
python3 export_confluence.py 123456 my-docs --with-children

# Export with limited depth
python3 export_confluence.py 123456 my-docs --with-children --max-depth 3
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

This means you can freely use, modify, and distribute this script for any purpose, including commercial use.
