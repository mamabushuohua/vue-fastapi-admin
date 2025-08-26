import asyncio

from tortoise import Tortoise

from app.commands.base import BaseCommand
from app.controllers.api import api_controller
from app.settings.config import settings


class ImportMenuAPICommand(BaseCommand):
    help = "Import new menu APIs from the application."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force import even if APIs already exist",
        )

    def handle(self, *args, **options):
        # Run the async import_menu_api function
        asyncio.run(self.import_menu_api(options.get("force", False)))

    async def import_menu_api(self, force=False):
        # Initialize Tortoise
        await Tortoise.init(config=settings.TORTOISE_ORM)

        # Check if force option is used
        if force:
            print("Force importing menu APIs...")

        # Refresh APIs
        await api_controller.refresh_api()

        print("Menu APIs have been imported successfully.")
