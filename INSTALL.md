# Installation Guide

## Table of Contents
- [Quick Install](#quick-install)
- [Linux Installation](#linux-installation)
- [Windows Installation](#windows-installation)
- [macOS Installation](#macos-installation)
- [Docker Installation](#docker-installation)
- [Development Installation](#development-installation)
- [Troubleshooting](#troubleshooting)

---

## Quick Install

### Using pip (Recommended for all platforms)

```bash
# Install from source
pip install .

# Or install in editable mode for development
pip install -e .
```

After installation, run:
```bash
telegram-contact-importer
```

---

## Linux Installation

### Method 1: System-wide Installation (Requires sudo)

```bash
# Using the automated installer
chmod +x install.sh
sudo ./install.sh

# Or manually
sudo pip install .
```

### Method 2: User Installation (Recommended - No sudo required)

```bash
# Install for current user only
pip install --user .

# Add to PATH if needed
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Run the application
telegram-contact-importer
```

### Method 3: Virtual Environment (Best for isolation)

```bash
# Create virtual environment
python3 -m venv ~/telegram-importer-env

# Activate it
source ~/telegram-importer-env/bin/activate

# Install
pip install .

# Run
telegram-contact-importer

# When done, deactivate
deactivate
```

### Method 4: Using the automated installer script

```bash
# Make the script executable
chmod +x install.sh

# Run the installer (creates venv automatically)
./install.sh

# Activate the environment
source venv/bin/activate

# Run the application
telegram-contact-importer
```

### Ubuntu/Debian Specific

```bash
# Install Python and pip if not present
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Install the application
pip3 install --user .

# Ensure ~/.local/bin is in PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Fedora/RHEL/CentOS Specific

```bash
# Install Python and pip
sudo dnf install python3 python3-pip

# Or for older versions
sudo yum install python3 python3-pip

# Install the application
pip3 install --user .
```

### Arch Linux Specific

```bash
# Install Python and pip
sudo pacman -S python python-pip

# Install the application
pip install --user .
```

---

## Windows Installation

### Method 1: Using pip

```powershell
# Install
pip install .

# Run
telegram-contact-importer

# Or run main.py directly
python main.py
```

### Method 2: Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install
pip install .

# Run
telegram-contact-importer
```

---

## macOS Installation

### Using Homebrew (Recommended)

```bash
# Install Python 3 if not present
brew install python3

# Install the application
pip3 install .

# Run
telegram-contact-importer
```

### Using Virtual Environment

```bash
# Create virtual environment
python3 -m venv ~/telegram-importer-env

# Activate
source ~/telegram-importer-env/bin/activate

# Install
pip install .

# Run
telegram-contact-importer
```

---

## Docker Installation

### Build and Run

```bash
# Build the Docker image
docker build -t telegram-contact-importer .

# Run interactively
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  telegram-contact-importer

# Run with specific file
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  telegram-contact-importer --preview /app/data/phones.txt
```

### Using Docker Compose

```bash
# Start the application
docker-compose up

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

---

## Development Installation

For development and contributing:

```bash
# Clone the repository
git clone https://github.com/Domains18/ct226.git
cd ct226

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Or install dev requirements separately
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Run tests
pytest tests/

# Format code
black src/

# Lint code
flake8 src/
```

---

## Post-Installation Setup

### 1. Get Telegram API Credentials

1. Visit [https://my.telegram.org/apps](https://my.telegram.org/apps)
2. Log in with your phone number
3. Create a new application
4. Note your `api_id` and `api_hash`

### 2. Configuration

```bash
# Copy default configuration
cp config.yaml.example config.yaml  # if example exists

# Edit configuration
nano config.yaml  # or vim, or any editor
```

### 3. First Run

```bash
# Run the application
telegram-contact-importer

# Or
python main.py

# Test installation
telegram-contact-importer --help
```

---

## Verify Installation

```bash
# Check if installed correctly
which telegram-contact-importer

# Check version
telegram-contact-importer --version  # if version flag is implemented

# Run tests
python test_setup.py
```

---

## Uninstallation

```bash
# Using pip
pip uninstall contact-importer

# Remove configuration and data (optional)
rm -rf ~/.config/telegram-contact-importer
rm -f telegram_config.json *.session
```

---

## Troubleshooting

### Command not found after installation

**Linux/macOS:**
```bash
# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Windows:**
- Add Python Scripts folder to PATH: `C:\Users\YourName\AppData\Local\Programs\Python\Python3X\Scripts`

### Permission denied

```bash
# Use --user flag
pip install --user .

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install .
```

### Module not found errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or use the installer
python install.py
```

### Telegram authentication issues

```bash
# Remove old session files
rm -f *.session telegram_*.json

# Try again with fresh authentication
telegram-contact-importer
```

### Python version issues

```bash
# Check Python version (must be 3.7+)
python --version

# Use specific Python version
python3.9 -m pip install .
```

### cryptg installation fails

```bash
# Install build dependencies first
# Ubuntu/Debian:
sudo apt install python3-dev build-essential

# Fedora/RHEL:
sudo dnf install python3-devel gcc

# macOS:
xcode-select --install
```

---

## System Service Installation (Linux)

To run as a background service:

```bash
# Copy service file
sudo cp telegram-importer.service /etc/systemd/system/

# Edit service file with your paths
sudo nano /etc/systemd/system/telegram-importer.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable telegram-importer
sudo systemctl start telegram-importer

# Check status
sudo systemctl status telegram-importer
```

---

## Updating

```bash
# If installed from source
cd ct226
git pull
pip install --upgrade .

# If installed from PyPI (future)
pip install --upgrade contact-importer
```

---

## Support

- **Issues**: https://github.com/Domains18/ct226/issues
- **Documentation**: See README.md
- **Configuration**: See config.yaml
