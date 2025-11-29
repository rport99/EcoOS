#!/usr/bin/env python3

import os
import sys
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                            QVBoxLayout, QPushButton, QGridLayout, QLabel, QStyleFactory)
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import QSize, Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StormOS Utilities v6.1")
        self.setGeometry(100, 100, 700, 500)
        
        # Apply Fusion style
        self.setStyle(QStyleFactory.create('Fusion'))
        
        # Apply dark mode with Fusion styling
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2D2D30;
                color: #E0E0E0;
                font-size: 11px;
            }
            QTabWidget::pane {
                border: 1px solid #3F3F46;
                background-color: #252526;
            }
            QTabBar::tab {
                background-color: #3F3F46;
                color: #E0E0E0;
                padding: 4px 12px;
                border: 1px solid #555555;
                border-bottom: none;
                margin-right: 1px;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #007ACC;
                border-color: #007ACC;
            }
            QPushButton {
                background-color: #3F3F46;
                border: 1px solid #555555;
                color: #E0E0E0;
                padding: 4px 8px;
                border-radius: 3px;
                text-align: left;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #007ACC;
            }
            QPushButton:pressed {
                background-color: #007ACC;
            }
            QGridLayout {
                spacing: 5px;
            }
            QToolTip {
                background-color: #3F3F46;
                color: #E0E0E0;
                border: 1px solid #555555;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create tab widget with tabs on top
        self.notebook = QTabWidget()
        self.notebook.setTabPosition(QTabWidget.North)
        main_layout.addWidget(self.notebook)
        
        # Create all tabs
        self.create_maintenance_tab()
        self.create_game_utilities_tab()
        self.create_printer_tab()
        self.create_arch_university_tab()
        self.create_about_us_tab()
    
    def create_button_with_icon(self, label, command, icon_name=None):
        button = QPushButton(label)
        if icon_name:
            try:
                button.setIcon(QIcon.fromTheme(icon_name))
            except:
                pass
            button.setIconSize(QSize(16, 16))
        button.clicked.connect(lambda checked, cmd=command: self.run_command(cmd))
        
        # Add tooltips for better usability
        button.setToolTip(f"Execute: {command}")
        
        return button
    
    def run_command(self, command):
        if command.startswith('xdg-open') or command.startswith('https://'):
            subprocess.Popen(command, shell=True)
        else:
            if not command.startswith('xfce4-terminal') and not command.startswith('/'):
                command = f"xfce4-terminal -e '{command}'"
            subprocess.Popen(command, shell=True)
    
    def create_maintenance_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        
        commands = [
            ("Refresh Mirrors", "sudo reflector --verbose -l 20 --sort rate --save /etc/pacman.d/mirrorlist", "view-refresh"),
            ("System Updates", "sudo pacman -Syyu --noconfirm", "system-software-update"),
            ("Aur Updates", "yay -Syyu --noconfirm", "system-software-update"),
            ("Keyring Updater", "upkeyring", "system-lock-screen"),
            ("Renew Keyring", "upsystem", "system-lock-screen"),
            ("Install Teamviewer", "tinstall", "applications-internet"),
            ("Install Lshw", "sudo pacman -S lshw --noconfirm", "applications-system"),
            ("Install i2c-tools", "sudo pacman -S i2c-tools --noconfirm", "applications-system"),
            ("Nvidia Drivers", "sudo pacman -S nvidia-dkms lib32-nvidia-utils lib32-opencl-nvidia lib32-primus_vk lib32-libvdpau cuda-tools cuda opencl-nvidia primus_vk --noconfirm", "video-display"),
            ("Nvidia-390xx", "sudo pacman -S nvidia-390xx-dkms nvidia-390xx-utils opencl-nvidia-390xx --noconfirm", "video-display")
        ]
        
        for i, (label, command, icon_name) in enumerate(commands):
            button = self.create_button_with_icon(label, command, icon_name)
            layout.addWidget(button, i, 0)
        
        self.notebook.addTab(tab, "Maintenance")
    
    def create_game_utilities_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        
        commands = [
            ("Steam Native", "sudo pacman -S --noconfirm steam-native-runtime gamemode", "applications-games"),
            ("Heroic Launcher", "yay -S --noconfirm heroic-games-launcher-bin gamemode", "applications-games"),
            ("Lutris Launcher", "sudo pacman -S --noconfirm lutris gamemode", "applications-games"),
            ("ProtonGE Updater", "yay -S --noconfirm proton-community-updater", "applications-games"),
            ("Mangohud/Goverlay", "yay -S --noconfirm mangohud goverlay-bin", "applications-games"),
            ("Bottles Launcher", "yay -S --noconfirm bottles", "applications-games"),
            ("Warpinator", "sudo pacman -S warpinator --noconfirm", "applications-internet"),
            ("Calculator", "sudo pacman -S gnome-calculator --noconfirm", "accessories-calculator"),
            ("Flameshot", "sudo pacman -S flameshot --noconfirm", "accessories-screenshot"),
            ("Transmission", "sudo pacman -S transmission-gtk --noconfirm", "network-workgroup"),
            ("Thunderbird", "sudo pacman -S thunderbird --noconfirm", "internet-mail"),
            ("Xed Editor", "sudo pacman -S xed --noconfirm", "accessories-text-editor"),
            ("OnlyOffice", "yay -S onlyoffice-bin --noconfirm", "applications-office"),
            ("Media Stream", "minstaller", "multimedia-video-player"),
            ("Minimize Tray", "trayinjector", "system-run")
        ]
        
        for i, (label, command, icon_name) in enumerate(commands):
            button = self.create_button_with_icon(label, command, icon_name)
            layout.addWidget(button, i, 0)
        
        self.notebook.addTab(tab, "Games/Utils")
    
    def create_printer_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        
        commands = [
            ("Enable Cups", "systemctl enable --now cups", "printer"),
            ("Cups Web", "xdg-open http://localhost:631", "applications-internet"),
            ("Epson Drivers", "epsoninstaller", "printer"),
            ("HP Drivers", "eom", "printer")
        ]
        
        for i, (label, command, icon_name) in enumerate(commands):
            button = self.create_button_with_icon(label, command, icon_name)
            layout.addWidget(button, i, 0)
        
        self.notebook.addTab(tab, "Printers")
    
    def create_arch_university_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        
        commands = [
            ("Arch Commands", '/usr/local/bin/data/commands', "utilities-terminal"),
            ("Arch Wiki", "xdg-open https://wiki.archlinux.org/", "internet-web-browser"),
            ("Arch Website", "xdg-open https://archlinux.org/", "internet-web-browser"),
            ("Pacman Guide", "xdg-open https://wiki.archlinux.org/title/Pacman", "internet-web-browser"),
            ("AUR Website", "xdg-open https://aur.archlinux.org/", "internet-web-browser"),
            ("Pacman Tutorial", "xdg-open https://www.youtube.com/watch?v=TQaHfQrwnXo", "applications-multimedia"),
            ("Advanced Pacman", "xdg-open https://www.youtube.com/watch?v=-dEuXTMzRKs", "applications-multimedia")
        ]
        
        for i, (label, command, icon_name) in enumerate(commands):
            button = self.create_button_with_icon(label, command, icon_name)
            layout.addWidget(button, i, 0)
        
        self.add_left_buttons(layout, len(commands))
        
        self.notebook.addTab(tab, "Arch University")
    
    def create_about_us_tab(self):
        tab = QWidget()
        layout = QGridLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        
        commands = [
            ("Discord", "sudo pacman -S discord --noconfirm", "internet-chat"),
            ("Join Us", "xdg-open https://discord.gg/stormos", "internet-web-browser"),
            ("Distrowatch", "xdg-open https://distrowatch.com/stormos", "internet-web-browser"),
            ("Gofundme", "xdg-open https://gofund.me/stormos", "internet-web-browser"),
            ("Patreon", "xdg-open https://patreon.com/stormos", "internet-web-browser"),
            ("StormOS Site", "https://stormos.org", "internet-web-browser"),
            ("ReadMe", '/usr/local/bin/data/about', "text-x-generic")
        ]
        
        for i, (label, command, icon_name) in enumerate(commands):
            button = self.create_button_with_icon(label, command, icon_name)
            layout.addWidget(button, i, 0)
        
        self.notebook.addTab(tab, "About")
    
    def add_left_buttons(self, layout, start_index):
        buttons = [
            ("Logout", "xfce4-session-logout", "system-log-out"),
            ("System Info", "xfce4-terminal -H -x sudo lshw -short", "system-help"),
            ("System Resources", "xfce4-terminal -H -x top", "utilities-system-monitor"),
            ("Update Utility", "utilityup", "view-refresh"),
            ("Add/Remove Software", "/usr/bin/octopi %U", "system-software-install"),
            ("Add to Tray", "alltray -H sysconfig", "utilities-terminal")
        ]
        
        for i, (label, command, icon_name) in enumerate(buttons):
            button = self.create_button_with_icon(label, command, icon_name)
            layout.addWidget(button, start_index + i, 0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set Fusion style
    app.setStyle(QStyleFactory.create('Fusion'))
    
    # Set dark palette for Fusion style
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(45, 45, 48))
    palette.setColor(QPalette.WindowText, QColor(224, 224, 224))
    palette.setColor(QPalette.Base, QColor(37, 37, 38))
    palette.setColor(QPalette.AlternateBase, QColor(45, 45, 48))
    palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ToolTipText, QColor(224, 224, 224))
    palette.setColor(QPalette.Text, QColor(224, 224, 224))
    palette.setColor(QPalette.Button, QColor(63, 63, 70))
    palette.setColor(QPalette.ButtonText, QColor(224, 224, 224))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(0, 122, 204))
    palette.setColor(QPalette.Highlight, QColor(0, 122, 204))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())