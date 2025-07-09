#!/usr/bin/env python3
"""
Setup script for the Smart Product Traceability System.

This script provides commands to set up the development environment,
install dependencies, and run tests.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional

# Project metadata
PROJECT_NAME = "smart_traceability_system"
VERSION = "2.0.0"
AUTHOR = "Your Name"
AUTHOR_EMAIL = "your.email@example.com"
DESCRIPTION = "A smart, automated product labeling and traceability system"
URL = "https://github.com/yourusername/smart-traceability-system"

# Project directories
BASE_DIR = Path(__file__).parent.absolute()
SRC_DIR = BASE_DIR / "src"
TESTS_DIR = BASE_DIR / "tests"
DOCS_DIR = BASE_DIR / "docs"
DATA_DIR = BASE_DIR / "data"

# Required directories
REQUIRED_DIRS = [
    DATA_DIR / "models",
    DATA_DIR / "labels",
    DATA_DIR / "logs",
    DATA_DIR / "captures",
    DATA_DIR / "backups",
]

# Environment variables
ENV_FILE = ".env"
CONFIG_FILE = "config.json"


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {title.upper()}".center(60))
    print("=" * 60 + "\n")


def run_command(cmd: List[str], cwd: Optional[Path] = None) -> int:
    """Run a shell command and return the exit code."""
    print(f"Running: {' '.join(cmd)}")
    try:
        return subprocess.call(cmd, cwd=cwd or BASE_DIR)
    except KeyboardInterrupt:
        return 1


def check_python_version() -> bool:
    """Check if the Python version is supported."""
    import sys
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        return False
    return True


def create_virtualenv() -> bool:
    """Create a Python virtual environment."""
    venv_dir = BASE_DIR / "venv"
    if venv_dir.exists():
        print(f"Virtual environment already exists at {venv_dir}")
        return True

    print(f"Creating virtual environment at {venv_dir}...")
    if run_command([sys.executable, "-m", "venv", str(venv_dir)]) != 0:
        print("Failed to create virtual environment")
        return False
    return True


def install_dependencies() -> bool:
    """Install project dependencies."""
    print("Installing dependencies...")
    
    # Determine the correct pip command based on the platform
    pip_cmd = ["pip", "install", "--upgrade", "pip", "setuptools", "wheel"]
    if os.name == 'nt':  # Windows
        pip = BASE_DIR / "venv" / "Scripts" / "pip"
        pip_cmd = [str(pip)] + pip_cmd[1:]
    else:  # Unix/Linux/Mac
        pip_cmd = ["pip"] + pip_cmd[1:]
    
    # Upgrade pip, setuptools, and wheel
    if run_command(pip_cmd) != 0:
        print("Failed to upgrade pip/setuptools/wheel")
        return False
    
    # Install dependencies
    if run_command(pip_cmd[:-3] + ["-r", "requirements.txt"]) != 0:
        print("Failed to install dependencies")
        return False
    
    # Install development dependencies (if any)
    if (BASE_DIR / "requirements-dev.txt").exists():
        if run_command(pip_cmd[:-3] + ["-r", "requirements-dev.txt"]) != 0:
            print("Failed to install development dependencies")
            return False
    
    print("\nDependencies installed successfully!")
    return True


def create_directories() -> None:
    """Create required directories."""
    print("Creating required directories...")
    for directory in REQUIRED_DIRS:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  - Created: {directory.relative_to(BASE_DIR)}")


def create_env_file() -> None:
    """Create a .env file if it doesn't exist."""
    env_path = BASE_DIR / ENV_FILE
    if env_path.exists():
        print(f"{ENV_FILE} already exists")
        return
    
    env_content = """# Smart Product Traceability System - Environment Variables
# Copy this file to .env and update the values as needed

# System Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
DATA_DIR=./data

# Database Configuration
DATABASE_URL=sqlite:///./data/traceability.db

# Web Interface
HOST=0.0.0.0
PORT=5000
DEBUG=True
SECRET_KEY=your-secret-key-here

# Camera Configuration
CAMERA_INDEX=0
CAMERA_WIDTH=1920
CAMERA_HEIGHT=1080
CAMERA_FPS=30

# AI/ML Configuration
MODEL_PATH=./data/models/default_model.h5
CONFIDENCE_THRESHOLD=0.7

# Label Printer Configuration
PRINTER_TYPE=file  # file, network, serial, usb, cups, zpl
PRINTER_FILE_SAVE_PATH=./data/labels

# Email Notifications (optional)
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-email-password
EMAIL_FROM=noreply@example.com
EMAIL_TO=admin@example.com
"""
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"Created {ENV_FILE} - Please review and update the configuration")


