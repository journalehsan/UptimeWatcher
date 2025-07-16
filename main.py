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
                               QLabel, QPushButton, QSpinBox, QComboBox, QFrame,
                               QScrollArea, QWidget)
from PySide6.QtCore import QTimer, QThread, Signal, Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QPixmap, QPainter, QAction, QFont, QPalette
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

class ModernDelayDialog(QDialog):
    """Modern iOS-style dialog for delay selection with scroll area"""
    
    def __init__(self, parent=None, total_delay_hours=0):
        super().__init__(parent)
        self.setWindowTitle("")
        self.setModal(True)
        self.setFixedSize(450, 500)  # Increased height from 300 to 500
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)
        
        self.total_delay_hours = total_delay_hours
        self.selected_delay = 0
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container frame
        container = QFrame()
        is_dark = darkdetect.isDark()
        
        if is_dark:
            container_bg = "rgba(40, 40, 40, 0.95)"
            container_border = "rgba(255, 255, 255, 0.1)"
        else:
            container_bg = "rgba(248, 248, 248, 0.95)"
            container_border = "rgba(0, 0, 0, 0.1)"
        
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {container_bg};
                border-radius: 20px;
                border: 1px solid {container_border};
            }}
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Delay Reboot Reminder")
        title_label.setAlignment(Qt.AlignCenter)
        title_color = "#FFFFFF" if is_dark else "#333"
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {title_color};
                margin-bottom: 10px;
            }}
        """)
        container_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("How long would you like to delay?")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_color = "#CCCCCC" if is_dark else "#666"
        subtitle_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {subtitle_color};
                margin-bottom: 20px;
            }}
        """)
        container_layout.addWidget(subtitle_label)
        
        # Create scroll area for buttons
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Dark mode scroll bar styling
        if is_dark:
            scroll_bg = "rgba(255, 255, 255, 0.1)"
            scroll_handle = "rgba(255, 255, 255, 0.3)"
            scroll_handle_hover = "rgba(255, 255, 255, 0.5)"
        else:
            scroll_bg = "rgba(0, 0, 0, 0.1)"
            scroll_handle = "rgba(0, 0, 0, 0.3)"
            scroll_handle_hover = "rgba(0, 0, 0, 0.5)"
        
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {scroll_bg};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {scroll_handle};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {scroll_handle_hover};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        
        # Create widget to hold buttons
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)
        buttons_layout.setSpacing(8)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        # Delay options
        delay_options = []
        
        if total_delay_hours < 48:
            delay_options = [
                ("24 hours later", 24 * 3600),
                ("10 hours later", 10 * 3600),
                ("5 hours later", 5 * 3600),
                ("3 hours later", 3 * 3600),
                ("1 hour later", 1 * 3600),
                ("10 minutes later", 10 * 60)
            ]
        else:
            delay_options = [
                ("10 minutes later", 10 * 60)
            ]
        
        # Filter options that would exceed 48 hours
        filtered_options = []
        for text, seconds in delay_options:
            if (total_delay_hours * 3600 + seconds) <= 48 * 3600:
                filtered_options.append((text, seconds))
        
        if not filtered_options:
            filtered_options = [("10 minutes later", 10 * 60)]
        
        # Create buttons for each option
        for text, seconds in filtered_options:
            btn = QPushButton(text)
            btn.setMinimumHeight(50)  # Increased button height
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #007AFF;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 15px 20px;
                    font-size: 16px;
                    font-weight: 600;
                    margin: 3px;
                }
                QPushButton:hover {
                    background-color: #0056CC;
                }
                QPushButton:pressed {
                    background-color: #004299;
                }
            """)
            btn.clicked.connect(lambda checked, s=seconds: self.delay_selected(s))
            buttons_layout.addWidget(btn)
        
        # Add stretch to push buttons to top
        buttons_layout.addStretch()
        
        # Set the buttons widget in the scroll area
        scroll_area.setWidget(buttons_widget)
        
        # Add scroll area to container
        container_layout.addWidget(scroll_area)
        
        # Warning label for 48 hour limit
        if total_delay_hours >= 24:
            warning_label = QLabel(f"⚠️ You've already delayed for {total_delay_hours} hours. Maximum delay is 48 hours.")
            warning_label.setAlignment(Qt.AlignCenter)
            warning_label.setWordWrap(True)
            warning_label.setStyleSheet("""
                QLabel {
                    font-size: 12px;
                    color: #FF3B30;
                    margin-top: 15px;
                    padding: 10px;
                    background-color: rgba(255, 59, 48, 0.1);
                    border-radius: 8px;
                }
            """)
            container_layout.addWidget(warning_label)
        
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        
        # Apply modern styling
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(0, 0, 0, 0.4);
            }
        """)
        
    def delay_selected(self, seconds):
        self.selected_delay = seconds
        self.accept()
        
    def get_delay_seconds(self):
        return self.selected_delay


