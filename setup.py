"""Interactive setup wizard for IMAI."""

import os
import json
from pathlib import Path
from notion.client import NotionClient
from notion.databases import create_para_databases
from config import Config


def print_header(text: str) -> None:
    """Print formatted header.

    Args:
        text: Header text
    """
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def get_input(prompt: str, default: str = "") -> str:
    """Get user input with optional default.

    Args:
        prompt: Input prompt
        default: Default value

    Returns:
        User input or default
    """
    if default:
        response = input(f"{prompt} [{default}]: ").strip()
        return response if response else default
    else:
        return input(f"{prompt}: ").strip()


def setup_environment() -> None:
    """Set up environment variables."""
    print_header("Environment Setup")

    env_file = Path(".env")
    if env_file.exists():
        overwrite = get_input(".env file exists. Overwrite? (y/N)", "N")
        if overwrite.lower() != "y":
            print("Skipping environment setup.")
            return

    print("Enter your API keys and configuration:")
    print("(Press Enter to skip optional fields)\n")

    env_vars = {}

    # Anthropic API Key
    anthropic_key = get_input("Anthropic API Key (ANTHROPIC_API_KEY)")
    if anthropic_key:
        env_vars["ANTHROPIC_API_KEY"] = anthropic_key

    # Notion API Key
    notion_key = get_input("Notion API Key (NOTION_API_KEY)")
    if notion_key:
        env_vars["NOTION_API_KEY"] = notion_key

    # Notion Parent Page ID
    parent_page = get_input("Notion Parent Page ID (NOTION_PARENT_PAGE_ID)")
    if parent_page:
        env_vars["NOTION_PARENT_PAGE_ID"] = parent_page

    # Google OAuth
    print("\nGoogle OAuth Configuration:")
    google_client_id = get_input("Google Client ID (GOOGLE_CLIENT_ID)")
    if google_client_id:
        env_vars["GOOGLE_CLIENT_ID"] = google_client_id

    google_client_secret = get_input("Google Client Secret (GOOGLE_CLIENT_SECRET)")
    if google_client_secret:
        env_vars["GOOGLE_CLIENT_SECRET"] = google_client_secret

    # Watch Directories
    print("\nWatch Directories (comma-separated or JSON array):")
    watch_dirs = get_input("Watch Directories (WATCH_DIRECTORIES)")
    if watch_dirs:
        # Try to parse as JSON, otherwise treat as comma-separated
        try:
            json.loads(watch_dirs)
            env_vars["WATCH_DIRECTORIES"] = watch_dirs
        except json.JSONDecodeError:
            dirs_list = [d.strip() for d in watch_dirs.split(",") if d.strip()]
            env_vars["WATCH_DIRECTORIES"] = json.dumps(dirs_list)

    # Obsidian Vault
    obsidian_path = get_input("Obsidian Vault Path (OBSIDIAN_VAULT_PATH)")
    if obsidian_path:
        env_vars["OBSIDIAN_VAULT_PATH"] = obsidian_path

    # Write .env file
    with open(".env", "w") as f:
        for key, value in env_vars.items():
            f.write(f'{key}="{value}"\n')

    print("\n✓ Environment variables saved to .env")


def setup_notion_databases() -> None:
    """Set up Notion databases."""
    print_header("Notion Database Setup")

    config = Config()
    if not config.notion_api_key:
        print("ERROR: NOTION_API_KEY not set. Please run environment setup first.")
        return

    if not config.notion_parent_page_id:
        print("ERROR: NOTION_PARENT_PAGE_ID not set. Please run environment setup first.")
        return

    # Check if databases already exist
    if all(
        [
            config.notion_inbox_db_id,
            config.notion_projects_db_id,
            config.notion_areas_db_id,
            config.notion_resources_db_id,
        ]
    ):
        print("Databases already configured via environment variables.")
        use_existing = get_input("Use existing databases? (Y/n)", "Y")
        if use_existing.lower() != "n":
            print("Using existing databases.")
            return

    print("Creating P.A.R.A. databases in Notion...")
    try:
        client = NotionClient(config.notion_api_key)
        database_ids = create_para_databases(client)

        print("\n✓ Databases created successfully!")
        print("\nAdd these to your .env file:")
        print(f'NOTION_INBOX_DB_ID="{database_ids["inbox"]}"')
        print(f'NOTION_PROJECTS_DB_ID="{database_ids["projects"]}"')
        print(f'NOTION_AREAS_DB_ID="{database_ids["areas"]}"')
        print(f'NOTION_RESOURCES_DB_ID="{database_ids["resources"]}"')

    except Exception as e:
        print(f"ERROR: Failed to create databases: {e}")


def setup_google_oauth() -> None:
    """Guide user through Google OAuth setup."""
    print_header("Google OAuth Setup")

    print("To set up Google OAuth:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select existing")
    print("3. Enable APIs: Gmail API, Calendar API, People API (Contacts)")
    print("4. Create OAuth 2.0 credentials")
    print("5. Add authorized redirect URI: http://localhost:8080/callback")
    print("6. Copy Client ID and Client Secret")
    print("\nRun this setup again after creating credentials.")


def verify_setup() -> None:
    """Verify setup is complete."""
    print_header("Setup Verification")

    config = Config()
    missing = config.validate()

    if missing:
        print("⚠ Missing required configuration:")
        for item in missing:
            print(f"  - {item}")
        print("\nPlease complete the setup above.")
    else:
        print("✓ All required configuration present!")

        # Test Notion connection
        try:
            client = NotionClient(config.notion_api_key)
            print("✓ Notion API connection successful")
        except Exception as e:
            print(f"⚠ Notion API connection failed: {e}")

        # Test Anthropic connection
        try:
            from processors.ai_processor import ClaudeProcessor

            processor = ClaudeProcessor(config.anthropic_api_key)
            print("✓ Claude API connection successful")
        except Exception as e:
            print(f"⚠ Claude API connection failed: {e}")


def main() -> None:
    """Main setup wizard."""
    print_header("IMAI Setup Wizard")

    while True:
        print("\nSetup Options:")
        print("1. Environment Variables (.env)")
        print("2. Notion Databases")
        print("3. Google OAuth Guide")
        print("4. Verify Setup")
        print("5. Exit")

        choice = get_input("\nSelect option", "4")

        if choice == "1":
            setup_environment()
        elif choice == "2":
            setup_notion_databases()
        elif choice == "3":
            setup_google_oauth()
        elif choice == "4":
            verify_setup()
        elif choice == "5":
            print("Setup complete!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()

