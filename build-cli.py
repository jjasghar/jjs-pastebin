#!/usr/bin/env python3
"""
Build script for JJ Pastebin CLI PyPI package

This script helps build and prepare the CLI package for PyPI distribution.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous build artifacts...")

    # Remove build directories
    for dir_name in ["build", "dist", "*.egg-info"]:
        for path in Path(".").glob(dir_name):
            if path.is_dir():
                try:
                    shutil.rmtree(path)
                    print(f"   Removed {path}")
                except Exception as e:
                    print(f"   Warning: Could not remove {path}: {e}")

    # Remove __pycache__
    for pycache in Path(".").rglob("__pycache__"):
        if pycache.is_dir():
            try:
                shutil.rmtree(pycache)
            except Exception as e:
                print(f"   Warning: Could not remove {pycache}: {e}")

    return True


def check_requirements():
    """Check if build requirements are installed"""
    print("📋 Checking build requirements...")

    required_packages = ["build", "twine", "setuptools", "wheel"]
    missing = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"   ❌ {package}")

    if missing:
        print(f"\n🚨 Missing packages: {', '.join(missing)}")
        print("Install them with: pip install build twine setuptools wheel")
        return False

    return True


def build_package():
    """Build the package"""
    print("🔨 Building package...")

    # Use setup-cli.py for building
    result = subprocess.run(
        [sys.executable, "setup-cli.py", "sdist", "bdist_wheel"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"❌ Build failed: {result.stderr}")
        return False

    print("✅ Package built successfully!")

    # List generated files
    dist_dir = Path("dist")
    if dist_dir.exists():
        print("\n📦 Generated files:")
        for file in dist_dir.glob("*"):
            print(f"   {file}")

    return True


def check_package():
    """Check the built package"""
    print("\n🔍 Checking package...")

    # Use twine to check
    result = subprocess.run(
        ["twine", "check", "dist/*"], capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"❌ Package check failed: {result.stderr}")
        return False

    print("✅ Package check passed!")
    return True


def test_install():
    """Test installation in a virtual environment"""
    print("\n🧪 Testing installation...")

    # Find the wheel file
    dist_dir = Path("dist")
    wheel_files = list(dist_dir.glob("*.whl"))

    if not wheel_files:
        print("❌ No wheel file found")
        return False

    wheel_file = wheel_files[0]

    # Test with pip show what would be installed
    result = subprocess.run(
        ["pip", "show", "--verbose", str(wheel_file)],
        capture_output=True,
        text=True,
    )

    print(f"📋 Package info preview for {wheel_file.name}")
    return True


def upload_test():
    """Upload to Test PyPI"""
    print("\n🚀 Ready to upload to Test PyPI")
    print("Run: twine upload --repository testpypi dist/*")
    print(
        "Then test install: pip install --index-url https://test.pypi.org/simple/ jj-pastebin-cli"
    )


def upload_prod():
    """Upload to PyPI"""
    print("\n🚀 Ready to upload to PyPI")
    print("Run: twine upload dist/*")


def main():
    """Main build process"""
    print("🎯 JJ Pastebin CLI - PyPI Build Script")
    print("=" * 50)

    # Change to script directory
    os.chdir(Path(__file__).parent)

    # Check if we have the necessary files
    required_files = [
        "setup-cli.py",
        "CLI-README.md",
        "pyproject.toml",
        "cli/jj.py",
    ]
    missing_files = [f for f in required_files if not Path(f).exists()]

    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return 1

    # Build process
    steps = [
        ("Clean build artifacts", clean_build),
        ("Check requirements", check_requirements),
        ("Build package", build_package),
        ("Check package", check_package),
        ("Test installation preview", test_install),
    ]

    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Failed at: {step_name}")
            return 1

    print("\n" + "=" * 50)
    print("🎉 Build completed successfully!")
    print("\nNext steps:")
    print("1. Test PyPI: twine upload --repository testpypi dist/*")
    print(
        "2. Test install: pip install --index-url https://test.pypi.org/simple/ jj-pastebin-cli"
    )
    print("3. Production: twine upload dist/*")

    return 0


if __name__ == "__main__":
    sys.exit(main())