def create_config_file() -> None:
    """Create a config file if it doesn't exist."""
    config_path = BASE_DIR / CONFIG_FILE
    if config_path.exists():
        print(f"{CONFIG_FILE} already exists")
        return
    
    # Copy the example config if it exists
    example_config = BASE_DIR / "config.example.json"
    if example_config.exists():
        shutil.copy(example_config, config_path)
        print(f"Created {CONFIG_FILE} from example configuration")
    else:
        print(f"Warning: {example_config} not found. Cannot create {CONFIG_FILE}")


def initialize_git() -> None:
    """Initialize a git repository if it doesn't exist."""
    git_dir = BASE_DIR / ".git"
    if git_dir.exists():
        print("Git repository already initialized")
        return
    
    print("Initializing git repository...")
    if run_command(["git", "init"]) == 0:
        # Create .gitignore if it doesn't exist
        gitignore = BASE_DIR / ".gitignore"
        if not gitignore.exists():
            with open(gitignore, 'w') as f:
                f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment variables
.env

# Database
*.db
*.sqlite3

# Data files
/data/*
!/data/.gitkeep

# Logs
*.log

# IDE
.vscode/
.idea/

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
""")
        print("Git repository initialized with .gitignore")
    else:
        print("Failed to initialize git repository")


def run_tests() -> int:
    """Run the test suite."""
    print_header("Running Tests")
    return run_command(["pytest", "tests/"])


def run_linter() -> int:
    """Run the linter."""
    print_header("Running Linter")
    return run_command(["flake8", "src/", "tests/"])


def run_type_checker() -> int:
    """Run the type checker."""
    print_header("Running Type Checker")
    return run_command(["mypy", "src/", "tests/"])


def format_code() -> int:
    """Format the code."""
    print_header("Formatting Code")
    return run_command(["black", "src/", "tests/", "setup.py"])


def sort_imports() -> int:
    """Sort imports."""
    print_header("Sorting Imports")
    return run_command(["isort", "src/", "tests/", "setup.py"])


def build_docs() -> int:
    """Build the documentation."""
    print_header("Building Documentation")
    return run_command(["sphinx-build", "-b", "html", "docs/source", "docs/build"])


def clean() -> None:
    """Clean build artifacts."""
    print_header("Cleaning")
    
    # Remove Python cache files
    for root, dirs, files in os.walk(BASE_DIR):
        for d in dirs:
            if d == "__pycache__":
                path = os.path.join(root, d)
                print(f"Removing {path}")
                shutil.rmtree(path, ignore_errors=True)
    
    # Remove build artifacts
    build_dirs = ["build", "dist", "*.egg-info", ".pytest_cache", ".mypy_cache"]
    for d in build_dirs:
        path = BASE_DIR / d
        if path.exists():
            print(f"Removing {path}")
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                path.unlink(missing_ok=True)
    
    # Remove Python compiled files
    for root, dirs, files in os.walk(BASE_DIR):
        for f in files:
            if f.endswith(('.pyc', '.pyo', '.pyd')):
                path = os.path.join(root, f)
                print(f"Removing {path}")
                os.unlink(path)
    
    print("\nClean complete!")


def show_help() -> None:
    """Show help message."""
    print("""
Smart Product Traceability System - Setup and Development Tools

Usage:
  python setup.py <command> [args...]

Commands:
  setup           Set up the development environment
  install         Install dependencies
  test            Run tests
  lint            Run linter
  typecheck       Run type checker
  format          Format code
  sort            Sort imports
  docs            Build documentation
  clean           Clean build artifacts
  help            Show this help message
""")


def main() -> int:
    """Main entry point."""
    if not check_python_version():
        return 1
    
    if len(sys.argv) < 2:
        show_help()
        return 1
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    if command == "setup":
        print_header("Setting Up Development Environment")
        create_virtualenv()
        install_dependencies()
        create_directories()
        create_env_file()
        create_config_file()
        initialize_git()
        print("\nSetup complete!")
        print("1. Review the .env and config.json files")
        print("2. Run 'python -m src.main' to start the application")
        return 0
    
    elif command == "install":
        return install_dependencies()
    
    elif command == "test":
        return run_tests()
    
    elif command == "lint":
        return run_linter()
    
    elif command == "typecheck":
        return run_type_checker()
    
    elif command == "format":
        return format_code()
    
    elif command == "sort":
        return sort_imports()
    
    elif command == "docs":
        return build_docs()
    
    elif command == "clean":
        clean()
        return 0
    
    elif command in ["help", "--help", "-h"]:
        show_help()
        return 0
    
    else:
        print(f"Error: Unknown command '{command}'", file=sys.stderr)
        show_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
