#!/bin/bash
# UptimeWatcher Linux Installer Script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="UptimeWatcher"
INSTALL_DIR="/opt/uptimewatcher"
BINARY_NAME="uptimewatcher"
DESKTOP_FILE="uptimewatcher.desktop"
AUTOSTART_FILE="$HOME/.config/autostart/$DESKTOP_FILE"
APPLICATIONS_DIR="$HOME/.local/share/applications"
LOG_DIR="/tmp/SelfCare"
CONFIG_DIR="$HOME/.config/UptimeWatcher"

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  $APP_NAME Linux Installer${NC}"
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

check_requirements() {
    print_info "Checking requirements..."
    
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
    
    if [ ! -f "dist/$BINARY_NAME" ]; then
        print_error "Binary 'dist/$BINARY_NAME' not found. Please build first with: python3 build.py"
        exit 1
    fi
    
    print_success "Requirements check passed"
}

create_directories() {
    print_info "Creating directories..."
    
    # Create install directory (requires sudo)
    if [ ! -d "$INSTALL_DIR" ]; then
        sudo mkdir -p "$INSTALL_DIR"
        print_success "Created $INSTALL_DIR"
    fi
    
    # Create user directories
    mkdir -p "$APPLICATIONS_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$(dirname "$AUTOSTART_FILE")"
    
    print_success "Directories created"
}

install_binary() {
    print_info "Installing binary..."
    
    # Copy binary to install directory
    sudo cp "dist/$BINARY_NAME" "$INSTALL_DIR/"
    sudo chmod +x "$INSTALL_DIR/$BINARY_NAME"
    
    # Create symbolic link in /usr/local/bin
    if [ -f "/usr/local/bin/$BINARY_NAME" ]; then
        sudo rm "/usr/local/bin/$BINARY_NAME"
    fi
    sudo ln -sf "$INSTALL_DIR/$BINARY_NAME" "/usr/local/bin/$BINARY_NAME"
    
    print_success "Binary installed to $INSTALL_DIR"
}

create_desktop_file() {
    print_info "Creating desktop file..."
    
    cat > "$APPLICATIONS_DIR/$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Comment=System uptime monitor and reboot reminder
Exec=$INSTALL_DIR/$BINARY_NAME
Icon=preferences-system-time
StartupNotify=false
NoDisplay=false
Categories=System;Monitor;
Keywords=uptime;system;monitor;reboot;
Terminal=false
StartupWMClass=UptimeWatcher
EOF
    
    chmod +x "$APPLICATIONS_DIR/$DESKTOP_FILE"
    print_success "Desktop file created"
}

create_autostart_file() {
    print_info "Creating autostart file..."
    
    cat > "$AUTOSTART_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Comment=System uptime monitor and reboot reminder
Exec=$INSTALL_DIR/$BINARY_NAME
Icon=preferences-system-time
StartupNotify=false
NoDisplay=true
Categories=System;Monitor;
Keywords=uptime;system;monitor;reboot;
Terminal=false
StartupWMClass=UptimeWatcher
X-GNOME-Autostart-enabled=true
Hidden=false
EOF
    
    chmod +x "$AUTOSTART_FILE"
    print_success "Autostart file created"
}

create_uninstaller() {
    print_info "Creating uninstaller..."
    
    cat > "$INSTALL_DIR/uninstall.sh" << EOF
#!/bin/bash
# UptimeWatcher Uninstaller

echo "Uninstalling $APP_NAME..."

# Kill running processes
pkill -f "$BINARY_NAME" || true

# Remove files
sudo rm -f "/usr/local/bin/$BINARY_NAME"
sudo rm -rf "$INSTALL_DIR"
rm -f "$APPLICATIONS_DIR/$DESKTOP_FILE"
rm -f "$AUTOSTART_FILE"

# Ask about config and logs
read -p "Remove configuration and logs? (y/N): " -n 1 -r
echo
if [[ \$REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$CONFIG_DIR"
    rm -rf "$LOG_DIR"
    echo "Configuration and logs removed"
fi

echo "$APP_NAME uninstalled successfully!"
EOF
    
    sudo chmod +x "$INSTALL_DIR/uninstall.sh"
    print_success "Uninstaller created at $INSTALL_DIR/uninstall.sh"
}

start_application() {
    print_info "Starting application..."
    
    # Kill any existing instances
    pkill -f "$BINARY_NAME" || true
    sleep 2
    
    # Start the application in background
    nohup "$INSTALL_DIR/$BINARY_NAME" > /dev/null 2>&1 &
    
    sleep 3
    
    # Check if it's running
    if pgrep -f "$BINARY_NAME" > /dev/null; then
        print_success "Application started successfully"
    else
        print_error "Failed to start application"
        exit 1
    fi
}

main() {
    print_header
    
    check_requirements
    create_directories
    install_binary
    create_desktop_file
    create_autostart_file
    create_uninstaller
    start_application
    
    echo
    print_success "Installation completed successfully!"
    echo
    echo -e "${BLUE}📋 Installation Summary:${NC}"
    echo -e "   Binary: $INSTALL_DIR/$BINARY_NAME"
    echo -e "   Desktop file: $APPLICATIONS_DIR/$DESKTOP_FILE"
    echo -e "   Autostart: $AUTOSTART_FILE"
    echo -e "   Logs: $LOG_DIR"
    echo -e "   Config: $CONFIG_DIR"
    echo -e "   Uninstaller: $INSTALL_DIR/uninstall.sh"
    echo
    echo -e "${GREEN}🚀 $APP_NAME is now running in the background!${NC}"
    echo -e "${YELLOW}💡 Look for the timer icon in your system tray${NC}"
    echo
    echo -e "${BLUE}📝 To uninstall later, run:${NC}"
    echo -e "   sudo $INSTALL_DIR/uninstall.sh"
    echo
}

# Run main function
main "$@"
