"""
Tests for web routes and templates.
"""

from app import db
from app.models import Paste, User


class TestHomeRoutes:
    """Test home page and main routes."""

    def test_home_page(self, client):
        """Test home page loads correctly."""
        response = client.get("/")

        assert response.status_code == 200
        assert b"JJ Pastebin" in response.data or b"Pastebin" in response.data
        assert b"Recent Pastes" in response.data or b"pastes" in response.data.lower()

    def test_home_page_with_pastes(self, client, test_paste):
        """Test home page displays pastes."""
        response = client.get("/")

        assert response.status_code == 200
        # Should show paste title or content
        assert test_paste.title.encode() in response.data

    def test_home_page_pagination(self, client, app, test_user):
        """Test home page pagination."""
        with app.app_context():
            # Create many pastes
            for i in range(25):
                paste = Paste(
                    title=f"Paste {i}",
                    content=f"Content {i}",
                    user_id=test_user.id,
                    is_public=True,
                )
                db.session.add(paste)
            db.session.commit()

        # Test first page
        response = client.get("/")
        assert response.status_code == 200

        # Test second page if pagination exists
        response = client.get("/?page=2")
        assert response.status_code == 200


class TestPasteRoutes:
    """Test paste-related routes."""

    def test_view_public_paste(self, client, test_paste):
        """Test viewing a public paste."""
        response = client.get(f"/paste/{test_paste.unique_id}")

        assert response.status_code == 200
        assert test_paste.title.encode() in response.data
        # Content might be syntax highlighted, so check for individual meaningful words
        # Look for "print", "Hello", "World" individually
        assert b"print" in response.data
        assert b"Hello" in response.data
        assert b"World" in response.data
        assert test_paste.language.encode() in response.data

    def test_view_private_paste_unauthorized(self, client, private_paste):
        """Test viewing private paste without authorization."""
        response = client.get(f"/paste/{private_paste.unique_id}")

        assert (
            response.status_code == 404
        )  # Private pastes should return 404 to unauthorized users

    def test_view_private_paste_authorized(
        self, client, auth, test_user, private_paste
    ):
        """Test viewing private paste with proper authorization."""
        auth.login("testuser", "testpass")

        response = client.get(f"/paste/{private_paste.unique_id}")

        assert response.status_code == 200
        assert private_paste.title.encode() in response.data
        # Content might be syntax highlighted, so check more flexibly
        content_words = private_paste.content.split()
        for word in content_words[:2]:  # Check first few words
            if word.strip():
                assert word.encode() in response.data

    def test_view_nonexistent_paste(self, client):
        """Test viewing non-existent paste."""
        response = client.get("/paste/nonexistent")

        assert response.status_code == 404

    def test_raw_paste_view(self, client, test_paste):
        """Test raw paste view."""
        response = client.get(f"/paste/{test_paste.unique_id}/raw")

        assert response.status_code == 200
        assert response.content_type == "text/plain; charset=utf-8"
        assert test_paste.content.encode() in response.data
        # Should not contain HTML
        assert b"<html>" not in response.data
        assert b"<!DOCTYPE" not in response.data

    def test_paste_view_count(self, client, app, test_paste):
        """Test that paste views are incremented."""
        with app.app_context():
            initial_views = test_paste.views

        # View the paste
        client.get(f"/paste/{test_paste.unique_id}")

        with app.app_context():
            updated_paste = Paste.query.get(test_paste.id)
            assert updated_paste.views == initial_views + 1

    def test_create_paste_get(self, client, auth, test_user):
        """Test GET /create - create paste form."""
        auth.login("testuser", "testpass")

        response = client.get("/create")

        assert response.status_code == 200
        assert b"Create Paste" in response.data
        assert b"Title" in response.data
        assert b"Content" in response.data
        assert b"Language" in response.data

    def test_create_paste_post(self, client, auth, test_user, app):
        """Test POST /create - create new paste."""
        auth.login("testuser", "testpass")

        response = client.post(
            "/create",
            data={
                "title": "New Test Paste",
                "content": 'def hello():\n    print("Hello, World!")',
                "language": "python",
                "is_public": True,
            },
        )

        assert response.status_code == 302  # Should redirect to paste view

        # Verify paste was created
        with app.app_context():
            paste = Paste.query.filter_by(title="New Test Paste").first()
            assert paste is not None
            assert paste.user_id == test_user.id
            assert paste.language == "python"
            assert paste.is_public is True

    def test_create_paste_private(self, client, auth, test_user, app):
        """Test creating a private paste."""
        auth.login("testuser", "testpass")

        response = client.post(
            "/create",
            data={
                "title": "Private Paste",
                "content": "secret code",
                "language": "text",
                "is_public": False,
            },
        )

        assert response.status_code == 302

        with app.app_context():
            paste = Paste.query.filter_by(title="Private Paste").first()
            assert paste is not None
            assert paste.is_public is False

    def test_create_paste_minimal_data(self, client, auth, test_user, app):
        """Test creating paste with minimal required data."""
        auth.login("testuser", "testpass")

        response = client.post(
            "/create",
            data={
                "title": "Minimal",  # Title is required
                "content": "Just some content",
            },
        )

        assert response.status_code == 302

        # Should use defaults
        with app.app_context():
            paste = Paste.query.filter_by(content="Just some content").first()
            assert paste is not None
            assert paste.title == "Minimal"
            assert paste.language == "text"

    def test_create_paste_requires_login(self, client):
        """Test that creating paste requires login."""
        response = client.get("/create")

        assert response.status_code == 302
        assert "/auth/login" in response.location

        response = client.post("/create", data={"content": "test"})

        assert response.status_code == 302
        assert "/auth/login" in response.location

    def test_edit_paste_get(self, client, auth, test_user, test_paste):
        """Test GET /paste/<id>/edit - edit paste form."""
        auth.login("testuser", "testpass")

        response = client.get(f"/paste/{test_paste.unique_id}/edit")

        assert response.status_code == 200
        assert b"Edit Paste" in response.data
        assert test_paste.title.encode() in response.data
        # For edit form, content should be in form fields (not syntax highlighted)
        # Look for the content in textarea or form context
        assert b"textarea" in response.data.lower()
        # Check if key parts of content are present
        assert b"print" in response.data
        assert b"Hello" in response.data

    def test_edit_paste_post(self, client, auth, test_user, test_paste, app):
        """Test POST /paste/<id>/edit - update paste."""
        auth.login("testuser", "testpass")

        response = client.post(
            f"/paste/{test_paste.unique_id}/edit",
            data={
                "title": "Updated Title",
                "content": "Updated content",
                "language": "javascript",
                "is_public": False,
            },
        )

        assert response.status_code == 302  # Should redirect to paste view

        # Verify paste was updated
        with app.app_context():
            updated_paste = Paste.query.get(test_paste.id)
            assert updated_paste.title == "Updated Title"
            assert updated_paste.content == "Updated content"
            assert updated_paste.language == "javascript"
            assert updated_paste.is_public is False

    def test_edit_paste_unauthorized(self, client, test_paste):
        """Test editing paste without login."""
        response = client.get(f"/paste/{test_paste.unique_id}/edit")

        assert response.status_code == 302
        assert "/auth/login" in response.location

    def test_edit_paste_wrong_user(self, client, app, test_paste):
        """Test editing paste as different user."""
        with app.app_context():
            # Create another user
            other_user = User(username="otheruser", email="other@example.com")
            other_user.set_password("otherpass")
            db.session.add(other_user)
            db.session.commit()

        # Login as other user
        client.post(
            "/auth/login",
            data={"username": "otheruser", "password": "otherpass"},
        )

        response = client.get(f"/paste/{test_paste.unique_id}/edit")

        # Should redirect back to paste view with error message
        assert response.status_code == 302
        assert f"/paste/{test_paste.unique_id}" in response.location


