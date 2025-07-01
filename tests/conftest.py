"""
Pytest configuration and fixtures for JJ Pastebin tests.
"""

import os
import tempfile

import pytest

from app import create_app, db
from app.models import Paste, User


@pytest.fixture
def app():
    """Create and configure a test app."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()

    # Create app with testing configuration
    app = create_app("testing")

    # Override configuration for testing
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "SECRET_KEY": "test-secret-key",
            "WTF_CSRF_ENABLED": False,  # Disable CSRF for testing
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def auth(client):
    """Authentication helper."""

    class AuthActions:
        def __init__(self, client):
            self._client = client

        def login(self, username="testuser", password="testpass"):
            return self._client.post(
                "/auth/login",
                data={"username": username, "password": password},
            )

        def logout(self):
            return self._client.get("/auth/logout")

        def register(
            self,
            username="testuser",
            email="test@example.com",
            password="testpass",
        ):
            return self._client.post(
                "/auth/register",
                data={
                    "username": username,
                    "email": email,
                    "password": password,
                    "password2": password,
                },
            )

    return AuthActions(client)


@pytest.fixture
def test_user(app):
    """Create a test user and return user data."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        user.set_password("testpass")
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        username = user.username
        email = user.email

    # Return a simple object with user data
    class UserData:
        def __init__(self, id, username, email):
            self.id = id
            self.username = username
            self.email = email

    return UserData(user_id, username, email)


@pytest.fixture
def admin_user(app):
    """Create an admin user and return user data."""
    with app.app_context():
        admin = User(username="admin", email="admin@example.com", is_superuser=True)
        admin.set_password("adminpass")
        db.session.add(admin)
        db.session.commit()
        admin_id = admin.id
        username = admin.username
        email = admin.email

    # Return a simple object with admin data
    class UserData:
        def __init__(self, id, username, email):
            self.id = id
            self.username = username
            self.email = email

    return UserData(admin_id, username, email)


@pytest.fixture
def test_paste(app, test_user):
    """Create a test paste and return paste data."""
    with app.app_context():
        paste = Paste(
            title="Test Paste",
            content='print("Hello, World!")',
            language="python",
            is_public=True,
            user_id=test_user.id,
        )
        db.session.add(paste)
        db.session.commit()
        paste_id = paste.id
        unique_id = paste.unique_id
        title = paste.title
        content = paste.content
        language = paste.language
        views = paste.views
        is_public = paste.is_public

    # Return a simple object with paste data
    class PasteData:
        def __init__(self, id, unique_id, title, content, language, views, is_public):
            self.id = id
            self.unique_id = unique_id
            self.title = title
            self.content = content
            self.language = language
            self.views = views
            self.is_public = is_public

    return PasteData(paste_id, unique_id, title, content, language, views, is_public)


@pytest.fixture
def private_paste(app, test_user):
    """Create a private test paste and return paste data."""
    with app.app_context():
        paste = Paste(
            title="Private Paste",
            content='secret_key = "very-secret"',
            language="python",
            is_public=False,
            user_id=test_user.id,
        )
        db.session.add(paste)
        db.session.commit()
        paste_id = paste.id
        unique_id = paste.unique_id
        title = paste.title
        content = paste.content
        language = paste.language
        views = paste.views
        is_public = paste.is_public

    # Return a simple object with paste data
    class PasteData:
        def __init__(self, id, unique_id, title, content, language, views, is_public):
            self.id = id
            self.unique_id = unique_id
            self.title = title
            self.content = content
            self.language = language
            self.views = views
            self.is_public = is_public

    return PasteData(paste_id, unique_id, title, content, language, views, is_public)


@pytest.fixture
def api_headers():
    """Standard API headers for testing."""
    return {"Content-Type": "application/json", "Accept": "application/json"}


@pytest.fixture
def sample_code():
    """Sample code snippets for testing."""
    return {
        "python": 'def hello():\n    print("Hello, World!")\n\nhello()',
        "javascript": 'function hello() {\n    console.log("Hello, World!");\n}\n\nhello();',
        "html": "<!DOCTYPE html>\n<html>\n<head>\n    <title>Test</title>\n</head>\n<body>\n    <h1>Hello, World!</h1>\n</body>\n</html>",
        "css": "body {\n    font-family: Arial, sans-serif;\n    margin: 0;\n    padding: 20px;\n}",
        "json": '{\n    "name": "test",\n    "version": "1.0.0",\n    "description": "Test JSON"\n}',
    }
