# Contact Importer Makefile

.PHONY: install dev-install test lint format clean run help

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install package and dependencies"
	@echo "  dev-install  - Install in development mode with dev dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black"
	@echo "  clean        - Clean build artifacts"
	@echo "  run          - Run the application with sample data"
	@echo "  help         - Show this help message"

# Install package and dependencies
install:
	pip install -r requirements.txt
	pip install -e .

# Install in development mode
dev-install:
	pip install -r requirements.txt
	pip install -e .
	pip install pytest black flake8

# Run tests
test:
	python -m pytest tests/ -v

# Run linting
lint:
	flake8 src/ --max-line-length=100
	python -m py_compile src/*.py

# Format code
format:
	black src/ --line-length=100
	black *.py --line-length=100

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -f *.log

# Run with sample data
run:
	@echo "Creating sample phone numbers file..."
	@echo "+254712345678\n0722334455\n254733556677\n+1-555-123-4567" > sample_phones.txt
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