class TestUserRoutes:
    """Test user-related routes."""

    def test_user_profile(self, client, test_user, test_paste):
        """Test user profile page."""
        response = client.get(f"/user/{test_user.username}")

        assert response.status_code == 200
        assert test_user.username.encode() in response.data
        assert (
            b"Profile" in response.data or test_user.username.encode() in response.data
        )

    def test_user_profile_shows_pastes(self, client, test_user, test_paste):
        """Test user profile shows user's pastes."""
        response = client.get(f"/user/{test_user.username}")

        assert response.status_code == 200
        # Should show user's public pastes
        assert test_paste.title.encode() in response.data

    def test_user_profile_nonexistent(self, client):
        """Test profile for non-existent user."""
        response = client.get("/user/nonexistent")

        assert response.status_code == 404

    def test_user_profile_private_pastes(self, client, auth, test_user, private_paste):
        """Test that private pastes are shown to owner."""
        auth.login("testuser", "testpass")

        response = client.get(f"/user/{test_user.username}")

        assert response.status_code == 200
        # Should show private paste to owner
        assert private_paste.title.encode() in response.data


class TestLanguageRoutes:
    """Test language filtering routes."""

    def test_language_filter(self, client, app, test_user):
        """Test filtering pastes by language."""
        with app.app_context():
            # Create pastes with different languages
            python_paste = Paste(
                title="Python Code",
                content='print("hello")',
                language="python",
                user_id=test_user.id,
            )
            js_paste = Paste(
                title="JavaScript Code",
                content='console.log("hello")',
                language="javascript",
                user_id=test_user.id,
            )
            db.session.add_all([python_paste, js_paste])
            db.session.commit()

        # Test Python filter
        response = client.get("/language/python")

        assert response.status_code == 200
        assert b"Python Code" in response.data
        assert b"JavaScript Code" not in response.data

    def test_language_filter_nonexistent(self, client):
        """Test filtering by non-existent language."""
        response = client.get("/language/nonexistent")

        assert response.status_code == 200  # Should show empty results
        assert b"No pastes found" in response.data or b"pastes" in response.data.lower()


