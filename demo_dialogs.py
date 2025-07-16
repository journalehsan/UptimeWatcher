#!/usr/bin/env python3
"""
Demo script to showcase the modern dialogs
"""

import sys
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt
from main import ModernRebootDialog, ModernDelayDialog
import darkdetect

class DemoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dialog Demo")
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Modern Dialog Demo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Dark mode indicator
        dark_mode_text = "🌙 Dark Mode" if darkdetect.isDark() else "☀️ Light Mode"
        mode_label = QLabel(f"Current: {dark_mode_text}")
        mode_label.setAlignment(Qt.AlignCenter)
        mode_label.setStyleSheet("font-size: 12px; color: #666; margin-bottom: 10px;")
        layout.addWidget(mode_label)
        
        # Reboot Dialog Button
        reboot_btn = QPushButton("Show Reboot Dialog")
        reboot_btn.clicked.connect(self.show_reboot_dialog)
        layout.addWidget(reboot_btn)
        
        # Delay Dialog Button (0 hours delayed)
        delay_btn1 = QPushButton("Show Delay Dialog (0 hours)")
        delay_btn1.clicked.connect(lambda: self.show_delay_dialog(0))
        layout.addWidget(delay_btn1)
        
        # Delay Dialog Button (25 hours delayed)
        delay_btn2 = QPushButton("Show Delay Dialog (25 hours)")
        delay_btn2.clicked.connect(lambda: self.show_delay_dialog(25))
        layout.addWidget(delay_btn2)
        
        # Delay Dialog Button (48+ hours delayed)
        delay_btn3 = QPushButton("Show Delay Dialog (48+ hours)")
        delay_btn3.clicked.connect(lambda: self.show_delay_dialog(49))
        layout.addWidget(delay_btn3)
        
        self.setLayout(layout)
        
    def show_reboot_dialog(self):
        dialog = ModernRebootDialog(None, "2d 5h 30m")
        result = dialog.exec()
        print(f"Reboot dialog result: {dialog.user_action}")
        
    def show_delay_dialog(self, hours):
        dialog = ModernDelayDialog(None, hours)
        result = dialog.exec()
        if result:
            print(f"Delay selected: {dialog.get_delay_seconds()} seconds")
        else:
            print("Delay dialog cancelled")

def main():
    app = QApplication(sys.argv)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
