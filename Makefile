# Telegram Contact Importer Makefile

.PHONY: install setup test test-parse run preview clean help build docker package

# Default target
help:
	@echo "🚀 Telegram Contact Importer - Available Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup        - Full installation with dependencies and environment"
	@echo "  install      - Install Python dependencies only"
	@echo "  dev-install  - Install in development mode with dev dependencies"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test         - Run the test suite"
	@echo "  test-parse   - Test phone number parsing only"
	@echo ""
	@echo "Running Commands:"
	@echo "  run          - Run the interactive CLI application"
	@echo "  preview      - Preview sample data file"
	@echo ""
	@echo "Build & Package Commands:"
	@echo "  build        - Build distribution packages"
	@echo "  package      - Create wheel and source distribution"
	@echo "  docker       - Build Docker image"
	@echo "  docker-run   - Run in Docker container"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  clean        - Clean temporary files and caches"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code with black"
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
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "__pycache__" -delete 2>/dev/null || true
	find . -type f -name "*.log" -delete 2>/dev/null || true
	find . -type f -name "*.session" -delete 2>/dev/null || true
	find . -type f -name "telegram_*.json" -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ 2>/dev/null || true
	@echo "✅ Cleanup completed"

# Build distribution packages
build: clean
	@echo "📦 Building distribution packages..."
	python -m build

# Create package
package: build
	@echo "✅ Package created in dist/"

# Build Docker image
docker:
	@echo "🐳 Building Docker image..."
	docker build -t telegram-contact-importer:latest .

# Run in Docker
docker-run:
	@echo "🐳 Running in Docker..."
	docker run -it --rm \
		-v $$(pwd)/data:/app/data \
		-v $$(pwd)/logs:/app/logs \
		telegram-contact-importer:latest

# Lint code
lint:
	@echo "🔍 Linting code..."
	flake8 src/ main.py --max-line-length=127

# Format code
format:
	@echo "✨ Formatting code..."
	black src/ main.py

# Create sample data
sample:
	@echo "Creating sample data files..."
	@mkdir -p data
	@echo "+254712345678" > data/sample_phones.txt
	@echo "0722334455" >> data/sample_phones.txt
	@echo "254733556677" >> data/sample_phones.txt
	@echo "+1-555-123-4567" >> data/sample_phones.txt
	@echo "0700123456" >> data/sample_phones.txt
	@echo "Sample phone numbers created in data/sample_phones.txt"

# Check if everything is installed correctly
check:
	@echo "🔍 Checking installation..."
	@python -c "import sys; print(f'Python: {sys.version}')"
	@python -c "from src.phone_parser import parse_phone_file; print('✓ Imports working')"
	@echo "✅ Installation looks good!"
