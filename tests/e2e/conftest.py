import multiprocessing
import time

import pytest
import uvicorn
from playwright.sync_api import BrowserContext
from sqlalchemy import create_engine, text

from app.config import settings
from app.database import Base

# Import models to register them with Base.metadata
from app.models import Calculation, User  # noqa: F401


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine for E2E tests."""
    engine = create_engine(settings.test_database_url)
    # Ensure all models are imported before creating tables
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def clean_db(test_db_engine):
    """Clean the database before each test."""
    with test_db_engine.connect() as conn:
        # Check if tables exist before truncating
        result = conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )
        )
        existing_tables = [row[0] for row in result]

        if "calculations" in existing_tables:
            conn.execute(text("TRUNCATE TABLE calculations RESTART IDENTITY CASCADE"))
        if "users" in existing_tables:
            conn.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
        conn.commit()
    yield
    with test_db_engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )
        )
        existing_tables = [row[0] for row in result]

        if "calculations" in existing_tables:
            conn.execute(text("TRUNCATE TABLE calculations RESTART IDENTITY CASCADE"))
        if "users" in existing_tables:
            conn.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
        conn.commit()


def run_server():
    """Run the FastAPI server in a separate process."""
    import os

    os.environ["DATABASE_URL"] = settings.test_database_url
    os.environ["TEST_DATABASE_URL"] = settings.test_database_url

    from main import app

    config = uvicorn.Config(
        app, host="127.0.0.1", port=8000, log_level="error", access_log=False
    )
    server = uvicorn.Server(config)
    server.run()


@pytest.fixture(scope="session")
def server():
    """Start the FastAPI server for E2E tests."""
    proc = multiprocessing.Process(target=run_server, daemon=True)
    proc.start()
    time.sleep(2)
    yield
    proc.terminate()
    proc.join(timeout=5)
    if proc.is_alive():
        proc.kill()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
        "permissions": ["clipboard-read", "clipboard-write"],
    }


@pytest.fixture(scope="function")
def page(context: BrowserContext, server, clean_db):
    """Create a new page for each test with clean database."""
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture
def unique_user_data():
    """Generate unique user data for each test to avoid conflicts."""
    import random
    import string

    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return {
        "username": f"testuser_{suffix}",
        "email": f"test_{suffix}@example.com",
        "password": "SecurePass123",
    }
