#!/usr/bin/env python3
"""Installation script for Telegram Contact Importer."""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python 3.7+ required. You have {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor} detected")
    return True


def install_requirements():
    """Install required packages."""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    command = f"{sys.executable} -m pip install -r requirements.txt"
    return run_command(command, "Installing requirements")


def create_directories():
    """Create necessary directories."""
    directories = [
        "logs",
        "sessions", 
        "exports"
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(exist_ok=True)
            print(f"📁 Created directory: {directory}")
    
    return True


def check_config():
    """Check configuration file."""
    config_file = Path("config.yaml")
    if config_file.exists():
        print("✅ Configuration file found")
        return True
    else:
        print("⚠️ Configuration file not found, will use defaults")
        return True


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("1. Get Telegram API credentials:")
    print("   - Visit: https://my.telegram.org/apps")
    print("   - Create a new application")
    print("   - Note your api_id and api_hash")
    print()
    print("2. Run the application:")
    print("   python main.py")
    print()
    print("3. Follow the interactive setup to:")
    print("   - Enter your API credentials")
    print("   - Authenticate with your phone number")
    print("   - Import your contacts")
    print()
    print("📄 Sample data file is located at: src/data/HGCS12.txt")
    print("📖 For more information, see README.md")
    print()


def main():
    """Main setup function."""
    print("🚀 Telegram Contact Importer Setup")
    print("="*40)
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Failed to install requirements")
        print("Please run manually: pip install -r requirements.txt")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check config
    check_config()
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()