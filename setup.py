from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jj-pastebin",
    version="1.0.0",
    author="JJ",
    author_email="jj@example.com",
    description="A modern pastebin application with CLI tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jjasghar/jjs-pastebin",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Flask>=2.3.3",
        "Flask-SQLAlchemy>=3.0.5",
        "Flask-Login>=0.6.3",
        "Flask-WTF>=1.1.1",
        "WTForms>=3.0.1",
        "Flask-Migrate>=4.0.5",
        "psycopg2-binary>=2.9.7",
        "click>=8.1.7",
        "python-dotenv>=1.0.0",
        "bcrypt>=4.0.1",
        "requests>=2.31.0",
        "Pygments>=2.16.1",
        "bleach>=6.0.0",
        "gunicorn>=21.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "pre-commit>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "jj=cli.jj:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
