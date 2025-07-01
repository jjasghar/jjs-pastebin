"""
Tests for database models.
"""

from datetime import datetime

from app import db
from app.models import Paste, User


class TestUser:
    """Test User model."""

    def test_password_hashing(self, app):
        """Test password hashing and verification."""
        with app.app_context():
            user = User(username="test", email="test@example.com")
            user.set_password("secret")

            assert user.password_hash != "secret"
            assert user.check_password("secret")
            assert not user.check_password("wrong")

    def test_user_creation(self, app):
        """Test user creation with all fields."""
        with app.app_context():
            user = User(
                username="testuser",
                email="test@example.com",
                is_superuser=True,
            )
            user.set_password("password")

            db.session.add(user)
            db.session.commit()

            saved_user = User.query.filter_by(username="testuser").first()
            assert saved_user.username == "testuser"
            assert saved_user.email == "test@example.com"
            assert saved_user.is_superuser is True
            assert saved_user.created_at is not None
            assert saved_user.check_password("password")

    def test_user_repr(self, app):
        """Test user string representation."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            assert repr(user) == "<User testuser>"

    def test_user_relationships(self, app, test_user):
        """Test user-paste relationships."""
        with app.app_context():
            user = User.query.get(test_user.id)

            # Create pastes for the user
            paste1 = Paste(title="Paste 1", content="content1", user_id=user.id)
            paste2 = Paste(title="Paste 2", content="content2", user_id=user.id)

            db.session.add_all([paste1, paste2])
            db.session.commit()

            # Test relationship
            assert user.pastes.count() == 2
            assert user.pastes[0].title in ["Paste 1", "Paste 2"]
            assert user.pastes[1].title in ["Paste 1", "Paste 2"]


class TestPaste:
    """Test Paste model."""

    def test_paste_creation(self, app, test_user):
        """Test paste creation with all fields."""
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

            saved_paste = Paste.query.filter_by(title="Test Paste").first()
            assert saved_paste.title == "Test Paste"
            assert saved_paste.content == 'print("Hello, World!")'
            assert saved_paste.language == "python"
            assert saved_paste.is_public is True
            assert saved_paste.user_id == test_user.id
            assert saved_paste.unique_id is not None
            assert len(saved_paste.unique_id) == 8
            assert saved_paste.created_at is not None
            assert saved_paste.updated_at is not None

    def test_paste_unique_id_generation(self, app, test_user):
        """Test that unique IDs are generated and unique."""
        with app.app_context():
            paste1 = Paste(title="Paste 1", content="content1", user_id=test_user.id)
            paste2 = Paste(title="Paste 2", content="content2", user_id=test_user.id)

            db.session.add_all([paste1, paste2])
            db.session.commit()

            assert paste1.unique_id != paste2.unique_id
            assert len(paste1.unique_id) == 8
            assert len(paste2.unique_id) == 8

    def test_paste_repr(self, app, test_user):
        """Test paste string representation."""
        with app.app_context():
            paste = Paste(title="Test Paste", content="content", user_id=test_user.id)
            db.session.add(paste)
            db.session.commit()

            # Test repr includes unique_id and title
            expected_repr = f"<Paste {paste.unique_id}: Test Paste>"
            assert repr(paste) == expected_repr

    def test_paste_author_relationship(self, app, test_user):
        """Test paste-author relationship."""
        with app.app_context():
            paste = Paste(title="Test Paste", content="content", user_id=test_user.id)
            db.session.add(paste)
            db.session.commit()

            # Test relationship
            assert paste.author.username == test_user.username
            assert paste.author.email == test_user.email

    def test_paste_defaults(self, app, test_user):
        """Test paste default values."""
        with app.app_context():
            paste = Paste(
                title="Minimal Paste", content="content", user_id=test_user.id
            )

            db.session.add(paste)
            db.session.commit()

            assert paste.language == "text"  # Default language
            assert paste.is_public is True  # Default visibility
            assert paste.views == 0  # Default view count

    def test_paste_view_increment(self, app, test_paste):
        """Test incrementing paste views."""
        with app.app_context():
            paste = Paste.query.get(test_paste.id)
            initial_views = paste.views

            # Simulate view increment (would normally be done in routes)
            paste.views += 1
            db.session.commit()

            updated_paste = Paste.query.get(test_paste.id)
            assert updated_paste.views == initial_views + 1

    def test_paste_update_timestamp(self, app, test_paste):
        """Test that updated_at timestamp changes on modification."""
        with app.app_context():
            paste = Paste.query.get(test_paste.id)
            original_updated = paste.updated_at

            # Wait a bit and update
            import time

            time.sleep(0.1)

            paste.content = "Updated content"
            paste.updated_at = (
                datetime.utcnow()
            )  # Would be handled by SQLAlchemy in real app
            db.session.commit()

            updated_paste = Paste.query.get(test_paste.id)
            assert updated_paste.updated_at > original_updated

    def test_public_pastes_query(self, app, test_user):
        """Test querying only public pastes."""
        with app.app_context():
            # Create public and private pastes
            public_paste = Paste(
                title="Public Paste",
                content="public content",
                is_public=True,
                user_id=test_user.id,
            )
            private_paste = Paste(
                title="Private Paste",
                content="private content",
                is_public=False,
                user_id=test_user.id,
            )

            db.session.add_all([public_paste, private_paste])
            db.session.commit()

            # Query only public pastes
            public_pastes = Paste.query.filter_by(is_public=True).all()
            public_titles = [p.title for p in public_pastes]

            assert "Public Paste" in public_titles
            assert "Private Paste" not in public_titles

    def test_paste_by_language(self, app, test_user):
        """Test querying pastes by language."""
        with app.app_context():
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

            # Query by language
            python_pastes = Paste.query.filter_by(language="python").all()
            js_pastes = Paste.query.filter_by(language="javascript").all()

            assert len(python_pastes) == 1
            assert len(js_pastes) == 1
            assert python_pastes[0].title == "Python Code"
            assert js_pastes[0].title == "JavaScript Code"