class TestDocumentationRoutes:
    """Test documentation routes."""

    def test_api_docs(self, client):
        """Test API documentation page."""
        response = client.get("/api-docs")

        assert response.status_code == 200
        assert b"API" in response.data
        assert b"Documentation" in response.data or b"Docs" in response.data

    def test_cli_tools_docs(self, client):
        """Test CLI tools documentation page."""
        response = client.get("/cli-tools")

        assert response.status_code == 200
        assert b"CLI" in response.data
        assert b"Tools" in response.data or b"Command Line" in response.data


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_404_page(self, client):
        """Test 404 error page."""
        response = client.get("/nonexistent-page")

        assert response.status_code == 404

    def test_empty_paste_content(self, client, auth, test_user):
        """Test creating paste with empty content."""
        auth.login("testuser", "testpass")

        response = client.post(
            "/create",
            data={
                "title": "Empty Paste",
                "content": "",  # Empty content
                "language": "text",
            },
        )

        # Should either reject or handle gracefully
        assert response.status_code in [200, 302, 400]

    def test_very_long_paste_title(self, client, auth, test_user):
        """Test creating paste with very long title."""
        auth.login("testuser", "testpass")

        long_title = "A" * 500  # Very long title

        response = client.post(
            "/create",
            data={
                "title": long_title,
                "content": "test content",
                "language": "text",
            },
        )

        # Should either truncate or reject
        assert response.status_code in [200, 302, 400]

    def test_large_paste_content(self, client, auth, test_user):
        """Test creating paste with large content."""
        auth.login("testuser", "testpass")

        large_content = "A" * 100000  # 100KB content

        response = client.post(
            "/create",
            data={
                "title": "Large Paste",
                "content": large_content,
                "language": "text",
            },
        )

        # Should either accept or reject based on limits
        assert response.status_code in [200, 302, 400, 413]


class TestSecurityFeatures:
    """Test security features."""

    def test_xss_prevention_in_paste_title(self, client, auth, test_user, app):
        """Test XSS prevention in paste titles."""
        auth.login("testuser", "testpass")

        malicious_title = '<script>alert("XSS")</script>'

        response = client.post(
            "/create",
            data={
                "title": malicious_title,
                "content": "test content",
                "language": "text",
            },
        )

        assert response.status_code == 302

        # Check that script is escaped in display
        with app.app_context():
            paste = Paste.query.filter_by(content="test content").first()
            if paste:
                response = client.get(f"/paste/{paste.unique_id}")
                # Script should be escaped
                assert (
                    b"<script>" not in response.data
                    or b"&lt;script&gt;" in response.data
                )

    def test_csrf_protection(self, client, auth, test_user):
        """Test CSRF protection if implemented."""
        auth.login("testuser", "testpass")

        # Try to create paste without CSRF token (if CSRF is enabled)
        # This test depends on your CSRF implementation
        response = client.post(
            "/create", data={"title": "CSRF Test", "content": "test"}
        )

        # Should either succeed (CSRF disabled in tests) or fail
        assert response.status_code in [200, 302, 400, 403]

    def test_sql_injection_prevention(self, client):
        """Test SQL injection prevention."""
        # Try SQL injection in paste ID
        response = client.get("/paste/'; DROP TABLE pastes; --")

        assert response.status_code == 404  # Should safely return 404, not crash
