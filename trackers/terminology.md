# Terminology Tracker

This file tracks all terminology, concepts, and naming conventions used in the IMAI project.

## P.A.R.A. Methodology Terms

### Core Concepts
- **Projects**: Goals with defined end dates (e.g., "Launch New Website")
- **Areas**: Broad responsibilities to maintain (e.g., "Finances")
- **Resources**: Topics of ongoing interest (e.g., "AI Development")
- **Archives**: Inactive items from Projects, Areas, or Resources

### Database Names
- **Master Inbox**: Central repository database in Notion
- **Projects Database**: Notion database for Projects
- **Areas Database**: Notion database for Areas
- **Resources Database**: Notion database for Resources

## Notion Property Names

### Master Inbox Properties
- `name` (Title) - Name/title of the item
- `status` (Select) - Status: New, Processing, Categorized, Archived
- `type` (Select) - Type: File, Email, Calendar, Contact, Other
- `source_path` (Text/URL) - Source path or URL
- `content` (Text) - Extracted content from source
- `summary` (Text) - AI-generated summary
- `tags` (Multi-select) - Tags for categorization
- `para_type` (Select) - P.A.R.A. type: Project, Area, Resource, Archive
- `project_relation` (Relation) - Link to Projects database
- `area_relation` (Relation) - Link to Areas database
- `resource_relation` (Relation) - Link to Resources database
- `created_date` (Created time) - When item was created
- `processed_date` (Date) - When item was processed

### Projects Database Properties
- `name` (Title)
- `status` (Select)
- `start_date` (Date)
- `end_date` (Date)
- `tags` (Multi-select)

### Areas Database Properties
- `name` (Title)
- `status` (Select)
- `tags` (Multi-select)
- `description` (Text)

### Resources Database Properties
- `name` (Title)
- `status` (Select)
- `tags` (Multi-select)
- `description` (Text)

## Code Terminology

### Functions/Methods
- `get_para_categories()` - Fetches current Projects, Areas, Resources from Notion
- `get_file_content()` - Extracts content from files
- `process_with_ai()` - Processes content with Claude AI
- `add_to_notion()` - Adds entry to Master Inbox database
- `NewFileHandler` - File watcher event handler class

### Variables
- `para_type` - P.A.R.A. classification type (Project/Area/Resource/Archive)
- `para_link` - Specific Project/Area/Resource name to link to

## Integration Names

### Services
- **Gmail** - Google Gmail integration
- **Google Calendar** - Google Calendar integration
- **Google Contacts** - Google Contacts integration
- **Notion** - Notion API integration
- **Claude** - Anthropic Claude AI (not OpenAI)

### File Types
- PDF, DOCX, TXT, MD - Document formats
- JPEG, PNG - Image formats (with OCR)
- CSV, JSON, XML - Data formats
- ZIP - Archive format

## URI Formats

- `obsidian://open?vault=...&file=...` - Obsidian URI format
- `file:///path/to/file` - Local file URI format
- `notion://...` - Notion page URL format

## Version History

- **Initial**: Core P.A.R.A. terminology and Notion property names defined

