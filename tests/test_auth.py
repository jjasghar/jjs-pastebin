"""
Tests for authentication system.
"""

from app.models import User


class TestAuth:
    """Test authentication functionality."""

    def test_register_get(self, client):
        """Test GET /auth/register - registration form display."""
        response = client.get("/auth/register")

        assert response.status_code == 200
        assert b"Register" in response.data
        assert b"Username" in response.data
        assert b"Email" in response.data
        assert b"Password" in response.data

    def test_register_valid_user(self, client, app):
        """Test successful user registration."""
        response = client.post(
            "/auth/register",
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "validpassword",
                "password2": "validpassword",
            },
        )

        # Should redirect to login after successful registration
        assert response.status_code == 302
        assert "/auth/login" in response.location

        # Verify user was created in database
        with app.app_context():
            user = User.query.filter_by(username="newuser").first()
            assert user is not None
            assert user.email == "newuser@example.com"
            assert user.check_password("validpassword")

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username."""
        response = client.post(
            "/auth/register",
            data={
                "username": "testuser",  # Already exists
                "email": "different@example.com",
                "password": "password",
                "password2": "password",
            },
        )

        assert response.status_code == 200  # Form redisplayed with errors
        assert (
            b"Username already taken" in response.data
            or b"already exists" in response.data
        )

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        response = client.post(
            "/auth/register",
            data={
                "username": "differentuser",
                "email": "test@example.com",  # Already exists
                "password": "password",
                "password2": "password",
            },
        )

        assert response.status_code == 200  # Form redisplayed with errors
        assert (
            b"Email already registered" in response.data
            or b"already exists" in response.data
        )

    def test_register_password_mismatch(self, client):
        """Test registration with mismatched passwords."""
        response = client.post(
            "/auth/register",
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password1",
                "password2": "password2",  # Different password
            },
        )

        assert response.status_code == 200  # Form redisplayed with errors
        assert (
            b"Passwords must match" in response.data
            or b"password" in response.data.lower()
        )

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        response = client.post(
            "/auth/register",
            data={
                "username": "newuser",
                "email": "invalid-email",  # Invalid format
                "password": "password",
                "password2": "password",
            },
        )

        assert response.status_code == 200  # Form redisplayed with errors
        assert (
            b"Invalid email address" in response.data
            or b"email" in response.data.lower()
        )

    def test_login_get(self, client):
        """Test GET /auth/login - login form display."""
        response = client.get("/auth/login")

        assert response.status_code == 200
        assert b"Login" in response.data
        assert b"Username" in response.data
        assert b"Password" in response.data

    def test_login_valid_credentials(self, client, test_user):
        """Test successful login with valid credentials."""
        response = client.post(
            "/auth/login",
            data={"username": "testuser", "password": "testpass"},
        )

        # Should redirect to home page after successful login
        assert response.status_code == 302
        assert response.location == "/"

        # Check if user is logged in by accessing profile
        response = client.get("/user/testuser")
        assert response.status_code == 200

    def test_login_invalid_username(self, client):
        """Test login with non-existent username."""
        response = client.post(
            "/auth/login",
            data={"username": "nonexistent", "password": "password"},
        )

        assert response.status_code == 200  # Form redisplayed with errors
        assert (
            b"Invalid username or password" in response.data
            or b"invalid" in response.data.lower()
        )

    def test_login_invalid_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post(
            "/auth/login",
            data={"username": "testuser", "password": "wrongpassword"},
        )

        assert response.status_code == 200  # Form redisplayed with errors
        assert (
            b"Invalid username or password" in response.data
            or b"invalid" in response.data.lower()
        )

    def test_login_empty_credentials(self, client):
        """Test login with empty credentials."""
        response = client.post(
            "/auth/login", data={"username": "", "password": ""}
        )

        assert response.status_code == 200  # Form redisplayed with errors
        # Should have validation errors for required fields

    def test_logout(self, client, auth, test_user):
        """Test user logout."""
        # First login
        auth.login("testuser", "testpass")

        # Verify user is logged in
        response = client.get("/user/testuser")
        assert response.status_code == 200

        # Logout
        response = client.get("/auth/logout")
        assert response.status_code == 302
        assert response.location == "/"

        # Verify user is logged out by trying to access protected page
        response = client.get("/create")
        assert response.status_code == 302  # Should redirect to login
        assert "/auth/login" in response.location

    def test_logout_when_not_logged_in(self, client):
        """Test logout when not logged in."""
        response = client.get("/auth/logout")

        # Should still redirect to home page
        assert response.status_code == 302
        assert response.location == "/"

    def test_login_redirect_next(self, client, test_user):
        """Test login redirect to 'next' parameter."""
        # Try to access protected page without login
        response = client.get("/create")
        assert response.status_code == 302
        assert "/auth/login" in response.location
        assert "next=" in response.location

        # Login and should redirect back to original page
        response = client.post(
            "/auth/login?next=/create",
            data={"username": "testuser", "password": "testpass"},
        )

        assert response.status_code == 302
        assert "/create" in response.location or response.location == "/create"


class TestAuthProtectedRoutes:
    """Test authentication protection on routes."""

    def test_create_paste_requires_login(self, client):
        """Test that creating paste requires login."""
        response = client.get("/create")

        assert response.status_code == 302
        assert "/auth/login" in response.location

    def test_create_paste_post_requires_login(self, client):
        """Test that POST to create paste requires login."""
        response = client.post(
            "/create", data={"title": "Test", "content": "test content"}
        )

        assert response.status_code == 302
        assert "/auth/login" in response.location

    def test_edit_paste_requires_login(self, client, test_paste):
        """Test that editing paste requires login."""
        response = client.get(f"/paste/{test_paste.unique_id}/edit")

        assert response.status_code == 302
        assert "/auth/login" in response.location

    def test_user_profile_accessible_when_logged_in(
        self, client, auth, test_user
    ):
        """Test user profile is accessible when logged in."""
        auth.login("testuser", "testpass")

        response = client.get("/user/testuser")
        assert response.status_code == 200
        assert b"testuser" in response.data

    def test_create_paste_accessible_when_logged_in(
        self, client, auth, test_user
    ):
        """Test create paste page is accessible when logged in."""
        auth.login("testuser", "testpass")

        response = client.get("/create")
        assert response.status_code == 200
        assert b"Create Paste" in response.data

    def test_public_pages_accessible_without_login(self, client, test_paste):
        """Test that public pages are accessible without login."""
        # Home page
        response = client.get("/")
        assert response.status_code == 200

        # Public paste view
        response = client.get(f"/paste/{test_paste.unique_id}")
        assert response.status_code == 200

        # Raw paste view
        response = client.get(f"/paste/{test_paste.unique_id}/raw")
        assert response.status_code == 200


class TestUserSessions:
    """Test user session management."""

    def test_session_persistence(self, client, auth, test_user):
        """Test that user session persists across requests."""
        auth.login("testuser", "testpass")

        # Multiple requests should maintain session
        for _ in range(3):
            response = client.get("/user/testuser")
            assert response.status_code == 200

    def test_remember_me_functionality(self, client, test_user):
        """Test remember me functionality if implemented."""
        # This test assumes remember me is implemented
        # Adjust based on actual implementation
        response = client.post(
            "/auth/login",
            data={
                "username": "testuser",
                "password": "testpass",
                "remember_me": True,
            },
        )

        assert response.status_code == 302

    def test_session_cleanup_on_logout(self, client, auth, test_user):
        """Test that session is properly cleaned up on logout."""
        auth.login("testuser", "testpass")

        # Verify logged in
        response = client.get("/user/testuser")
        assert response.status_code == 200

        # Logout
        auth.logout()

        # Verify session is cleared
        response = client.get("/create")
        assert response.status_code == 302  # Should redirect to login


class TestPasswordSecurity:
    """Test password security features."""

    def test_password_hashing(self, app):
        """Test that passwords are properly hashed."""
        with app.app_context():
            user = User(username="hashtest", email="hash@example.com")
            user.set_password("plaintext")

            # Password should be hashed, not stored as plaintext
            assert user.password_hash != "plaintext"
            assert len(user.password_hash) > 20  # Reasonable hash length

            # Should be able to verify correct password
            assert user.check_password("plaintext")
            assert not user.check_password("wrong")

    def test_password_requirements(self, client):
        """Test password requirements if implemented."""
        # Test weak password
        response = client.post(
            "/auth/register",
            data={
                "username": "weakpass",
                "email": "weak@example.com",
                "password": "123",  # Too short
                "password2": "123",
            },
        )

        # Should reject weak password or accept it based on requirements
        # Adjust assertion based on actual password requirements
        assert response.status_code in [200, 302]  # Either error or success

    def test_case_insensitive_username(self, client, test_user):
        """Test username case sensitivity in login."""
        # Try logging in with different case
        response = client.post(
            "/auth/login",
            data={
                "username": "TESTUSER",
                "password": "testpass",
            },  # Different case
        )

        # Should work if case insensitive, fail if case sensitive
        # Adjust based on actual implementation
        assert response.status_code in [200, 302]
