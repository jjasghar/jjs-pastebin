#!/usr/bin/env python3
"""
JJ Pastebin - Main application runner
"""

import os

from app import create_app, db
from app.models import User


def deploy():
    """Run deployment tasks."""
    # Create database tables
    db.create_all()

    # Create a default superuser if none exists
    if not User.query.filter_by(is_superuser=True).first():
        admin = User(
            username="admin", email="admin@example.com", is_superuser=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Created default admin user:")
        print("Username: admin")
        print("Password: admin123")
        print("Please change this password after first login!")


# Create app instance for Gunicorn
app = create_app()

# Run deployment tasks when in production/Docker
if os.environ.get("FLASK_ENV") == "production":
    with app.app_context():
        deploy()

if __name__ == "__main__":
    # Run deployment if database doesn't exist (development mode)
    if not os.path.exists("instance/pastebin_dev.db"):
        with app.app_context():
            deploy()

    # Start the application in development mode
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
