# JJ Pastebin Tests

This directory contains comprehensive tests for the JJ Pastebin application.

## Test Structure

```
tests/
├── conftest.py         # pytest configuration and fixtures
├── test_models.py      # Database model tests
├── test_api.py         # API endpoint tests
├── test_auth.py        # Authentication system tests
├── test_web.py         # Web interface tests
├── test_cli.py         # CLI tool tests
└── README.md          # This file
```

## Test Categories

### Unit Tests
- **Models** (`test_models.py`): Tests for User and Paste models
- **Authentication** (`test_auth.py`): Login, registration, and session management
- **CLI** (`test_cli.py`): Command-line interface functionality

### Integration Tests
- **API** (`test_api.py`): REST API endpoints and authentication
- **Web** (`test_web.py`): Web routes, templates, and user interactions

### Test Markers
Tests are organized using pytest markers:
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.api` - API-specific tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.web` - Web interface tests
- `@pytest.mark.cli` - CLI tool tests
- `@pytest.mark.models` - Model tests
- `@pytest.mark.slow` - Slow-running tests

## Running Tests

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov=cli --cov-report=html
```

### Using the Test Runner Script
```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type api

# Run with coverage
python run_tests.py --coverage

# Run linting
python run_tests.py --lint

# Run security checks
python run_tests.py --security

# Install dependencies and run all checks
python run_tests.py --install-deps --coverage --lint --security
```

### Specific Test Commands
```bash
# Run only unit tests (exclude integration)
pytest -m "not integration"

# Run only integration tests
pytest -m "integration"

# Run specific test file
pytest tests/test_models.py

# Run specific test class
pytest tests/test_api.py::TestAPIPastes

# Run specific test method
pytest tests/test_auth.py::TestAuth::test_login_valid_credentials

# Run with verbose output
pytest -v

# Run with very verbose output
pytest -vv
```

## Test Configuration

### pytest.ini
The `pytest.ini` file in the project root contains:
- Test discovery settings
- Marker definitions
- Warning filters
- Default command-line options

### Environment Variables
Tests use the following environment variables:
- `FLASK_ENV=testing` - Sets Flask to testing mode
- `DATABASE_URL` - Database connection string (defaults to in-memory SQLite)
- `TESTING=true` - Enables testing mode

### Fixtures
Common fixtures are defined in `conftest.py`:
- `app` - Flask application instance
- `client` - Test client for HTTP requests
- `auth` - Authentication helper
- `test_user` - Test user account
- `admin_user` - Admin user account
- `test_paste` - Public test paste
- `private_paste` - Private test paste
- `api_headers` - Standard API headers
- `sample_code` - Code samples for testing

## Continuous Integration

Tests run automatically on GitHub Actions for:
- **Push/PR Events**: All tests on Python 3.8-3.12
- **Code Quality**: Linting with flake8, black, isort
- **Security**: Bandit and safety checks
- **Integration**: PostgreSQL database tests
- **Docker**: Container build and functionality tests

### GitHub Actions Workflow
The workflow includes:
1. **Test Matrix**: Python 3.8, 3.9, 3.10, 3.11, 3.12
2. **Linting**: Code style and quality checks
3. **Security**: Vulnerability scanning
4. **Integration**: Database and CLI tests
5. **Docker**: Container deployment tests

## Coverage Reports

### Local Coverage
```bash
# Generate HTML coverage report
pytest --cov=app --cov=cli --cov-report=html

# View report
open htmlcov/index.html
```

### CI Coverage
Coverage reports are automatically uploaded to Codecov when tests run in CI.

## Writing Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test
```python
def test_create_paste(self, client, auth, test_user):
    \"\"\"Test creating a new paste.\"\"\"
    auth.login('testuser', 'testpass')
    
    response = client.post('/create', data={
        'title': 'Test Paste',
        'content': 'print("hello")',
        'language': 'python'
    })
    
    assert response.status_code == 302
    # Add more assertions...
```

### Testing Guidelines
1. **Isolation**: Each test should be independent
2. **Descriptive Names**: Test names should clearly describe what they test
3. **Arrange-Act-Assert**: Structure tests with clear setup, action, and verification
4. **Use Fixtures**: Leverage pytest fixtures for common setup
5. **Mock External Dependencies**: Use mocks for external services
6. **Test Edge Cases**: Include tests for error conditions and edge cases

## Debugging Tests

### Running Specific Tests
```bash
# Run failing test with full output
pytest tests/test_api.py::TestAPIPastes::test_create_paste -vvs

# Run with pdb debugger
pytest tests/test_models.py::TestUser::test_password_hashing --pdb

# Run with print statements visible
pytest tests/test_auth.py -s
```

### Test Database
Tests use an in-memory SQLite database by default. For debugging:
```python
# In conftest.py, change to file-based database
'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'
```

## Performance Testing

### Slow Tests
Mark slow tests with `@pytest.mark.slow`:
```python
@pytest.mark.slow
def test_large_paste_upload(self, client, auth):
    # Test with large data...
```

### Skip Slow Tests
```bash
# Skip slow tests
pytest -m "not slow"
```

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies are installed
2. **Database Errors**: Check database permissions and connection strings
3. **Port Conflicts**: Ensure test ports are available
4. **Fixture Errors**: Check fixture dependencies and scopes

### Debug Mode
```bash
# Run with maximum verbosity
pytest -vvs --tb=long

# Show local variables in tracebacks
pytest --tb=auto --showlocals
``` 