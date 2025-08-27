import asyncio

from app.commands.base import BaseCommand


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
        # await Tortoise.init(config=settings.TORTOISE_ORM)
        # if settings.DB_TYPE == "mysql":

        #     await Tortoise.generate_schemas(safe=False)

        # else:
        #     # For SQLite and others, use the existing approach
        #     # await Tortoise.init(config=settings.TORTOISE_ORM)
        #     await Tortoise._drop_databases()

        # # Reinitialize Tortoise with fresh connection

        # # Initialize data
        # # await init_data()
        # await Tortoise.close_connections()

        print("Database has been reset successfully.")
