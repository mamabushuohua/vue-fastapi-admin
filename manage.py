#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Load environment variables before importing app modules
from dotenv import load_dotenv

# Load .env file if it exists
env_path = Path(project_root) / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

from app import app
from app.commands.import_menu_api import ImportMenuAPICommand
from app.commands.manager import CommandManager
from app.commands.reset_db import ResetDBCommand


def main():
    # Create command manager
    command_manager = CommandManager(app)

    # Register commands
    command_manager.register("reset_db", ResetDBCommand)
    command_manager.register("import_menu_api", ImportMenuAPICommand)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Custom command management tool.")
    parser.add_argument("command", nargs="?", help="The command to execute")
    parser.add_argument("--list", action="store_true", help="List all available commands")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments for the command")

    args = parser.parse_args()

    # List commands if requested
    if args.list:
        command_manager.list_commands()
        return

    # Execute command if provided
    if args.command:
        command_manager.execute(args.command, *args.args)
    else:
        print("No command specified. Use --list to see available commands.")
        parser.print_help()


if __name__ == "__main__":
    main()
