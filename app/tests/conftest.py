import asyncio
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
env_path = project_root / ".env-test"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

# Initialize the app for testing
from app import create_app
from app.core.redis import init_redis, close_redis


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def app():
    """Create and configure a new app instance for each test session."""
    # Initialize Redis
    await init_redis()

    # Create the app
    app = create_app()

    yield app

    # Clean up
    await close_redis()


@pytest.fixture(scope="session")
async def client(app):
    """Create a test client for the app."""
    from httpx import AsyncClient

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
