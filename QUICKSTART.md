# 🚀 Quick Start Guide

## Prerequisites
- Python 3.7+ installed
- Telegram account
- API credentials from https://my.telegram.org/apps

---

## Installation (Choose One)

### 🐧 Linux - Automated
```bash
chmod +x install.sh
./install.sh
source activate.sh
```

### 🐧 Linux - Manual
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### 🪟 Windows
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### 🐳 Docker
```bash
docker build -t telegram-importer .
docker run -it --rm -v $(pwd)/data:/app/data telegram-importer
```

---

## First Run

1. **Get Telegram API Credentials**
   - Visit: https://my.telegram.org/apps
   - Create new application
   - Save your `api_id` and `api_hash`

2. **Run the application**
   ```bash
   telegram-contact-importer
   # or
   python main.py
   ```

3. **Follow the prompts**
   - Enter API credentials
   - Enter your phone number
   - Enter verification code from Telegram

---

## Usage Examples

### Interactive Mode
```bash
telegram-contact-importer
```

### Preview Phone Numbers
```bash
telegram-contact-importer --preview data/phones.txt
python main.py --preview src/data/HGCS12.txt
```

### Show Configuration
```bash
telegram-contact-importer --config
python main.py --config
```

### Verbose Mode
```bash
telegram-contact-importer --verbose
```

---

## File Format

Your phone number file should contain one number per line:

```
821020131384
+852 1234 5678
254712345678
+1-555-123-4567
```

Supported formats:
- With/without country code
- With/without + prefix
- With/without spaces or hyphens
- International format

---

## Configuration

Edit `config.yaml` to customize:
- Default country code
- Output formats
- Phone number formatting
- Logging settings

---

## Troubleshooting

### Command not found
```bash
# Linux/Mac - Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or activate venv
source venv/bin/activate
```

### Import errors
```bash
pip install -r requirements.txt --force-reinstall
```

### Authentication issues
```bash
# Remove old sessions
rm -f *.session telegram_*.json
```

---

## Common Commands

```bash
# Install
pip install -e .

# Run
telegram-contact-importer

# Test
python test_setup.py

# Preview file
python main.py --preview data.txt

# Check config
python main.py --config

# Clean up
make clean  # or manually delete *.session, *.log files
```

---

## Need Help?

- 📖 Full documentation: [INSTALL.md](INSTALL.md)
- 🐛 Report issues: https://github.com/Domains18/ct226/issues
- 💡 Improvements: [IMPROVEMENTS.md](IMPROVEMENTS.md)

---

## Quick Commands Reference

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make run` | Run the application |
| `make test` | Run tests |
| `make clean` | Clean temporary files |
| `make preview` | Preview sample data |
