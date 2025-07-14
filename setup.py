#!/usr/bin/env python3
"""
Setup script for UptimeWatcher
"""

import sys
import subprocess
import os
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    try:
        # Create log directory
        log_dir = Path("/tmp/SelfCare")
        log_dir.mkdir(exist_ok=True)
        
        # Create config directory
        config_dir = Path.home() / ".config" / "UptimeWatcher"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        print("✅ Directories created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating directories: {e}")
        return False

def create_desktop_entry():
    """Create desktop entry for Linux"""
    if not sys.platform.startswith('linux'):
        return True
        
    desktop_file = Path.home() / ".local/share/applications/uptimewatcher.desktop"
    desktop_file.parent.mkdir(parents=True, exist_ok=True)
    
    current_dir = Path(__file__).parent.absolute()
    main_script = current_dir / "main.py"
    
    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=UptimeWatcher
Comment=System uptime monitor
Exec=python3 {main_script}
Icon=preferences-system
StartupNotify=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
"""
    
    try:
        with open(desktop_file, 'w') as f:
            f.write(desktop_content)
        print("✅ Desktop entry created!")
        return True
    except Exception as e:
        print(f"❌ Error creating desktop entry: {e}")
        return False

def main():
    """Main setup function"""
    print("🔧 Setting up UptimeWatcher...")
    print("="*50)
    
    success = True
    
    # Install dependencies
    if not install_dependencies():
        success = False
    
    # Create directories
    if not create_directories():
        success = False
    
    # Create desktop entry (Linux only)
    if not create_desktop_entry():
        success = False
    
    print("="*50)
    if success:
        print("✅ Setup completed successfully!")
        print(f"\nTo run UptimeWatcher:")
        print(f"  python3 {Path(__file__).parent.absolute() / 'main.py'}")
        print(f"\nLogs will be stored in: /tmp/SelfCare/uptimewatcher.log")
        print(f"Config will be stored in: {Path.home() / '.config/UptimeWatcher/config.json'}")
    else:
        print("❌ Setup completed with errors!")
        sys.exit(1)

if __name__ == "__main__":
    main()
