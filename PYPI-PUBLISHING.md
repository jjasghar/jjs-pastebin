# Publishing JJ Pastebin CLI to PyPI

This guide explains how to publish the JJ Pastebin CLI tool to PyPI.

## 📋 Prerequisites

1. **PyPI Account**: Create accounts on both [Test PyPI](https://test.pypi.org/) and [PyPI](https://pypi.org/)
2. **API Tokens**: Generate API tokens for both services
3. **Build Tools**: Install required build tools

```bash
pip install build twine setuptools wheel
```

## 🏗️ Build Process

### 1. Clean Previous Builds
```bash
rm -rf build dist *.egg-info
```

### 2. Build the Package
```bash
python setup-cli.py sdist bdist_wheel
```

### 3. Check the Package
```bash
twine check dist/*
```

## 🧪 Test on Test PyPI

### 1. Upload to Test PyPI
```bash
twine upload --repository testpypi dist/*
```

### 2. Test Installation
```bash
# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ jj-pastebin-cli

# Test the CLI
jj --help
jj version
```

### 3. Test Functionality
```bash
# Test basic commands
echo "print('Hello, World!')" | jj paste -
```

## 🚀 Publish to PyPI

### 1. Upload to PyPI
```bash
twine upload dist/*
```

### 2. Verify Installation
```bash
pip install jj-pastebin-cli
jj --help
```

## 📦 Package Structure

The CLI package includes:

```
cli/
├── __init__.py          # Version and package info
└── jj.py               # Main CLI implementation

setup-cli.py             # Setup script for CLI only
CLI-README.md           # PyPI description
pyproject.toml          # Modern packaging config
MANIFEST.in             # File inclusion rules
requirements-cli.txt    # Minimal CLI dependencies
```

## 🔧 Configuration Files

### setup-cli.py
- Minimal setup focusing only on CLI
- Excludes Flask application dependencies
- Includes only `click` and `requests`

### pyproject.toml
- Modern Python packaging standards
- Proper metadata and dependencies
- Build system configuration

### MANIFEST.in
- Includes only necessary files
- Excludes Flask app, tests, docs
- Clean distribution package

## 📋 Checklist

Before publishing:

- [ ] Update version in `cli/__init__.py`
- [ ] Update version in `setup-cli.py` 
- [ ] Update version in `pyproject.toml`
- [ ] Test build process: `python setup-cli.py check`
- [ ] Test package: `twine check dist/*`
- [ ] Test on Test PyPI first
- [ ] Verify CLI functionality
- [ ] Update documentation if needed

## 🔄 Version Management

1. **Update Version**: Change version in all three places:
   - `cli/__init__.py`
   - `setup-cli.py`
   - `pyproject.toml`

2. **Build and Test**: Always test on Test PyPI first

3. **Tag Release**: Create git tag for the release
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

## 🛠️ Automated Build Script

Use the provided build script:

```bash
python build-cli.py
```

This script will:
- Clean previous builds
- Check requirements
- Build the package
- Validate the package
- Provide next steps

## 📞 Support

If you encounter issues:

1. Check the [PyPI documentation](https://packaging.python.org/)
2. Verify your API tokens are set correctly
3. Ensure all dependencies are properly specified
4. Test the package installation in a clean environment

## 🎯 Success Metrics

After publishing, verify:

- [ ] Package appears on PyPI: https://pypi.org/project/jj-pastebin-cli/
- [ ] Installation works: `pip install jj-pastebin-cli`
- [ ] CLI commands work: `jj --help`, `jj version`
- [ ] Dependencies are correctly resolved
- [ ] Package metadata is displayed correctly

---

**Note**: The CLI tool is designed to work independently of the Flask application, making it a standalone utility that can connect to any compatible pastebin API. 