class ModernRebootDialog(QDialog):
    """Modern iOS-style reboot dialog that can't be closed without action"""
    
    def __init__(self, parent=None, uptime_str=""):
        super().__init__(parent)
        self.setWindowTitle("")
        self.setModal(True)
        self.setFixedSize(450, 350)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint)
        
        self.user_action = None
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Container frame
        container = QFrame()
        is_dark = darkdetect.isDark()
        
        if is_dark:
            container_bg = "rgba(40, 40, 40, 0.98)"
            container_border = "rgba(255, 255, 255, 0.1)"
            title_color = "#FFFFFF"
            message_color = "#CCCCCC"
        else:
            container_bg = "rgba(248, 248, 248, 0.98)"
            container_border = "rgba(0, 0, 0, 0.1)"
            title_color = "#333"
            message_color = "#666"
        
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {container_bg};
                border-radius: 20px;
                border: 1px solid {container_border};
            }}
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(25)
        container_layout.setContentsMargins(40, 40, 40, 40)
        
        # Warning icon
        icon_label = QLabel("⚠️")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                margin-bottom: 10px;
            }
        """)
        container_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel("Reboot Recommended")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight: bold;
                color: {title_color};
                margin-bottom: 10px;
            }}
        """)
        container_layout.addWidget(title_label)
        
        # Message
        message_label = QLabel(f"Your system has been running for {uptime_str}.\n\nIt's recommended to reboot your system regularly for optimal performance and security.")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {message_color};
                line-height: 1.4;
                margin-bottom: 20px;
            }}
        """)
        container_layout.addWidget(message_label)
        
        # Buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        # Reboot Now button
        reboot_btn = QPushButton("Reboot Now")
        reboot_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF3B30;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #CC2E24;
            }
            QPushButton:pressed {
                background-color: #A0241A;
            }
        """)
        reboot_btn.clicked.connect(self.reboot_now)
        button_layout.addWidget(reboot_btn)
        
        # Skip Reboot button
        skip_btn = QPushButton("Skip Reboot")
        skip_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0056CC;
            }
            QPushButton:pressed {
                background-color: #004299;
            }
        """)
        skip_btn.clicked.connect(self.skip_reboot)
        button_layout.addWidget(skip_btn)
        
        container_layout.addLayout(button_layout)
        
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        
        # Apply modern styling
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(0, 0, 0, 0.5);
            }
        """)
        
    def reboot_now(self):
        self.user_action = "reboot"
        self.accept()
        
    def skip_reboot(self):
        self.user_action = "skip"
        self.accept()
        
    def closeEvent(self, event):
        # Prevent closing without action
        event.ignore()
        
    def keyPressEvent(self, event):
        # Prevent closing with Escape key
        if event.key() == Qt.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)

class UptimeWatcher(QApplication):
    """Main application class"""
    
    def __init__(self):
        super().__init__(sys.argv)
        
        # Setup logging
        self.setup_logging()
        
        # Configuration
        if os.name == 'nt':
            self.config_file = Path(os.getenv('APPDATA')) / "UptimeWatcher" / "config.json"
        else:
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
        """Setup logging for the application"""
        if os.name == 'nt':
            log_dir = Path(os.getenv('APPDATA')) / "UptimeWatcher"
        else:
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
            "last_boot_time": 0,
            "total_delay_time": 0,
            "delay_start_time": 0
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
        
        # Test Dialog action (for demo purposes)
        test_action = QAction("Test Dialog", self)
        test_action.triggered.connect(self.test_dialog)
        tray_menu.addAction(test_action)
        
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
            self.config["total_delay_time"] = 0
            self.config["delay_start_time"] = 0
            
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
        
        dialog = ModernRebootDialog(None, uptime_str)
        dialog.exec()
        
        if dialog.user_action == "reboot":
            self.reboot_system()
        elif dialog.user_action == "skip":
            self.handle_delay_request(uptime_seconds)
        
        self.save_config()
        
    def handle_delay_request(self, uptime_seconds):
        """Handle delay request from user using modern dialog"""
        # Calculate total delay time so far
        if self.config["delay_start_time"] == 0:
            self.config["delay_start_time"] = time.time()
            self.config["total_delay_time"] = 0
        
        total_delay_hours = self.config["total_delay_time"] // 3600
        
        dialog = ModernDelayDialog(None, total_delay_hours)
        if dialog.exec() == QDialog.Accepted:
            delay_seconds = dialog.get_delay_seconds()
            self.config["ignore_until"] = time.time() + delay_seconds
            self.config["total_delay_time"] += delay_seconds
            logging.info(f"Reboot reminder delayed by {delay_seconds} seconds. Total delay: {self.config['total_delay_time']} seconds")
            
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
        if os.name == 'nt':
            log_file = Path(os.getenv('APPDATA')) / "UptimeWatcher" / "uptimewatcher.log"
        else:
            log_file = Path("/tmp/SelfCare/uptimewatcher.log")
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Settings")
        msg.setText("UptimeWatcher Settings")
        msg.setInformativeText(f"Config file: {self.config_file}\nLog file: {log_file}")
        msg.exec()
        
    def show_about(self):
        """Show about dialog"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("About UptimeWatcher")
        msg.setText("UptimeWatcher v1.0")
        msg.setInformativeText("A cross-platform system uptime monitor\n\nMonitors system uptime and reminds you to reboot after 24 hours.")
        msg.exec()
        
    def test_dialog(self):
        """Test the modern dialog (for demo purposes)"""
        # Test the reboot dialog
        uptime_seconds = int(time.time() - psutil.boot_time())
        self.show_reboot_reminder(uptime_seconds)
        
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
