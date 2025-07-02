#!/usr/bin/env python3
"""
Setup script for JJ Pastebin CLI Tool
"""

import os

from setuptools import setup


# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "CLI-README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return (
        "A command-line tool for uploading and managing code snippets "
        "with any pastebin-compatible service."
    )


# Read version from cli module
def read_version():
    try:
        import cli

        return getattr(cli, "__version__", "1.0.0")
    except Exception:
        return "1.0.0"


setup(
    name="jj-pastebin-cli",
    version="1.0.0",
    author="JJ Asghar",
    author_email="jj@jjasghar.io",
    description=(
        "A modern command-line pastebin client with support for "
        "syntax highlighting and private pastes"
    ),
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/jjasghar/jjs-pastebin",
    project_urls={
        "Bug Reports": "https://github.com/jjasghar/jjs-pastebin/issues",
        "Source": "https://github.com/jjasghar/jjs-pastebin",
        "Documentation": "https://jjasghar.github.io/jjs-pastebin/cli-tools.html",
    },
    packages=["cli"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    keywords="pastebin cli command-line code-sharing snippet upload",
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jj=cli.jj:cli",
            "jj-pastebin=cli.jj:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    platforms=["any"],
    license="Apache License 2.0",
)
