# JJ Pastebin

A modern, feature-rich pastebin application with a web interface and CLI tool, similar to GitHub Gist. Built with Flask and designed for both development and production use.

## 📖 Documentation

**[Visit the full documentation site →](https://jjasghar.github.io/jjs-pastebin)**

The complete documentation includes:
- 🏠 **[Project Overview](https://jjasghar.github.io/jjs-pastebin)** - Features, installation, and quick start
- 🔌 **[API Documentation](https://jjasghar.github.io/jjs-pastebin/api-docs.html)** - Complete REST API reference
- 🛠️ **[CLI Tools & Vim Plugin](https://jjasghar.github.io/jjs-pastebin/cli-tools.html)** - Command-line tools and editor integration

## Features

### Web Interface
- 🎨 Modern UI inspired by GitHub Gist
- 🔍 Syntax highlighting for 20+ programming languages
- 👥 User authentication and profiles
- 🔒 Public and private pastes
- 📊 View tracking and statistics
- 📱 Responsive design for mobile and desktop
- ✏️ Edit and delete your pastes
- 🔗 Easy sharing with unique URLs

### CLI Tool
- 🚀 Fast command-line uploads
- 📁 Drag-and-drop file support
- 🔐 Secure authentication
- 📋 List and manage your pastes
- 🔍 View pastes from the terminal
- 🗑️ Delete pastes with confirmation

### API
- 🌐 Full REST API
- 🔑 Token-based authentication
- 📝 Complete CRUD operations
- 👑 Admin endpoints for user management
- 📊 Pagination support

### Database Support
- 🗄️ SQLite for development
- 🐘 PostgreSQL for production
- 🔄 Database migrations with Flask-Migrate

## Vim Plugin

JJ Pastebin includes a powerful Vim plugin that lets you paste code directly from your editor!

### Quick Setup

```bash
cd vim-plugin
./install.sh
```

### Usage

```vim
:JJ                    " Paste entire buffer
:JJ My Title           " Paste with custom title  
:5,10JJ                " Paste lines 5-10
:'<,'>JJ               " Paste visual selection
:JJPriv                " Create private paste
:JJConfig              " Show configuration
```

See the [vim-plugin/README.md](vim-plugin/README.md) for detailed documentation.

## Installation

### Prerequisites
- Python 3.8+
- pip
- (Optional) PostgreSQL for production

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jjasghar/jjs-pastebin.git
   cd jjs-pastebin
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install the CLI tool:**
   ```bash
   pip install -e .
   ```

4. **Run the application:**
   ```bash
   python run.py
   ```

5. **Visit the application:**
   Open your browser to `http://localhost:5000`
   
   **Note:** On macOS, port 5000 may conflict with AirPlay. If you encounter a "port in use" error, use:
   ```bash
   PORT=8000 python run.py
   ```
   Then visit `http://localhost:8000`

### Default Admin User
The application creates a default admin user:
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Important:** Change this password after first login!

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Basic Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Database Configuration
DATABASE_URL=sqlite:///pastebin_dev.db

# For production with PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/pastebin

# API Configuration
API_BASE_URL=http://localhost:5000

# Port Configuration (use 8000 on macOS if port 5000 conflicts with AirPlay)
PORT=5000
```

### Production Deployment

For production deployment with PostgreSQL:

1. **Set environment variables:**
   ```bash
   export FLASK_ENV=production
   export DATABASE_URL=postgresql://user:password@localhost/pastebin
   export SECRET_KEY=your-production-secret-key
   ```

2. **Run with Gunicorn:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

## Usage

### Web Interface

1. **Creating a paste:**
   - Visit the homepage
   - Click "New Paste"
   - Enter your code or text
   - Choose language and visibility
   - Click "Create Paste"

2. **Managing pastes:**
   - View your profile to see all your pastes
   - Edit pastes you own
   - Delete pastes with confirmation
   - Share paste URLs

### CLI Tool

1. **Login:**
   ```bash
   jj login
   ```

2. **Upload a file:**
   ```bash
   jj paste myfile.py
   ```

3. **Upload from stdin:**
   ```bash
   echo "print('Hello, World!')" | jj paste -
   ```

4. **List your pastes:**
   ```bash
   jj list
   ```

5. **View a paste:**
   ```bash
   jj view <paste_id>
   ```

6. **Delete a paste:**
   ```bash
   jj delete <paste_id>
   ```

### CLI Options

```bash
# Upload with custom title and language
jj paste myfile.py --title "My Script" --language python

# Upload as private paste
jj paste myfile.py --private

# Use different API URL
jj paste myfile.py --api-url https://your-pastebin.com/api
```

### REST API

#### Authentication
```bash
# Login to get token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

#### Create a paste
```bash
curl -X POST http://localhost:5000/api/pastes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "My Paste",
    "content": "print(\"Hello, World!\")",
    "language": "python",
    "is_public": true
  }'
```

#### Get a paste
```bash
curl http://localhost:5000/api/pastes/<paste_id>
```

#### List public pastes
```bash
curl http://localhost:5000/api/pastes?page=1&per_page=20
```

## Development

### Testing

JJ Pastebin includes comprehensive test coverage with pytest.

#### Quick Test Commands
```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov=cli --cov-report=html

# Run specific test types
pytest -m "api"          # API tests only
pytest -m "not integration"  # Unit tests only
```

#### Using the Test Runner
```bash
# Run all tests with coverage and linting
python run_tests.py --coverage --lint

# Run specific test categories
python run_tests.py --type api
python run_tests.py --type auth
python run_tests.py --type web
```

#### Continuous Integration
Tests run automatically on GitHub Actions:
- ✅ **Multi-Python Support**: Python 3.8-3.12
- ✅ **Code Quality**: Linting and formatting checks
- ✅ **Security Scanning**: Bandit and safety checks
- ✅ **Database Testing**: SQLite and PostgreSQL
- ✅ **Docker Testing**: Container functionality
- ✅ **Coverage Reports**: Automatic coverage tracking

See [tests/README.md](tests/README.md) for detailed testing documentation.

## API Documentation

### Authentication Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Paste Endpoints
- `GET /api/pastes` - List public pastes
- `POST /api/pastes` - Create a new paste
- `GET /api/pastes/<id>` - Get a specific paste
- `PUT /api/pastes/<id>` - Update a paste (authenticated)
- `DELETE /api/pastes/<id>` - Delete a paste (authenticated)
- `GET /api/pastes/<id>/raw` - Get raw paste content

### User Endpoints
- `GET /api/users/me` - Get current user info (authenticated)
- `GET /api/users/me/pastes` - Get current user's pastes (authenticated)
- `GET /api/users` - List all users (admin only)
- `DELETE /api/users/<id>` - Delete a user (admin only)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:
1. Check the **[Documentation Site](https://jjasghar.github.io/jjs-pastebin)** for comprehensive guides
2. Browse the [Issues](https://github.com/jjasghar/jjs-pastebin/issues) page for known issues
3. Create a new issue with detailed information
4. Include steps to reproduce any bugs

## Roadmap

- [ ] Paste expiration dates
- [ ] Paste folders/categories
- [ ] Collaborative editing
- [ ] Paste templates
- [ ] Advanced search functionality
- [ ] Dark mode theme
- [ ] Email notifications
- [ ] Paste statistics dashboard

---

Made with ❤️ by JJ 