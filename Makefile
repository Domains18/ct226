# Telegram Contact Importer Makefile

.PHONY: install setup test test-parse run preview clean help

# Default target
help:
	@echo "🚀 Telegram Contact Importer - Available Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup        - Install dependencies and setup environment"
	@echo "  install      - Install Python dependencies only"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test         - Run the test suite"
	@echo "  test-parse   - Test phone number parsing only"
	@echo ""
	@echo "Running Commands:"
	@echo "  run          - Run the interactive CLI application"
	@echo "  preview      - Preview sample data file"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  clean        - Clean temporary files and caches"
	@echo "  help         - Show this help message"

# Full setup with dependencies and environment
setup:
	@echo "🚀 Setting up Telegram Contact Importer..."
	python install.py

# Install Python dependencies only
install:
	@echo "📦 Installing Python dependencies..."
	pip install -r requirements.txt

# Install in development mode
dev-install:
	pip install -r requirements.txt
	pip install -e .
	pip install pytest black flake8

# Run tests
test:
	@echo "🧪 Running test suite..."
	python test_setup.py

# Test phone number parsing only
test-parse:
	@echo "📱 Testing phone number parsing..."
	python main.py --preview src/data/HGCS12.txt

# Run the interactive CLI application
run:
	@echo "🚀 Starting Telegram Contact Importer..."
	python main.py

# Preview the sample data file
preview:
	@echo "📄 Previewing sample data..."
	python main.py --preview src/data/HGCS12.txt

# Clean temporary files and caches
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	find . -type f -name "*.session" -delete
	find . -type f -name "telegram_*.json" -delete
	rm -rf build/ dist/ *.egg-info/
	@echo "✅ Cleanup completed"
	@echo "Running contact importer..."
	python src/cli.py sample_phones.txt --verbose

# Create sample data
sample:
	@echo "Creating sample data files..."
	@echo "+254712345678" > sample_phones.txt
	@echo "0722334455" >> sample_phones.txt
	@echo "254733556677" >> sample_phones.txt
	@echo "+1-555-123-4567" >> sample_phones.txt
	@echo "0700123456" >> sample_phones.txt
	@echo "Sample phone numbers created in sample_phones.txt"
