#!/usr/bin/env python3
"""
Build script for UptimeWatcher using PyInstaller
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller is already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully")

def clean_build_dirs():
    """Clean previous build directories"""
    build_dirs = ['build', 'dist', '__pycache__']
    for dir_name in build_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 Cleaned {dir_name}/")

def build_for_platform():
    """Build executable for current platform"""
    current_platform = platform.system().lower()
    
    if current_platform == 'linux':
        spec_file = 'uptimewatcher-linux.spec'
        print("🐧 Building for Linux...")
    elif current_platform == 'windows':
        spec_file = 'uptimewatcher-windows.spec'
        print("🪟 Building for Windows...")
    elif current_platform == 'darwin':
        spec_file = 'uptimewatcher-macos.spec'
        print("🍎 Building for macOS...")
    else:
        print(f"❌ Unsupported platform: {current_platform}")
        return False
    
    if not os.path.exists(spec_file):
        print(f"❌ Spec file {spec_file} not found!")
        return False
    
    try:
        # Run PyInstaller
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", spec_file]
        subprocess.check_call(cmd)
        print("✅ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_version_info():
    """Create version info file for Windows"""
    version_info = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
# filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
# Set not needed items to zero 0.
filevers=(1,0,0,0),
prodvers=(1,0,0,0),
# Contains a bitmask that specifies the valid bits 'flags'r
mask=0x3f,
# Contains a bitmask that specifies the Boolean attributes of the file.
flags=0x0,
# The operating system for which this file was designed.
# 0x4 - NT and there is no need to change it.
OS=0x4,
# The general type of file.
# 0x1 - the file is an application.
fileType=0x1,
# The function of the file.
# 0x0 - the function is not defined for this fileType
subtype=0x0,
# Creation date and time stamp.
date=(0, 0)
),
  kids=[
StringFileInfo(
  [
  StringTable(
    '040904B0',
    [StringStruct('CompanyName', 'UptimeWatcher'),
    StringStruct('FileDescription', 'System Uptime Monitor'),
    StringStruct('FileVersion', '1.0.0'),
    StringStruct('InternalName', 'UptimeWatcher'),
    StringStruct('LegalCopyright', 'Copyright (c) 2025'),
    StringStruct('OriginalFilename', 'UptimeWatcher.exe'),
    StringStruct('ProductName', 'UptimeWatcher'),
    StringStruct('ProductVersion', '1.0.0')])
  ]), 
VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)'''
    
    with open('version_info.txt', 'w') as f:
        f.write(version_info)
    print("✅ Version info file created")

def main():
    """Main build function"""
    print("🔨 Building UptimeWatcher...")
    print("=" * 50)
    
    # Create version info for Windows
    create_version_info()
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build for current platform
    success = build_for_platform()
    
    if success:
        print("=" * 50)
        print("✅ Build completed successfully!")
        print(f"📁 Executable can be found in: {os.path.abspath('dist')}")
        
        # List built files
        dist_dir = Path('dist')
        if dist_dir.exists():
            print("\n📦 Built files:")
            for item in dist_dir.iterdir():
                if item.is_file():
                    print(f"  📄 {item.name}")
                elif item.is_dir():
                    print(f"  📁 {item.name}/")
    else:
        print("❌ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
