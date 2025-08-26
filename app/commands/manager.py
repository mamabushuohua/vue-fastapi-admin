import argparse
import sys
from typing import Dict, Type

from .base import BaseCommand


class CommandManager:
    """
    Manages custom commands.
    """

    def __init__(self, app):
        self.app = app
        self.commands: Dict[str, Type[BaseCommand]] = {}

    def register(self, name: str, command_class: Type[BaseCommand]):
        """
        Register a command.
        """
        self.commands[name] = command_class

    def execute(self, name: str, *args, **options):
        """
        Execute a command by name.
        """
        if name not in self.commands:
            print(f"Unknown command: {name}")
            sys.exit(1)

        command_class = self.commands[name]
        command = command_class(self.app)

        # Create a parser for this command
        parser = argparse.ArgumentParser(
            prog=f"manage.py {name}",
            description=getattr(command_class, "help", ""),
        )

        # Add command-specific arguments
        if hasattr(command, "add_arguments"):
            command.add_arguments(parser)

        # Parse command-specific arguments
        parsed_args, remaining_args = parser.parse_known_args(list(args))

        # Convert parsed args to dict
        command_options = vars(parsed_args)

        # Merge with options
        command_options.update(options)

        command.handle(*remaining_args, **command_options)

    def list_commands(self):
        """
        List all available commands.
        """
        print("Available commands:")
        for name, command_class in self.commands.items():
            help_text = getattr(command_class, "help", "")
            print(f"  {name}: {help_text}")
