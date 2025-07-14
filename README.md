# UptimeWatcher

A cross-platform system uptime monitor that runs in the background and reminds you to reboot your system after 24 hours of continuous operation.

## Features

- 🖥️ **Cross-platform**: Works on Windows, macOS, Linux, and FreeBSD
- ⏰ **Automatic monitoring**: Checks system uptime every 5 minutes
- 🔔 **Smart notifications**: Shows reboot reminders after 24 hours uptime
- 🎨 **Dark mode support**: Automatically adapts to system theme
- 📱 **System tray integration**: Runs quietly in the background
- 🔧 **Flexible options**: Three response options for reboot reminders
- 📝 **Logging**: Detailed logs stored in `/tmp/SelfCare/`

## Installation

### Quick Install (Linux)
```bash
git clone https://github.com/yourusername/UptimeWatcher.git
cd UptimeWatcher
./build-and-install.sh
```

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/UptimeWatcher.git
cd UptimeWatcher
```

2. Create virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/macOS
# or
venv\Scripts\activate     # On Windows
pip install -r requirements.txt
```

3. Run from source:
```bash
python main.py
```

### Building Executable

1. Build for current platform:
```bash
python build.py
```

2. Install the built executable (Linux):
```bash
./install-linux.sh
```

### Platform-Specific Builds

- **Linux**: `pyinstaller uptimewatcher-linux.spec`
- **Windows**: `pyinstaller uptimewatcher-windows.spec`
- **macOS**: `pyinstaller uptimewatcher-macos.spec`

## Usage

### Running the Application

The application runs in the background with a system tray icon. Once started, it will:

1. Monitor system uptime every 5 minutes
2. Display current uptime in the system tray tooltip
3. Show a reboot reminder dialog when uptime exceeds 24 hours

### Reboot Reminder Options

When the 24-hour uptime threshold is reached, you'll see a dialog with three options:

1. **Reboot Now**: Immediately restarts the system
2. **Do it Later**: Delays the reminder for a specified time (1-24 hours or minutes)
3. **Not Today**: Ignores reminders until the next day

### System Tray Menu

Right-click the system tray icon to access:

- **Uptime**: Current system uptime display
- **Settings**: View configuration and log file locations
- **About**: Application information
- **Quit**: Exit the application

## Configuration

The application stores its configuration in:
- **Linux/macOS**: `~/.config/UptimeWatcher/config.json`
- **Windows**: `%APPDATA%\UptimeWatcher\config.json`

## Logging

Logs are stored in `/tmp/SelfCare/uptimewatcher.log` and include:
- Application start/stop events
- Uptime checks
- User interactions with reboot reminders
- Error messages

## Platform-Specific Notes

### Linux/FreeBSD
- Requires `sudo` privileges for system reboot
- Uses `sudo reboot` command

### macOS
- Requires `sudo` privileges for system reboot
- Uses `sudo shutdown -r now` command

### Windows
- Uses `shutdown /r /t 0` command
- May require administrator privileges

## Dependencies

- **PySide6**: GUI framework
- **psutil**: System information and process utilities
- **darkdetect**: Dark mode detection

## Development

### Project Structure
```
UptimeWatcher/
├── main.py                      # Main application
├── requirements.txt             # Dependencies
├── build.py                     # Build script for PyInstaller
├── build-and-install.sh         # One-click build and install (Linux)
├── install-linux.sh             # Linux installer script
├── run.sh                       # Development runner script
├── setup.py                     # Setup script
├── uptimewatcher-linux.spec     # PyInstaller spec for Linux
├── uptimewatcher-windows.spec   # PyInstaller spec for Windows
├── uptimewatcher-macos.spec     # PyInstaller spec for macOS
├── version_info.txt             # Version info for Windows builds
├── dist/                        # Built executables
├── build/                       # Build artifacts
├── venv/                        # Virtual environment
└── README.md                    # This file
```

### Key Components

- **UptimeWatcher**: Main application class
- **UptimeChecker**: Background thread for uptime monitoring
- **DelayDialog**: Dialog for selecting reminder delays

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Support

If you encounter any issues or have questions, please create an issue on the GitHub repository.
