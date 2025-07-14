#!/usr/bin/env python3
"""
UptimeWatcher - A cross-platform system uptime monitor
Monitors system uptime and displays reboot notifications after 24 hours
"""

import sys
import os
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, 
                               QMessageBox, QDialog, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QSpinBox, QComboBox)
from PySide6.QtCore import QTimer, QThread, Signal, Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QAction
import psutil
import darkdetect

class UptimeChecker(QThread):
    """Thread to check system uptime every 5 minutes"""
    uptime_signal = Signal(int)  # Signal to emit uptime in seconds
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        while self.running:
            try:
                # Get system uptime using psutil
                uptime_seconds = int(time.time() - psutil.boot_time())
                self.uptime_signal.emit(uptime_seconds)
                
                # Wait 5 minutes (300 seconds)
                for _ in range(300):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                logging.error(f"Error checking uptime: {e}")
                time.sleep(60)  # Wait 1 minute on error
                
    def stop(self):
        self.running = False

class DelayDialog(QDialog):
    """Dialog to select delay time when user chooses 'Do it later'"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delay Reboot Reminder")
        self.setModal(True)
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout()
        
        # Label
        label = QLabel("How long would you like to delay the reminder?")
        layout.addWidget(label)
        
        # Time selection
        time_layout = QHBoxLayout()
        self.time_spinbox = QSpinBox()
        self.time_spinbox.setRange(1, 24)
        self.time_spinbox.setValue(2)
        
        self.time_unit = QComboBox()
        self.time_unit.addItems(["Hours", "Minutes"])
        
        time_layout.addWidget(self.time_spinbox)
        time_layout.addWidget(self.time_unit)
        time_layout.addStretch()
        
        layout.addLayout(time_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def get_delay_seconds(self):
        """Return delay in seconds"""
        value = self.time_spinbox.value()
        unit = self.time_unit.currentText()
        
        if unit == "Hours":
            return value * 3600
        else:  # Minutes
            return value * 60

class UptimeWatcher(QApplication):
    """Main application class"""
    
    def __init__(self):
        super().__init__(sys.argv)
        
        # Setup logging
        self.setup_logging()
        
        # Configuration
        self.config_file = Path.home() / ".config" / "UptimeWatcher" / "config.json"
        self.config = self.load_config()
        
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "System Tray",
                               "System tray is not available on this system.")
            sys.exit(1)
            
        # Create system tray icon
        self.create_tray_icon()
        
        # Start uptime checker thread
        self.uptime_checker = UptimeChecker()
        self.uptime_checker.uptime_signal.connect(self.handle_uptime)
        self.uptime_checker.start()
        
        # Apply dark mode if detected
        self.apply_theme()
        
        logging.info("UptimeWatcher started")
        
    def setup_logging(self):
        """Setup logging to /tmp/SelfCare directory"""
        log_dir = Path("/tmp/SelfCare")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "uptimewatcher.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def load_config(self):
        """Load configuration from file"""
        default_config = {
            "last_reboot_reminder": 0,
            "ignore_until": 0,
            "ignore_today": False,
            "last_boot_time": 0
        }
        
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return {**default_config, **config}
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            
        return default_config
        
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving config: {e}")
            
    def create_tray_icon(self):
        """Create system tray icon and menu"""
        # Create a simple timer icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.create_timer_icon())
        self.tray_icon.setToolTip("UptimeWatcher")
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Show uptime action
        self.uptime_action = QAction("Uptime: Checking...", self)
        self.uptime_action.setEnabled(False)
        tray_menu.addAction(self.uptime_action)
        
        tray_menu.addSeparator()
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tray_menu.addAction(settings_action)
        
        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        tray_menu.addAction(about_action)
        
        tray_menu.addSeparator()
        
        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def create_timer_icon(self):
        """Create a simple timer icon"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw clock face
        painter.setPen(Qt.white if darkdetect.isDark() else Qt.black)
        painter.drawEllipse(2, 2, 28, 28)
        
        # Draw clock hands
        painter.drawLine(16, 16, 16, 8)   # Hour hand
        painter.drawLine(16, 16, 22, 16)  # Minute hand
        
        painter.end()
        return QIcon(pixmap)
        
    def apply_theme(self):
        """Apply dark theme if system is in dark mode"""
        if darkdetect.isDark():
            self.setStyleSheet("""
                QDialog {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #3c3c3c;
                    border: 1px solid #555555;
                    color: #ffffff;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #4c4c4c;
                }
                QSpinBox, QComboBox {
                    background-color: #3c3c3c;
                    border: 1px solid #555555;
                    color: #ffffff;
                    padding: 2px;
                }
            """)
            
    def handle_uptime(self, uptime_seconds):
        """Handle uptime signal from checker thread"""
        current_boot_time = psutil.boot_time()
        
        # Update tray tooltip
        uptime_str = self.format_uptime(uptime_seconds)
        self.uptime_action.setText(f"Uptime: {uptime_str}")
        self.tray_icon.setToolTip(f"UptimeWatcher - Uptime: {uptime_str}")
        
        # Check if system has rebooted
        if self.config["last_boot_time"] != 0 and current_boot_time != self.config["last_boot_time"]:
            self.config["ignore_today"] = False
            self.config["ignore_until"] = 0
            
        self.config["last_boot_time"] = current_boot_time
        
        # Check if we should show reboot reminder
        if uptime_seconds > 24 * 3600:  # More than 24 hours
            current_time = time.time()
            
            # Check ignore conditions
            if self.config["ignore_today"]:
                # Check if it's a new day
                if datetime.now().date() > datetime.fromtimestamp(self.config["last_reboot_reminder"]).date():
                    self.config["ignore_today"] = False
                else:
                    return
                    
            if current_time < self.config["ignore_until"]:
                return
                
            # Show reboot reminder
            self.show_reboot_reminder(uptime_seconds)
            
        self.save_config()
        logging.info(f"Uptime check: {uptime_str}")
        
    def format_uptime(self, seconds):
        """Format uptime seconds to human readable string"""
        days = seconds // (24 * 3600)
        hours = (seconds % (24 * 3600)) // 3600
        minutes = (seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
            
    def show_reboot_reminder(self, uptime_seconds):
        """Show reboot reminder dialog"""
        uptime_str = self.format_uptime(uptime_seconds)
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Reboot Recommended")
        msg.setText(f"Your system has been running for {uptime_str}.")
        msg.setInformativeText("It's recommended to reboot your system regularly. Would you like to reboot now?")
        
        # Custom buttons
        reboot_btn = msg.addButton("Reboot Now", QMessageBox.AcceptRole)
        later_btn = msg.addButton("Do it Later", QMessageBox.RejectRole)
        not_today_btn = msg.addButton("Not Today", QMessageBox.RejectRole)
        
        msg.exec()
        
        clicked_button = msg.clickedButton()
        current_time = time.time()
        
        if clicked_button == reboot_btn:
            self.reboot_system()
        elif clicked_button == later_btn:
            self.handle_delay_request()
        elif clicked_button == not_today_btn:
            self.config["ignore_today"] = True
            self.config["last_reboot_reminder"] = current_time
            
        self.save_config()
        
    def handle_delay_request(self):
        """Handle delay request from user"""
        dialog = DelayDialog(self)
        if dialog.exec() == QDialog.Accepted:
            delay_seconds = dialog.get_delay_seconds()
            self.config["ignore_until"] = time.time() + delay_seconds
            logging.info(f"Reboot reminder delayed by {delay_seconds} seconds")
            
    def reboot_system(self):
        """Reboot the system based on platform"""
        try:
            if sys.platform.startswith('win'):
                os.system('shutdown /r /t 0')
            elif sys.platform.startswith('darwin'):  # macOS
                os.system('sudo shutdown -r now')
            elif sys.platform.startswith('linux') or sys.platform.startswith('freebsd'):
                os.system('sudo reboot')
            else:
                QMessageBox.warning(None, "Unsupported Platform", 
                                  "Automatic reboot is not supported on this platform.")
                logging.warning("Unsupported platform for automatic reboot")
        except Exception as e:
            logging.error(f"Error rebooting system: {e}")
            QMessageBox.critical(None, "Reboot Error", f"Failed to reboot: {e}")
            
    def show_settings(self):
        """Show settings dialog"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Settings")
        msg.setText("UptimeWatcher Settings")
        msg.setInformativeText(f"Config file: {self.config_file}\nLog file: /tmp/SelfCare/uptimewatcher.log")
        msg.exec()
        
    def show_about(self):
        """Show about dialog"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("About UptimeWatcher")
        msg.setText("UptimeWatcher v1.0")
        msg.setInformativeText("A cross-platform system uptime monitor\n\nMonitors system uptime and reminds you to reboot after 24 hours.")
        msg.exec()
        
    def quit_application(self):
        """Quit the application"""
        self.uptime_checker.stop()
        self.uptime_checker.wait()
        logging.info("UptimeWatcher stopped")
        self.quit()

def main():
    """Main function"""
    app = UptimeWatcher()
    app.setQuitOnLastWindowClosed(False)  # Keep running in background
    
    # Handle Ctrl+C gracefully
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
