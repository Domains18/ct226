# 📱 Telegram Contact Importer CLI

An interactive command-line application for bulk importing phone numbers to your Telegram account. This tool is designed for legitimate contact management purposes and follows Telegram's API guidelines.

## ✨ Features

- **Interactive CLI**: User-friendly menu system with colored output
- **Bulk Import**: Add hundreds of contacts in batches with progress tracking
- **Phone Validation**: Automatic phone number validation and formatting
- **Error Handling**: Robust error handling with detailed logging
- **Skip Duplicates**: Automatically skip existing contacts
- **Progress Tracking**: Real-time progress bars and detailed statistics
- **Session Management**: Persistent Telegram session management
- **File Support**: Import from text files with various phone number formats

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Telegram API Credentials

1. Go to [https://my.telegram.org/apps](https://my.telegram.org/apps)
2. Create a new application
3. Note down your `api_id` and `api_hash`

### 3. Run the Application

```bash
python main.py
```

## Usage

```bash
# Basic usage
python contact_importer.py input.txt

# Specify output format and file
python contact_importer.py input.txt --output contacts.vcf --format vcf

# With country code assumption
python contact_importer.py input.txt --country-code KE

# Verbose mode
python contact_importer.py input.txt --verbose
```

## File Format

Input file should contain one phone number per line:
```
+254712345678
0712345678
254712345678
+1-555-123-4567
```

## Output Formats

- VCF (vCard) - Default
- CSV
- JSON
