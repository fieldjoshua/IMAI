# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IMAI (Intelligent Management AI) is a Python-based P.A.R.A. methodology organizer that uses Notion as the central hub. It automatically integrates files, calendar events, emails, and contacts through AI-powered categorization using Claude AI.

## Core Architecture

### Main Components

1. **PARAOrchestrator** (`main.py:19-182`): Central orchestrator that coordinates all integrations and processing
   - Initializes Notion client, classifier, and integrations
   - Manages lifecycle of file watchers and sync operations
   - Handles graceful shutdown and error recovery

2. **NotionClient** (`notion/client.py`): Manages all Notion API interactions
   - Creates and updates database items
   - Handles page creation with rich content
   - Manages database schema operations

3. **PARAClassifier** (`processors/para_classifier.py`): AI-powered categorization using Claude
   - Analyzes content and categorizes into Projects/Areas/Resources/Archives
   - Extracts tags and keywords
   - Determines appropriate P.A.R.A. category based on content analysis

4. **Integration System** (`integrations/`):
   - **BaseIntegration** (`integrations/base.py`): Abstract base for all integrations
   - **FileWatcher** (`integrations/file_watcher.py`): Monitors directories for new files
   - **GmailIntegration** (`integrations/gmail.py`): Syncs Gmail emails
   - **CalendarIntegration** (`integrations/calendar.py`): Syncs Google Calendar events
   - **ContactsIntegration** (`integrations/contacts.py`): Syncs Google Contacts

5. **File Processing** (`processors/file_processor.py`): Extracts content from various file types
   - Supports PDF, DOCX, TXT, MD, images (with OCR), CSV, JSON, XML, ZIP

## Development Commands

### Setup and Installation
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run setup wizard (creates .env and Notion databases)
python setup.py

# Verify setup
python -c "from config import Config; Config().validate()"
```

### Running the Application
```bash
# Start the main orchestrator
python main.py

# Run in debug mode (more verbose output)
IMAI_DEBUG=true python main.py
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_file_processor.py

# Run with coverage
pytest --cov=. tests/

# Run tests for specific PR phase
pytest -m "pr01"  # Replace with actual PR marker
```

### Code Quality
```bash
# Format code
black .

# Check linting
ruff check .

# Type checking
mypy .

# All quality checks
black . && ruff check . && mypy .
```

### PR Workflow Commands
```bash
# Create a new PR (runs validation automatically)
./scripts/create_pr.sh

# Verify PR compliance manually
python scripts/verify_pr.py

# Update dependency/terminology trackers
python scripts/update_trackers.py

# Clean PR after CI fixes
python scripts/clean_pr.py
```

## Configuration Management

### Environment Variables
The project uses `.env` file for configuration. Key variables include:
- `ANTHROPIC_API_KEY`: Claude AI API key for content analysis
- `NOTION_API_KEY`: Notion integration token
- `NOTION_*_DB_ID`: Database IDs for P.A.R.A. categories
- `GOOGLE_*`: OAuth credentials for Google services
- `WATCH_DIRECTORIES`: JSON array of directories to monitor
- `*_SYNC_INTERVAL`: Sync intervals in seconds for each integration

### Configuration Flow
1. `config.py:Config` class loads from environment
2. Validates required fields based on enabled features
3. Provides typed access to all configuration values
4. Auto-converts JSON strings and handles defaults

## PR and Testing Requirements

### PR Versioning
All PRs must follow the versioning format defined in `.cursorrules`:
- Format: `PR #XX(a) — [Phase Name]` (letter increments for iterations)
- Include version history in PR description
- Track progression through CI checks

### Test Markers
Tests must be marked with PR phase markers:
```python
@pytest.mark.pr01  # For PR #01
def test_feature():
    pass
```

### Mandatory Updates for PRs
1. Update `trackers/dependencies.md` when adding/modifying dependencies
2. Update `trackers/terminology.md` when introducing new concepts
3. Ensure all tests pass before creating PR
4. Remove all debug code (print statements, temporary logging)

### Commit Message Format
Follow conventions in `docs/COMMIT_CONVENTIONS.md`:
- Format: `<type>: <subject>` (e.g., `feat: add file watcher`)
- Types: feat, fix, test, docs, refactor, chore, style, perf, ci, build

## Critical Implementation Notes

### Notion API Integration
- Database schemas are defined in `notion/schemas.py`
- All database operations go through `NotionClient` class
- Rate limiting is handled automatically with exponential backoff
- Page creation includes automatic property mapping and rich text formatting

### File Processing Flow
1. File detected by `FileWatcher` or added manually
2. Content extracted by `FileProcessor` based on file type
3. Content analyzed by `PARAClassifier` using Claude AI
4. Item created in appropriate Notion database
5. Original file path stored as reference

### Google OAuth Flow
1. Initial authorization redirects to `http://localhost:8080/callback`
2. Tokens stored in `.token/` directory (gitignored)
3. Auto-refresh handled by google-auth library
4. Each integration manages its own token file

### Error Handling Strategy
- All integrations return standardized result dictionaries
- Failures are logged but don't stop the orchestrator
- Retry logic with exponential backoff for API failures
- Graceful degradation when services unavailable

## Anti-Patterns to Avoid

1. **Never use mock implementations** - All tests must use real APIs/data
2. **Never commit without running tests** - Use pre-commit hooks
3. **Never bypass the PARAClassifier** - All items must be categorized
4. **Never modify trackers without PR** - Tracker updates are mandatory for PRs
5. **Never store credentials in code** - Use environment variables only

## Debugging Tips

### Common Issues
- **Notion API errors**: Check API key and database IDs in `.env`
- **Google OAuth failures**: Verify redirect URI matches exactly
- **File processing errors**: Check file permissions and formats
- **Claude API errors**: Verify API key and check rate limits

### Useful Debug Commands
```bash
# Check Notion connection
python -c "from notion.client import NotionClient; NotionClient('<api_key>').get_database('<db_id>')"

# Test file processor
python -c "from processors.file_processor import FileProcessor; print(FileProcessor.extract_content('path/to/file'))"

# Verify Google OAuth
python -c "from integrations.gmail import GmailIntegration; GmailIntegration(Config()).authenticate()"
```

## Architecture Decision Records

1. **Notion as Central Hub**: Chosen for rich API, database capabilities, and existing user adoption
2. **P.A.R.A. Methodology**: Provides clear organizational structure that maps well to different content types
3. **Claude AI for Classification**: Superior context understanding for accurate categorization
4. **Python Ecosystem**: Rich libraries for document processing and API integrations
5. **Modular Integration Pattern**: Each integration is independent, allowing easy addition/removal