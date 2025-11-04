#!/bin/bash

# Telegram Contact Importer - Linux Installation Script
# This script automates the installation process for Linux systems

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VENV_DIR="venv"
PYTHON_MIN_VERSION="3.7"
APP_NAME="telegram-contact-importer"

# Print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║         📱 Telegram Contact Importer - Installer            ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Compare version numbers
version_ge() {
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

# Check Python version
check_python() {
    print_info "Checking Python installation..."
    
    # Try different Python commands
    for cmd in python3 python; do
        if command_exists $cmd; then
            PYTHON_CMD=$cmd
            PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
            
            if version_ge "$PYTHON_VERSION" "$PYTHON_MIN_VERSION"; then
                print_success "Found Python $PYTHON_VERSION ($PYTHON_CMD)"
                return 0
            fi
        fi
    done
    
    print_error "Python $PYTHON_MIN_VERSION or higher is required"
    print_info "Please install Python 3.7+ and try again"
    print_info "Visit: https://www.python.org/downloads/"
    exit 1
}

# Check for pip
check_pip() {
    print_info "Checking pip installation..."
    
    if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        print_warning "pip not found, attempting to install..."
        
        # Try to install pip
        if command_exists apt-get; then
            sudo apt-get update && sudo apt-get install -y python3-pip
        elif command_exists yum; then
            sudo yum install -y python3-pip
        elif command_exists dnf; then
            sudo dnf install -y python3-pip
        else
            print_error "Could not install pip automatically"
            print_info "Please install pip manually: https://pip.pypa.io/en/stable/installation/"
            exit 1
        fi
    fi
    
    print_success "pip is available"
}

# Install system dependencies
install_system_deps() {
    print_info "Checking system dependencies..."
    
    # Detect package manager and install build tools
    if command_exists apt-get; then
        print_info "Detected Debian/Ubuntu system"
        if ! dpkg -l | grep -q python3-dev; then
            print_warning "Installing build dependencies..."
            sudo apt-get update
            sudo apt-get install -y python3-dev python3-venv build-essential libssl-dev
        fi
    elif command_exists dnf; then
        print_info "Detected Fedora/RHEL system"
        if ! rpm -qa | grep -q python3-devel; then
            print_warning "Installing build dependencies..."
            sudo dnf install -y python3-devel gcc openssl-devel
        fi
    elif command_exists yum; then
        print_info "Detected CentOS/RHEL system"
        if ! rpm -qa | grep -q python3-devel; then
            print_warning "Installing build dependencies..."
            sudo yum install -y python3-devel gcc openssl-devel
        fi
    elif command_exists pacman; then
        print_info "Detected Arch Linux system"
        if ! pacman -Qi base-devel >/dev/null 2>&1; then
            print_warning "Installing build dependencies..."
            sudo pacman -S --noconfirm base-devel
        fi
    fi
    
    print_success "System dependencies OK"
}

# Create virtual environment
create_venv() {
    print_info "Setting up virtual environment..."
    
    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
        else
            print_info "Using existing virtual environment"
            return 0
        fi
    fi
    
    $PYTHON_CMD -m venv "$VENV_DIR"
    print_success "Virtual environment created"
}

# Activate virtual environment
activate_venv() {
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
        print_success "Virtual environment activated"
    else
        print_error "Could not find virtual environment activation script"
        exit 1
    fi
}

# Upgrade pip
upgrade_pip() {
    print_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    print_success "pip upgraded"
}

# Install Python dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Install the application
install_app() {
    print_info "Installing application..."
    
    if [ -f "setup.py" ]; then
        pip install -e .
        print_success "Application installed in development mode"
    else
        print_warning "setup.py not found, skipping package installation"
    fi
}

# Create desktop entry (optional)
create_desktop_entry() {
    if [ "$INSTALL_DESKTOP" = true ]; then
        print_info "Creating desktop entry..."
        
        DESKTOP_FILE="$HOME/.local/share/applications/$APP_NAME.desktop"
        mkdir -p "$(dirname "$DESKTOP_FILE")"
        
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Telegram Contact Importer
Comment=Bulk import phone numbers to Telegram
Exec=$(pwd)/$VENV_DIR/bin/python $(pwd)/main.py
Icon=contact
Terminal=true
Categories=Utility;Network;
EOF
        
        chmod +x "$DESKTOP_FILE"
        print_success "Desktop entry created"
    fi
}

# Create activation script
create_activation_script() {
    print_info "Creating activation script..."
    
    cat > activate.sh << 'EOF'
#!/bin/bash
# Activate the Telegram Contact Importer environment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"

echo "✓ Telegram Contact Importer environment activated"
echo "Run 'telegram-contact-importer' or 'python main.py' to start"
EOF
    
    chmod +x activate.sh
    print_success "Created activate.sh script"
}

# Run tests
run_tests() {
    if [ "$RUN_TESTS" = true ]; then
        print_info "Running tests..."
        
        if [ -f "test_setup.py" ]; then
            python test_setup.py
            print_success "Tests passed"
        else
            print_warning "test_setup.py not found, skipping tests"
        fi
    fi
}

# Print post-installation instructions
print_instructions() {
    echo ""
    print_success "Installation completed successfully!"
    echo ""
    print_info "To use the application:"
    echo ""
    echo "  1. Activate the virtual environment:"
    echo "     ${GREEN}source venv/bin/activate${NC}"
    echo ""
    echo "     Or use the activation script:"
    echo "     ${GREEN}source activate.sh${NC}"
    echo ""
    echo "  2. Run the application:"
    echo "     ${GREEN}telegram-contact-importer${NC}"
    echo "     or"
    echo "     ${GREEN}python main.py${NC}"
    echo ""
    echo "  3. For help:"
    echo "     ${GREEN}python main.py --help${NC}"
    echo ""
    print_info "Before first run, you'll need:"
    echo "  - Telegram API credentials (api_id and api_hash)"
    echo "  - Get them from: https://my.telegram.org/apps"
    echo ""
    print_info "Configuration file: config.yaml"
    print_info "Documentation: README.md"
    echo ""
}

# Main installation function
main() {
    print_header
    
    # Parse arguments
    INSTALL_DESKTOP=false
    RUN_TESTS=false
    SKIP_VENV=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --desktop)
                INSTALL_DESKTOP=true
                shift
                ;;
            --test)
                RUN_TESTS=true
                shift
                ;;
            --no-venv)
                SKIP_VENV=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --desktop    Create desktop entry"
                echo "  --test       Run tests after installation"
                echo "  --no-venv    Install globally (not recommended)"
                echo "  --help       Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Check prerequisites
    check_python
    check_pip
    install_system_deps
    
    # Setup virtual environment unless skipped
    if [ "$SKIP_VENV" = false ]; then
        create_venv
        activate_venv
        upgrade_pip
    else
        print_warning "Skipping virtual environment (installing globally)"
    fi
    
    # Install application
    install_dependencies
    install_app
    
    # Optional features
    create_desktop_entry
    create_activation_script
    run_tests
    
    # Show instructions
    print_instructions
}

# Run main function
main "$@"
