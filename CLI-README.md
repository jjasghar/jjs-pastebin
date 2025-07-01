# JJ Pastebin CLI

A modern, fast command-line client for uploading and managing code snippets with pastebin services. Features automatic language detection, private pastes, and a clean, intuitive interface.

## 🚀 Features

- **Fast uploads** - Upload files or stdin content instantly
- **Language detection** - Automatic syntax highlighting detection from file extensions
- **Private pastes** - Support for both public and private snippets
- **User management** - Login, list, view, and delete your pastes
- **Cross-platform** - Works on Windows, macOS, and Linux
- **Minimal dependencies** - Only requires `click` and `requests`
- **Multiple servers** - Configure custom pastebin API endpoints

## 📦 Installation

Install from PyPI:

```bash
pip install jj-pastebin-cli
```

Or install from source:

```bash
git clone https://github.com/jjasghar/jjs-pastebin.git
cd jjs-pastebin
pip install -e .
```

## 🔧 Quick Start

### Upload a file
```bash
jj paste myfile.py
```

### Upload with custom title and make private
```bash
jj paste myfile.py --title "My Script" --private
```

### Upload from stdin
```bash
echo "print('Hello, World!')" | jj paste -
```

### Login to manage your pastes
```bash
jj login
```

### List your pastes
```bash
jj list
```

### View a specific paste
```bash
jj view <paste_id>
```

### Delete a paste
```bash
jj delete <paste_id>
```

## 📋 Command Reference

### `jj paste [FILE]`
Upload a file or stdin content to pastebin.

**Options:**
- `--title, -t TEXT` - Custom title for the paste
- `--language, -l TEXT` - Force a specific programming language
- `--private, -p` - Make the paste private (requires login)
- `--api-url TEXT` - Use a custom API endpoint

**Examples:**
```bash
# Upload a Python file
jj paste script.py

# Upload with custom title
jj paste script.py --title "My Python Script"

# Upload as private paste
jj paste script.py --private

# Upload from stdin
cat myfile.js | jj paste -

# Force language detection
jj paste config.txt --language yaml
```

### `jj login`
Login and save credentials for managing pastes.

**Options:**
- `--username, -u TEXT` - Username (will prompt if not provided)
- `--password, -p TEXT` - Password (will prompt securely if not provided)

### `jj logout`
Remove saved credentials.

### `jj list`
List your uploaded pastes (requires login).

**Options:**
- `--page, -p INTEGER` - Page number for pagination

### `jj view <PASTE_ID>`
Display the content of a specific paste.

### `jj delete <PASTE_ID>`
Delete one of your pastes (requires login and confirmation).

## 🌐 Language Detection

The CLI automatically detects programming languages based on file extensions:

| Extension | Language |
|-----------|----------|
| `.py` | Python |
| `.js` | JavaScript |
| `.ts` | TypeScript |
| `.html` | HTML |
| `.css` | CSS |
| `.json` | JSON |
| `.xml` | XML |
| `.sql` | SQL |
| `.sh`, `.bash` | Bash |
| `.c` | C |
| `.cpp` | C++ |
| `.java` | Java |
| `.php` | PHP |
| `.rb` | Ruby |
| `.go` | Go |
| `.rs` | Rust |
| `.yml`, `.yaml` | YAML |
| `.md` | Markdown |

## ⚙️ Configuration

The CLI stores configuration in `~/.jj/config.json`:

```json
{
  "api_url": "https://your-pastebin.com/api",
  "token": "your-auth-token"
}
```

### Custom API Endpoint

You can use the CLI with any pastebin service that implements the compatible API:

```bash
# Set API URL for current command
jj paste myfile.py --api-url https://your-pastebin.com/api

# Set default API URL
jj --api-url https://your-pastebin.com/api login
```

## 🔧 Compatible Services

This CLI is designed to work with:
- [JJ Pastebin](https://github.com/jjasghar/jjs-pastebin) (reference implementation)
- Any pastebin service implementing the compatible REST API

### API Requirements

Your pastebin service should implement these endpoints:
- `POST /api/auth/login` - Authentication
- `POST /api/pastes` - Create paste
- `GET /api/pastes/{id}` - Get paste
- `GET /api/users/me/pastes` - List user pastes
- `DELETE /api/pastes/{id}` - Delete paste

## 🛠️ Development

### Running Tests
```bash
pip install -e ".[dev]"
pytest
```

### Code Formatting
```bash
black cli/
flake8 cli/
```

## 📄 License

Licensed under the Apache License 2.0. See [LICENSE](https://github.com/jjasghar/jjs-pastebin/blob/main/LICENSE) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

- **Documentation**: https://jjasghar.github.io/jjs-pastebin/cli-tools.html
- **Issues**: https://github.com/jjasghar/jjs-pastebin/issues
- **Source Code**: https://github.com/jjasghar/jjs-pastebin

---

**Note**: This CLI tool can work with any compatible pastebin service. The default configuration points to `localhost:5000` for development, but you can easily configure it to work with your deployed pastebin instance. 