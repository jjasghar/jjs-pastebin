#!/usr/bin/env python3
"""
JJ Pastebin CLI Tool

Usage:
    jj paste <file>          - Upload a file
    jj paste -                - Upload from stdin
    jj login                  - Login and save credentials
    jj logout                 - Logout and remove credentials
    jj list                   - List your pastes
    jj view <paste_id>        - View a paste
    jj delete <paste_id>      - Delete a paste
    jj version                - Show version information
"""

import json
import sys
from pathlib import Path

import click
import requests

# Version information
try:
    from . import __version__
except ImportError:
    __version__ = "1.0.0"

# Configuration
CONFIG_DIR = Path.home() / ".jj"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_API_URL = "http://localhost:5000/api"


class JJConfig:
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        self.config = {}
        self.load_config()

    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
            except Exception:
                self.config = {}

    def save_config(self):
        """Save configuration to file"""
        self.config_dir.mkdir(exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def get_api_url(self):
        return self.config.get("api_url", DEFAULT_API_URL)

    def get_token(self):
        return self.config.get("token")

    def set_token(self, token):
        self.config["token"] = token
        self.save_config()

    def set_api_url(self, url):
        self.config["api_url"] = url
        self.save_config()

    def clear_auth(self):
        self.config.pop("token", None)
        self.save_config()


config = JJConfig()


def get_headers():
    """Get headers with authentication if available"""
    headers = {"Content-Type": "application/json"}
    token = config.get_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def detect_language(filename):
    """Detect programming language from file extension"""
    if not filename or filename == "-":
        return "text"

    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".xml": "xml",
        ".sql": "sql",
        ".sh": "bash",
        ".bash": "bash",
        ".c": "c",
        ".cpp": "cpp",
        ".java": "java",
        ".php": "php",
        ".rb": "ruby",
        ".go": "go",
        ".rs": "rust",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".md": "markdown",
        ".dockerfile": "dockerfile",
    }

    ext = Path(filename).suffix.lower()
    return ext_map.get(ext, "text")


@click.group()
@click.option("--api-url", help="API URL for the pastebin service")
def cli(api_url):
    """JJ Pastebin CLI - Upload and manage code snippets"""
    if api_url:
        config.set_api_url(api_url)


@cli.command()
@click.argument("file", type=click.File("r"), default="-")
@click.option("--title", "-t", help="Title for the paste")
@click.option("--language", "-l", help="Programming language")
@click.option("--private", "-p", is_flag=True, help="Make paste private")
@click.option("--api-url", help="API URL for the pastebin service")
def paste(file, title, language, private, api_url):
    """Upload a file or stdin to pastebin"""
    if api_url:
        config.set_api_url(api_url)

    # Read content
    try:
        content = file.read()
        if not content.strip():
            click.echo("Error: No content to paste", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error reading file: {e}", err=True)
        sys.exit(1)

    # Determine title and language
    filename = file.name if file.name != "<stdin>" else None
    if not title:
        title = Path(filename).name if filename else "Untitled"

    if not language:
        language = detect_language(filename)

    # Prepare data
    data = {
        "title": title,
        "content": content,
        "language": language,
        "is_public": not private,
    }

    # Make request
    try:
        response = requests.post(
            f"{config.get_api_url()}/pastes", json=data, headers=get_headers()
        )

        if response.status_code == 201:
            paste_data = response.json()
            paste_url = f"{config.get_api_url().replace('/api', '')}/paste/{paste_data['unique_id']}"
            click.echo("Paste created successfully!")
            click.echo(f"URL: {paste_url}")
            click.echo(f"ID: {paste_data['unique_id']}")
        else:
            click.echo(
                f"Error: {response.json().get('error', 'Unknown error')}",
                err=True,
            )
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to API: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--username", "-u", prompt=True, help="Username")
@click.option("--password", "-p", prompt=True, hide_input=True, help="Password")
def login(username, password):
    """Login and save credentials"""
    data = {"username": username, "password": password}

    try:
        response = requests.post(
            f"{config.get_api_url()}/auth/login",
            json=data,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            result = response.json()
            config.set_token(result["token"])
            click.echo(f"Logged in successfully as {result['user']['username']}")
        else:
            click.echo(
                f"Login failed: {response.json().get('error', 'Unknown error')}",
                err=True,
            )
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to API: {e}", err=True)
        sys.exit(1)


@cli.command()
def logout():
    """Logout and remove saved credentials"""
    config.clear_auth()
    click.echo("Logged out successfully")


@cli.command()
@click.option("--page", "-p", default=1, help="Page number")
def list(page):
    """List your pastes"""
    if not config.get_token():
        click.echo("Error: Please login first (jj login)", err=True)
        sys.exit(1)

    try:
        response = requests.get(
            f"{config.get_api_url()}/users/me/pastes?page={page}",
            headers=get_headers(),
        )

        if response.status_code == 200:
            data = response.json()
            pastes = data["pastes"]

            if not pastes:
                click.echo("No pastes found")
                return

            click.echo(f"Your pastes (Page {data['current_page']} of {data['pages']}):")
            click.echo("-" * 60)

            for paste in pastes:
                status = "Public" if paste["is_public"] else "Private"
                click.echo(f"ID: {paste['unique_id']}")
                click.echo(f"Title: {paste['title']}")
                click.echo(f"Language: {paste['language']}")
                click.echo(f"Status: {status}")
                click.echo(f"Views: {paste['views']}")
                click.echo(f"Created: {paste['created_at']}")
                click.echo("-" * 60)
        else:
            click.echo(
                f"Error: {response.json().get('error', 'Unknown error')}",
                err=True,
            )
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to API: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("paste_id")
def view(paste_id):
    """View a paste"""
    try:
        response = requests.get(
            f"{config.get_api_url()}/pastes/{paste_id}", headers=get_headers()
        )

        if response.status_code == 200:
            paste = response.json()
            click.echo(f"Title: {paste['title']}")
            click.echo(f"Language: {paste['language']}")
            click.echo(f"Author: {paste['author']}")
            click.echo(f"Created: {paste['created_at']}")
            click.echo(f"Views: {paste['views']}")
            click.echo("-" * 60)
            click.echo(paste["content"])
        else:
            click.echo(
                f"Error: {response.json().get('error', 'Unknown error')}",
                err=True,
            )
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to API: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("paste_id")
@click.confirmation_option(prompt="Are you sure you want to delete this paste?")
def delete(paste_id):
    """Delete a paste"""
    if not config.get_token():
        click.echo("Error: Please login first (jj login)", err=True)
        sys.exit(1)

    try:
        response = requests.delete(
            f"{config.get_api_url()}/pastes/{paste_id}", headers=get_headers()
        )

        if response.status_code == 200:
            click.echo("Paste deleted successfully")
        else:
            click.echo(
                f"Error: {response.json().get('error', 'Unknown error')}",
                err=True,
            )
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        click.echo(f"Error connecting to API: {e}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Show version information"""
    click.echo(f"JJ Pastebin CLI Version: {__version__}")


if __name__ == "__main__":
    cli()
