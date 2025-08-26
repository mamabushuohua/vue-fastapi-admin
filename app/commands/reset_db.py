import argparse
import asyncio
import os
import sys

import aiomysql
import pymysql
from tortoise import Tortoise
from tortoise.backends.mysql.client import MySQLClient
from tortoise.exceptions import DBConnectionError

from app.commands.base import BaseCommand
from app.core.init_app import init_data, init_db
from app.settings.config import settings


class ResetDBCommand(BaseCommand):
    help = "Reset the database by dropping all tables and recreating them."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Tells Django to NOT prompt the user for input of any kind.",
        )

    def handle(self, *args, **options):
        # Confirm with user before proceeding (unless --no-input is used)
        if not options.get("no_input"):
            confirm = input("This will reset the database. Are you sure? (yes/no): ")
            if confirm.lower() != "yes":
                print("Database reset cancelled.")
                return

        # Run the async reset_db function
        asyncio.run(self.reset_db())

    async def reset_db(self):
        # Handle different database types
        if settings.DB_TYPE == "mysql":
            await self._reset_mysql_db()
        else:
            # For SQLite and others, use the existing approach
            await Tortoise.init(config=settings.TORTOISE_ORM)
            await Tortoise._drop_databases()
            await init_db()

        # Reinitialize Tortoise with fresh connection
        await Tortoise.init(config=settings.TORTOISE_ORM)

        # Initialize data
        await init_data()

        print("Database has been reset successfully.")
