#!/bin/bash
# UptimeWatcher - Build and Install Script for Linux

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  UptimeWatcher Build & Install${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

check_python() {
    print_info "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.7 or later."
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Python $python_version found"
}

install_dependencies() {
    print_info "Installing Python dependencies..."
    
    # Install pip if not available
    if ! command -v pip3 &> /dev/null; then
        print_info "Installing pip..."
        sudo apt update
        sudo apt install -y python3-pip
    fi
    
    # Install requirements
    pip3 install -r requirements.txt
    print_success "Dependencies installed"
}

build_application() {
    print_info "Building application..."
    
    # Run build script
    python3 build.py
    
    if [ -f "dist/uptimewatcher" ]; then
        print_success "Build completed successfully"
    else
        print_error "Build failed - executable not found"
        exit 1
    fi
}

install_application() {
    print_info "Installing application..."
    
    # Run install script
    ./install-linux.sh
    
    print_success "Installation completed"
}

main() {
    print_header
    
    # Check if we're in the right directory
    if [ ! -f "main.py" ]; then
        print_error "Please run this script from the UptimeWatcher directory"
        exit 1
    fi
    
    check_python
    install_dependencies
    build_application
    install_application
    
    echo
    print_success "UptimeWatcher has been built and installed successfully!"
    echo
    echo -e "${BLUE}🎉 You can now:${NC}"
    echo -e "   • Find UptimeWatcher in your application menu"
    echo -e "   • Run it from terminal: uptimewatcher"
    echo -e "   • It will start automatically on next login"
    echo
    echo -e "${YELLOW}💡 The application is now running in the background!${NC}"
    echo -e "${YELLOW}   Look for the timer icon in your system tray${NC}"
    echo
}

# Run main function
main "$@"
