"""
Tests for API endpoints.
"""

import base64
import json

from app import db
from app.models import Paste, User


class TestAPIAuth:
    """Test API authentication."""

    def test_api_requires_auth(self, client, api_headers):
        """Test that API endpoints require authentication."""
        # Test POST without auth
        response = client.post(
            "/api/pastes",
            headers=api_headers,
            data=json.dumps({"title": "Test", "content": "test"}),
        )
        assert response.status_code == 401

        # Test GET specific paste without auth (should work for public)
        response = client.get("/api/pastes/nonexistent", headers=api_headers)
        assert response.status_code == 404  # Not 401, because it doesn't exist

    def test_basic_auth_valid(self, client, test_user, api_headers):
        """Test valid basic authentication."""
        auth_string = base64.b64encode(b"testuser:testpass").decode("utf-8")
        headers = {**api_headers, "Authorization": f"Basic {auth_string}"}

        response = client.post(
            "/api/pastes",
            headers=headers,
            data=json.dumps(
                {
                    "title": "Test Paste",
                    "content": 'print("hello")',
                    "language": "python",
                }
            ),
        )

        assert response.status_code == 201

    def test_basic_auth_invalid(self, client, api_headers):
        """Test invalid basic authentication."""
        auth_string = base64.b64encode(b"invalid:wrong").decode("utf-8")
        headers = {**api_headers, "Authorization": f"Basic {auth_string}"}

        response = client.post(
            "/api/pastes",
            headers=headers,
            data=json.dumps({"title": "Test", "content": "test"}),
        )

        assert response.status_code == 401


