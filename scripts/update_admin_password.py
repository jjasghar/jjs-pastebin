#!/usr/bin/env python3
"""
Update Admin Password Script

This script updates the admin user's password in the database.
Can be run via Docker Compose or standalone Docker container.

Usage:
    python scripts/update_admin_password.py [new_password]

If no password is provided, you'll be prompted to enter one securely.
"""

import os
import sys
from getpass import getpass

# Add the parent directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User


def update_admin_password(new_password=None):
    """Update the admin user's password."""

    # Create Flask app context
    app = create_app()

    with app.app_context():
        # Find the admin user
        admin_user = User.query.filter_by(username="admin").first()

        if not admin_user:
            print("❌ Admin user not found!")
            print("Make sure the application has been deployed and admin user created.")
            return False

        # Get new password if not provided
        if not new_password:
            print("Enter new password for admin user:")
            new_password = getpass("New password: ")
            confirm_password = getpass("Confirm password: ")

            if new_password != confirm_password:
                print("❌ Passwords don't match!")
                return False

        if len(new_password) < 6:
            print("❌ Password must be at least 6 characters long!")
            return False

        # Update the password
        try:
            admin_user.set_password(new_password)
            db.session.commit()

            print("✅ Admin password updated successfully!")
            print(f"Username: {admin_user.username}")
            print("Please use the new password to login.")
            return True

        except Exception as e:
            print(f"❌ Error updating password: {e}")
            db.session.rollback()
            return False


def main():
    """Main function."""
    print("🔐 JJ Pastebin - Admin Password Update Tool")
    print("=" * 50)

    # Check if password provided as argument
    new_password = None
    if len(sys.argv) > 1:
        new_password = sys.argv[1]

    success = update_admin_password(new_password)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
