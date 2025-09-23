# Contact Importer

A CLI tool to import phone numbers from text files and convert them to various contact formats.

## Features

- Parse plain text files with phone numbers
- Validate and format phone numbers
- Export to vCard (.vcf) format
- Support for different phone number formats
- Duplicate detection and handling
- Progress tracking for large files

## Installation

```bash
pip install -r requirements.txt
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