class TestAPIPastes:
    """Test API paste endpoints."""

    def test_get_all_pastes(self, client, test_paste, api_headers):
        """Test GET /api/pastes - get all public pastes."""
        response = client.get("/api/pastes", headers=api_headers)

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "pastes" in data
        assert len(data["pastes"]) >= 1

        # Check paste structure
        paste_data = data["pastes"][0]
        expected_fields = [
            "id",
            "title",
            "language",
            "is_public",
            "author",
            "created_at",
            "views",
        ]
        for field in expected_fields:
            assert field in paste_data

    def test_get_paste_by_id(self, client, test_paste, api_headers):
        """Test GET /api/pastes/<id> - get specific paste."""
        response = client.get(
            f"/api/pastes/{test_paste.unique_id}", headers=api_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["title"] == test_paste.title
        assert data["content"] == test_paste.content
        assert data["language"] == test_paste.language
        assert data["id"] == test_paste.unique_id

    def test_get_private_paste_unauthorized(self, client, private_paste, api_headers):
        """Test accessing private paste without authentication."""
        response = client.get(
            f"/api/pastes/{private_paste.unique_id}", headers=api_headers
        )

        assert response.status_code == 404  # Private pastes return 404 to non-owners

    def test_get_private_paste_authorized(
        self, client, test_user, private_paste, api_headers
    ):
        """Test accessing private paste with proper authentication."""
        auth_string = base64.b64encode(b"testuser:testpass").decode("utf-8")
        headers = {**api_headers, "Authorization": f"Basic {auth_string}"}

        response = client.get(f"/api/pastes/{private_paste.unique_id}", headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["title"] == private_paste.title

    def test_create_paste(self, client, test_user, api_headers):
        """Test POST /api/pastes - create new paste."""
        auth_string = base64.b64encode(b"testuser:testpass").decode("utf-8")
        headers = {**api_headers, "Authorization": f"Basic {auth_string}"}

        paste_data = {
            "title": "API Test Paste",
            "content": 'def test():\n    return "hello"',
            "language": "python",
            "is_public": True,
        }

        response = client.post(
            "/api/pastes", headers=headers, data=json.dumps(paste_data)
        )

        assert response.status_code == 201
        data = json.loads(response.data)

        assert "id" in data
        assert "url" in data
        assert data["title"] == paste_data["title"]

        # Verify paste was created in database
        created_paste = Paste.query.filter_by(unique_id=data["id"]).first()
        assert created_paste is not None
        assert created_paste.title == paste_data["title"]
        assert created_paste.user_id == test_user.id

    def test_create_paste_minimal(self, client, test_user, api_headers):
        """Test creating paste with minimal data."""
        auth_string = base64.b64encode(b"testuser:testpass").decode("utf-8")
        headers = {**api_headers, "Authorization": f"Basic {auth_string}"}

        paste_data = {"content": "Just some content"}

        response = client.post(
            "/api/pastes", headers=headers, data=json.dumps(paste_data)
        )

        assert response.status_code == 201
        data = json.loads(response.data)

        # Verify defaults were applied
        created_paste = Paste.query.filter_by(unique_id=data["id"]).first()
        assert created_paste.title == "Untitled"  # Default title
        assert created_paste.language == "text"  # Default language
        assert created_paste.is_public is True  # Default visibility

    def test_create_paste_invalid_data(self, client, test_user, api_headers):
        """Test creating paste with invalid data."""
        auth_string = base64.b64encode(b"testuser:testpass").decode("utf-8")
        headers = {**api_headers, "Authorization": f"Basic {auth_string}"}

        # Missing content
        response = client.post(
            "/api/pastes",
            headers=headers,
            data=json.dumps({"title": "No content"}),
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_update_paste(self, client, test_user, test_paste, api_headers):
        """Test PUT /api/pastes/<id> - update paste."""
        auth_string = base64.b64encode(b"testuser:testpass").decode("utf-8")
        headers = {**api_headers, "Authorization": f"Basic {auth_string}"}

        update_data = {
            "title": "Updated Title",
            "content": "Updated content",
            "language": "javascript",
        }

        response = client.put(
            f"/api/pastes/{test_paste.unique_id}",
            headers=headers,
            data=json.dumps(update_data),
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data["title"] == update_data["title"]

        # Verify database was updated
        updated_paste = Paste.query.get(test_paste.id)
        assert updated_paste.title == update_data["title"]
        assert updated_paste.content == update_data["content"]
        assert updated_paste.language == update_data["language"]

    def test_update_paste_unauthorized(self, client, api_headers, test_paste):
        """Test updating paste without proper authorization."""
        # No auth
        response = client.put(
            f"/api/pastes/{test_paste.unique_id}",
            headers=api_headers,
            data=json.dumps({"title": "Hacked"}),
        )

        assert response.status_code == 401

    def test_update_paste_wrong_user(self, client, app, test_paste, api_headers):
        """Test updating paste as different user."""
        with app.app_context():
            # Create another user
            other_user = User(username="otheruser", email="other@example.com")
            other_user.set_password("otherpass")
            db.session.add(other_user)
            db.session.commit()

        auth_string = base64.b64encode(b"otheruser:otherpass").decode("utf-8")
        headers = {**api_headers, "Authorization": f"Basic {auth_string}"}

        response = client.put(
            f"/api/pastes/{test_paste.unique_id}",
            headers=headers,
            data=json.dumps({"title": "Unauthorized"}),
        )

        assert response.status_code == 403

    def test_delete_paste(self, client, test_user, test_paste, api_headers):
        """Test DELETE /api/pastes/<id> - delete paste."""
        auth_string = base64.b64encode(b"testuser:testpass").decode("utf-8")
        headers = {**api_headers, "Authorization": f"Basic {auth_string}"}

        response = client.delete(f"/api/pastes/{test_paste.unique_id}", headers=headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data

        # Verify paste was deleted
        deleted_paste = Paste.query.get(test_paste.id)
        assert deleted_paste is None

    def test_delete_paste_unauthorized(self, client, test_paste, api_headers):
        """Test deleting paste without authorization."""
        response = client.delete(
            f"/api/pastes/{test_paste.unique_id}", headers=api_headers
        )

        assert response.status_code == 401

    def test_paste_not_found(self, client, api_headers):
        """Test accessing non-existent paste."""
        response = client.get("/api/pastes/nonexistent", headers=api_headers)

        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data


class TestAPIUsers:
    """Test API user endpoints."""

    def test_get_user_pastes(self, client, test_user, test_paste, api_headers):
        """Test GET /api/users/<username>/pastes - get user's pastes."""
        response = client.get(
            f"/api/users/{test_user.username}/pastes", headers=api_headers
        )

        assert response.status_code == 200
        data = json.loads(response.data)

        assert "pastes" in data
        assert "user" in data
        assert data["user"]["username"] == test_user.username
        assert len(data["pastes"]) >= 1

    def test_get_user_pastes_nonexistent(self, client, api_headers):
        """Test getting pastes for non-existent user."""
        response = client.get("/api/users/nonexistent/pastes", headers=api_headers)

        assert response.status_code == 404

    def test_get_user_profile(self, client, test_user, api_headers):
        """Test GET /api/users/<username> - get user profile."""
        response = client.get(f"/api/users/{test_user.username}", headers=api_headers)

        assert response.status_code == 200
        data = json.loads(response.data)

        expected_fields = ["username", "created_at", "paste_count"]
        for field in expected_fields:
            assert field in data

        assert data["username"] == test_user.username
        assert "email" not in data  # Email should not be exposed in API


class TestAPIFiltering:
    """Test API filtering and pagination."""

    def test_filter_by_language(self, client, test_user, api_headers):
        """Test filtering pastes by language."""
        auth_string = base64.b64encode(b"testuser:testpass").decode("utf-8")
        headers = {**api_headers, "Authorization": f"Basic {auth_string}"}

        # Create pastes with different languages
        languages = ["python", "javascript", "python"]
        for i, lang in enumerate(languages):
            client.post(
                "/api/pastes",
                headers=headers,
                data=json.dumps(
                    {
                        "title": f"Paste {i}",
                        "content": f"content {i}",
                        "language": lang,
                    }
                ),
            )

        # Filter by Python
        response = client.get("/api/pastes?language=python", headers=api_headers)
        assert response.status_code == 200
        data = json.loads(response.data)

        # Should have 2 Python pastes
        python_pastes = [p for p in data["pastes"] if p["language"] == "python"]
        assert len(python_pastes) == 2

    def test_pagination(self, client, test_user, api_headers):
        """Test API pagination."""
        auth_string = base64.b64encode(b"testuser:testpass").decode("utf-8")
        headers = {**api_headers, "Authorization": f"Basic {auth_string}"}

        # Create multiple pastes
        for i in range(15):
            client.post(
                "/api/pastes",
                headers=headers,
                data=json.dumps({"title": f"Paste {i}", "content": f"content {i}"}),
            )

        # Test first page
        response = client.get("/api/pastes?page=1&per_page=10", headers=api_headers)
        assert response.status_code == 200
        data = json.loads(response.data)

        assert len(data["pastes"]) == 10
        assert "pagination" in data
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["pages"] >= 2
        assert data["pagination"]["total"] >= 15

    def test_search_pastes(self, client, test_user, api_headers):
        """Test searching pastes by title/content."""
        auth_string = base64.b64encode(b"testuser:testpass").decode("utf-8")
        headers = {**api_headers, "Authorization": f"Basic {auth_string}"}

        # Create searchable pastes
        client.post(
            "/api/pastes",
            headers=headers,
            data=json.dumps(
                {
                    "title": "Flask Tutorial",
                    "content": "Flask application code",
                }
            ),
        )

        client.post(
            "/api/pastes",
            headers=headers,
            data=json.dumps(
                {
                    "title": "Django Project",
                    "content": "Django application code",
                }
            ),
        )

        # Search for Flask
        response = client.get("/api/pastes?search=Flask", headers=api_headers)
        assert response.status_code == 200
        data = json.loads(response.data)

        # Should find Flask paste
        flask_pastes = [p for p in data["pastes"] if "Flask" in p["title"]]
        assert len(flask_pastes) >= 1
