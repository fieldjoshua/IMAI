# P.A.R.A. Life OS

A comprehensive Python-based system that uses Notion as the central hub for organizing your life using the P.A.R.A. methodology. Automatically integrates files, calendar events, emails, contacts, and other data sources through AI-powered categorization.

## Features

- **P.A.R.A. Organization**: Automatically categorizes items into Projects, Areas, Resources, or Archives
- **Notion Integration**: Central hub for all your information
- **File Watching**: Monitors directories for new files and processes them automatically
- **Email Integration**: Syncs Gmail and categorizes emails
- **Calendar Integration**: Syncs Google Calendar events
- **Contacts Integration**: Syncs Google Contacts
- **AI-Powered**: Uses Claude AI for intelligent categorization
- **Universal Search**: Search across all your organized data

## Prerequisites

- Python 3.10 or higher
- Notion account with API access
- Anthropic API key (for Claude AI)
- Google Cloud project with OAuth credentials (for Gmail, Calendar, Contacts)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AIAm
```

2. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the setup wizard:
```bash
python setup.py
```

The setup wizard will guide you through:
- Setting up environment variables
- Creating Notion databases
- Configuring Google OAuth
- Verifying your setup

## Configuration

### Environment Variables

Create a `.env` file in the project root (or use the setup wizard):

```bash
# Anthropic Claude API
ANTHROPIC_API_KEY="sk-ant-..."

# Notion API
NOTION_API_KEY="secret_..."
NOTION_PARENT_PAGE_ID="your_parent_page_id"
NOTION_INBOX_DB_ID="your_master_inbox_db_id"
NOTION_PROJECTS_DB_ID="your_projects_db_id"
NOTION_AREAS_DB_ID="your_areas_db_id"
NOTION_RESOURCES_DB_ID="your_resources_db_id"

# Google OAuth
GOOGLE_CLIENT_ID="your_google_client_id"
GOOGLE_CLIENT_SECRET="your_google_client_secret"
GOOGLE_REDIRECT_URI="http://localhost:8080/callback"

# Watch Directories (JSON array)
WATCH_DIRECTORIES='["/path/to/directory1", "/path/to/directory2"]'

# Obsidian Vault Path
OBSIDIAN_VAULT_PATH="/path/to/obsidian/vault"

# Optional: Processing intervals (seconds)
GMAIL_SYNC_INTERVAL=300
CALENDAR_SYNC_INTERVAL=300
CONTACTS_SYNC_INTERVAL=600
```

### Notion Setup

1. Create a Notion integration:
   - Go to https://www.notion.so/my-integrations
   - Click "New integration"
   - Give it a name and select your workspace
   - Copy the "Internal Integration Token" (this is your `NOTION_API_KEY`)

2. Create a parent page in Notion where databases will be created

3. Share the parent page with your integration:
   - Open the parent page
   - Click "..." → "Add connections"
   - Select your integration

4. Run the setup wizard to create databases automatically, or create them manually using the schemas in `notion/schemas.py`

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Gmail API
   - Google Calendar API
   - People API (for Contacts)
4. Create OAuth 2.0 credentials:
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: "Web application"
   - Authorized redirect URIs: `http://localhost:8080/callback`
5. Copy the Client ID and Client Secret to your `.env` file

## Usage

### Running the Main Application

Start the orchestrator:
```bash
python main.py
```

This will:
- Start watching configured directories for new files
- Periodically sync Gmail, Calendar, and Contacts (if enabled)
- Process and categorize all items into Notion

### Search Utility

Search your Master Inbox:
```python
from utils.search import search_notion_inbox

# Search by query
results = search_notion_inbox(query="project name")

# Filter by tags
results = search_notion_inbox(tags=["important", "work"])

# Filter by P.A.R.A. type
results = search_notion_inbox(para_type="Project")
```

### Command Line Search

Create a simple CLI script (e.g., `search_cli.py`):
```python
#!/usr/bin/env python3
import sys
from utils.search import search_notion_inbox, format_search_result

query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
results = search_notion_inbox(query=query)

for page in results:
    print(format_search_result(page))
    print("-" * 60)
```

## Project Structure

```
AIAm/
├── main.py                 # Main orchestrator
├── config.py               # Configuration management
├── setup.py                # Setup wizard
├── requirements.txt         # Python dependencies
├── .env                    # Environment variables (gitignored)
├── .cursorrules            # Cursor editor guardrails
├── notion/                 # Notion API integration
│   ├── client.py
│   ├── databases.py
│   └── schemas.py
├── processors/             # Content processing
│   ├── ai_processor.py    # Claude AI integration
│   ├── file_processor.py  # File content extraction
│   └── para_classifier.py # P.A.R.A. classification
├── integrations/           # External service integrations
│   ├── base.py
│   ├── file_watcher.py
│   ├── gmail.py
│   ├── calendar.py
│   └── contacts.py
├── utils/                  # Utility functions
│   ├── search.py
│   └── uri_builder.py
└── trackers/               # PR tracking
    ├── dependencies.md
    └── terminology.md
```

## P.A.R.A. Methodology

- **Projects**: Goals with defined end dates (e.g., "Launch New Website")
- **Areas**: Broad responsibilities to maintain (e.g., "Finances", "Health")
- **Resources**: Topics of ongoing interest (e.g., "AI Development", "Photography")
- **Archives**: Inactive items from Projects, Areas, or Resources

The system uses Claude AI to automatically categorize items based on their content and your existing P.A.R.A. structure.

## Supported File Types

- **Documents**: PDF, DOCX, TXT, MD
- **Images**: JPEG, PNG (with OCR)
- **Data**: CSV, JSON, XML
- **Archives**: ZIP (extracts and processes contents)

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
ruff check .
mypy .
```

### Adding New Integrations

1. Create a new class in `integrations/` inheriting from `BaseIntegration`
2. Implement `authenticate()` and `sync()` methods
3. Add to `main.py` orchestrator
4. Update configuration as needed

## Troubleshooting

### Notion API Errors

- Verify your API key is correct
- Ensure databases exist and IDs are correct
- Check that your integration has access to the parent page

### Google OAuth Issues

- Verify redirect URI matches exactly: `http://localhost:8080/callback`
- Ensure APIs are enabled in Google Cloud Console
- Check that credentials are correctly set in `.env`

### File Processing Errors

- Verify file paths exist and are readable
- Check file permissions
- Ensure required libraries are installed (e.g., pytesseract for OCR)

### Claude API Errors

- Verify API key is correct
- Check token usage limits
- Ensure you have sufficient API credits

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

[Add support information here]

