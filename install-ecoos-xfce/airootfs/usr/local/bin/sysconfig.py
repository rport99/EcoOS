#!/usr/bin/env python3

import os
import sys
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                            QVBoxLayout, QPushButton, QGridLayout, QLabel, 
                            QStyleFactory, QHBoxLayout, QFrame, QTextEdit,
                            QSystemTrayIcon, QMenu, QAction, QMessageBox)
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont, QPixmap, QFontDatabase
from PyQt5.QtCore import QSize, Qt, QTimer, QRect
import webbrowser

class ModernButton(QPushButton):
    """Custom modern button with Tokyo Night styling"""
    def __init__(self, text, command, icon_name=None, parent=None):
        super().__init__(text, parent)
        self.command = command
        self.icon_name = icon_name
        
        # Set up button properties
        self.setMinimumHeight(35)
        self.setCursor(Qt.PointingHandCursor)
        
        # Try to set icon from theme
        if icon_name:
            icon = QIcon.fromTheme(icon_name)
            if not icon.isNull():
                self.setIcon(icon)
                self.setIconSize(QSize(18, 18))
        
        # Tooltip with command preview
        self.setToolTip(f"<b>{text}</b><br><code>{command}</code>")
        self.setToolTipDuration(3000)

class ModernLabel(QLabel):
    """Custom label with modern styling"""
    def __init__(self, text, size="normal", bold=False, parent=None):
        super().__init__(text, parent)
        
        if bold:
            font = QFont("Segoe UI" if sys.platform == "win32" else "Ubuntu", 10, QFont.Bold)
        else:
            font = QFont("Segoe UI" if sys.platform == "win32" else "Ubuntu", 9)
            
        if size == "large":
            font.setPointSize(12)
        elif size == "small":
            font.setPointSize(8)
            
        self.setFont(font)
        self.setStyleSheet("color: #a9b1d6;")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EcoOS Utilities v7.0")
        self.setGeometry(100, 100, 850, 600)
        
        # Set application icon
        self.setWindowIcon(QIcon.fromTheme("applications-system"))
        
        # Apply Fusion style
        self.setStyle(QStyleFactory.create('Fusion'))
        
        # Apply Tokyo Night theme
        self.apply_tokyo_night_theme()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)
        
        # Header section
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Create tab widget with modern styling
        self.notebook = QTabWidget()
        self.notebook.setTabPosition(QTabWidget.North)
        self.notebook.setDocumentMode(True)
        main_layout.addWidget(self.notebook)
        
        # Create status bar
        self.status_bar = self.create_status_bar()
        main_layout.addWidget(self.status_bar)
        
        # Create all tabs
        self.create_maintenance_tab()
        self.create_game_utilities_tab()
        self.create_printer_tab()
        self.create_arch_university_tab()
        self.create_about_us_tab()
        self.create_system_info_tab()  # New tab
        
        # Setup system tray
        self.setup_system_tray()
        
    def apply_tokyo_night_theme(self):
        """Apply Tokyo Night color scheme"""
        self.setStyleSheet("""
            /* Main Window */
            QMainWindow, QWidget {
                background-color: #1a1b26;
                color: #c0caf5;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
                font-size: 10pt;
                border: none;
            }
            
            /* Tab Widget */
            QTabWidget::pane {
                border: 1px solid #414868;
                background-color: #1a1b26;
                border-radius: 6px;
                margin-top: 4px;
            }
            
            QTabBar::tab {
                background-color: #24283b;
                color: #787c99;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border: 1px solid #414868;
                border-bottom: none;
                min-width: 100px;
                font-weight: 500;
            }
            
            QTabBar::tab:selected {
                background-color: #1a1b26;
                color: #7aa2f7;
                border-color: #7aa2f7;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #292e42;
                color: #c0caf5;
            }
            
            /* Buttons */
            ModernButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #292e42, stop: 1 #24283b);
                border: 1px solid #414868;
                color: #c0caf5;
                padding: 8px 12px;
                border-radius: 6px;
                text-align: left;
                font-weight: 500;
                min-height: 35px;
            }
            
            ModernButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #364a82, stop: 1 #292e42);
                border-color: #7aa2f7;
                color: #ffffff;
            }
            
            ModernButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #24283b, stop: 1 #292e42);
            }
            
            ModernButton:focus {
                border: 2px solid #7aa2f7;
                padding: 7px 11px;
            }
            
            /* Tool Tips */
            QToolTip {
                background-color: #24283b;
                color: #c0caf5;
                border: 1px solid #414868;
                border-radius: 4px;
                padding: 6px;
                font-size: 9pt;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #24283b;
                color: #787c99;
                border-top: 1px solid #414868;
                padding: 4px;
            }
            
            /* Separator */
            QFrame[frameShape="4"] {
                background-color: #414868;
                max-height: 1px;
                min-height: 1px;
            }
            
            /* Text Edit */
            QTextEdit {
                background-color: #24283b;
                color: #c0caf5;
                border: 1px solid #414868;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Monospace', 'Consolas', 'Ubuntu Mono';
                font-size: 9pt;
            }
            
            /* Scroll Bars */
            QScrollBar:vertical {
                border: none;
                background: #24283b;
                width: 10px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: #414868;
                min-height: 20px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #565f89;
            }
            
            /* Group Box */
            QGroupBox {
                border: 1px solid #414868;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
                font-weight: bold;
                color: #7aa2f7;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def create_header(self):
        """Create modern header with title and quick actions"""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        # Title section
        title_layout = QVBoxLayout()
        title = ModernLabel("⚡ EcoOS Utilities v7.0", "large", True)
        subtitle = ModernLabel("Tokyo Night Edition • Arch Linux Management Suite", "small")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Quick action buttons
        quick_actions = [
            ("Update All", "sudo pacman -Syyu && yay -Syyu --noconfirm", "view-refresh"),
            ("System Info", "inxi -Fxxxz", "dialog-information"),
            ("Open Terminal", "xfce4-terminal", "utilities-terminal")
        ]
        
        for text, cmd, icon in quick_actions:
            btn = ModernButton(text, cmd, icon)
            btn.setMaximumWidth(120)
            btn.clicked.connect(lambda checked, c=cmd: self.run_command(c))
            header_layout.addWidget(btn)
        
        return header_frame
    
    def create_status_bar(self):
        """Create modern status bar"""
        status_frame = QFrame()
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(8, 4, 8, 4)
        
        # Status label
        self.status_label = ModernLabel("Ready", "small")
        status_layout.addWidget(self.status_label)
        
        # Spacer
        status_layout.addStretch()
        
        # System info labels
        self.time_label = ModernLabel("", "small")
        status_layout.addWidget(self.time_label)
        
        # Update timer for status bar
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_status_bar)
        self.update_timer.start(1000)
        
        return status_frame
    
    def update_status_bar(self):
        """Update status bar information"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(f"🕒 {current_time}")
    
    def setup_system_tray(self):
        """Setup system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("applications-system"))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        update_action = QAction("Check Updates", self)
        update_action.triggered.connect(lambda: self.run_command("sudo pacman -Syy"))
        tray_menu.addAction(update_action)
        
        terminal_action = QAction("Open Terminal", self)
        terminal_action.triggered.connect(lambda: self.run_command("xfce4-terminal"))
        tray_menu.addAction(terminal_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def run_command(self, command):
        """Execute command with proper handling"""
        self.status_label.setText(f"Executing: {command[:50]}...")
        
        try:
            if command.startswith('xdg-open') or command.startswith('https://'):
                # Handle URLs and file openings
                if command.startswith('https://'):
                    webbrowser.open(command)
                else:
                    subprocess.Popen(command, shell=True)
            elif command.startswith('/') and os.path.exists(command.split()[0]):
                # Handle local file execution
                subprocess.Popen(command, shell=True)
            else:
                # Open terminal for commands
                terminal_cmd = f"xfce4-terminal --geometry=120x30 -e 'bash -c \"{command}; echo -e \\\"\\n\\nPress Enter to exit...\\\"; read\"'"
                subprocess.Popen(terminal_cmd, shell=True)
            
            QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)[:50]}")
            QMessageBox.warning(self, "Command Error", f"Failed to execute command:\n{str(e)}")
    
    def create_maintenance_tab(self):
        """Create system maintenance tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Section title
        title = ModernLabel("🛠️ System Maintenance & Updates", "large", True)
        layout.addWidget(title)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)
        
        # Buttons grid
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        
        commands = [
            ("🔄 Refresh Mirrors", "sudo reflector --latest 20 --protocol https --sort rate --save /etc/pacman.d/mirrorlist", "view-refresh"),
            ("📦 System Updates", "sudo pacman -Syyu --noconfirm", "system-software-update"),
            ("🌟 AUR Updates", "yay -Syyu --noconfirm", "system-software-update"),
            ("🔑 Update Keyring", "sudo pacman -Sy archlinux-keyring && sudo pacman-key --populate", "system-lock-screen"),
            ("🔧 Full System Update", "sudo pacman -Syu && yay -Syu", "system-run"),
            
            ("📊 Install HW Tools", "sudo pacman -S lshw inxi htop --noconfirm", "applications-system"),
            ("🔌 Install i2c Tools", "sudo pacman -S i2c-tools lm_sensors --noconfirm", "applications-system"),
            ("🎮 Install TeamViewer", "yay -S teamviewer --noconfirm", "applications-internet"),
            ("🎨 Nvidia Drivers", "sudo pacman -S nvidia nvidia-utils lib32-nvidia-utils nvidia-settings --noconfirm", "video-display"),
            ("🎨 Nvidia 390xx (Legacy)", "sudo pacman -S nvidia-390xx-dkms nvidia-390xx-utils --noconfirm", "video-display"),
            
            ("🧹 Clean Package Cache", "sudo pacman -Sc --noconfirm", "edit-clear"),
            ("🗑️ Remove Orphans", "sudo pacman -Rns $(pacman -Qtdq) --noconfirm 2>/dev/null || echo 'No orphans'", "user-trash"),
            ("📈 View System Info", "inxi -Fxxxz", "dialog-information"),
            ("🔍 Check Disk Usage", "df -h", "drive-harddisk"),
            ("📊 Memory Info", "free -h", "media-memory"),
            ("🌐 Network Info", "ip addr show", "network-wired")
        ]
        
        for i, (label, command, icon_name) in enumerate(commands):
            btn = ModernButton(label, command, icon_name)
            grid.addWidget(btn, i // 3, i % 3)
        
        layout.addLayout(grid)
        self.notebook.addTab(tab, "🔧 Maintenance")
    
    def create_game_utilities_tab(self):
        """Create gaming and utilities tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        title = ModernLabel("🎮 Gaming & Utilities", "large", True)
        layout.addWidget(title)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)
        
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        
        commands = [
            ("🎮 Steam Native", "sudo pacman -S steam-native-runtime gamemode --noconfirm", "applications-games"),
            ("🏆 Heroic Launcher", "yay -S heroic-games-launcher-bin --noconfirm", "applications-games"),
            ("⚔️ Lutris", "sudo pacman -S lutris gamemode --noconfirm", "applications-games"),
            ("🔧 ProtonGE", "yay -S protonup-qt --noconfirm", "applications-games"),
            ("📊 MangoHud", "yay -S mangohud goverlay --noconfirm", "applications-games"),
            ("🍾 Bottles", "yay -S bottles --noconfirm", "applications-games"),
            
            ("📁 Warpinator", "sudo pacman -S warpinator --noconfirm", "applications-internet"),
            ("🖼️ Flameshot", "sudo pacman -S flameshot --noconfirm", "accessories-screenshot"),
            ("🧮 Calculator", "sudo pacman -S gnome-calculator --noconfirm", "accessories-calculator"),
            ("📨 Thunderbird", "sudo pacman -S thunderbird --noconfirm", "internet-mail"),
            ("📝 OnlyOffice", "yay -S onlyoffice-bin --noconfirm", "applications-office"),
            ("🎵 Media Players", "sudo pacman -S vlc celluloid rhythmbox --noconfirm", "multimedia-video-player"),
            
            ("🔗 Transmission", "sudo pacman -S transmission-gtk --noconfirm", "network-workgroup"),
            ("✏️ Xed Editor", "sudo pacman -S xed --noconfirm", "accessories-text-editor"),
            ("📦 Flatpak", "sudo pacman -S flatpak --noconfirm", "system-software-install"),
            ("🐳 Docker", "sudo pacman -S docker docker-compose --noconfirm", "applications-system"),
            ("📚 VS Code", "yay -S visual-studio-code-bin --noconfirm", "applications-development"),
            ("🐍 Python Tools", "sudo pacman -S python-pip python-virtualenv --noconfirm", "applications-development")
        ]
        
        for i, (label, command, icon_name) in enumerate(commands):
            btn = ModernButton(label, command, icon_name)
            grid.addWidget(btn, i // 3, i % 3)
        
        layout.addLayout(grid)
        self.notebook.addTab(tab, "🎮 Games/Utils")
    
    def create_printer_tab(self):
        """Create printer utilities tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        title = ModernLabel("🖨️ Printer Configuration", "large", True)
        layout.addWidget(title)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)
        
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        
        commands = [
            ("🔄 Enable CUPS", "sudo systemctl enable --now cups", "printer"),
            ("🌐 CUPS Web Interface", "xdg-open http://localhost:631", "applications-internet"),
            ("🖨️ Install Epson", "sudo pacman -S epson-inkjet-printer-escpr --noconfirm", "printer"),
            ("🖨️ Install HP", "sudo pacman -S hplip --noconfirm", "printer"),
            ("🖨️ Install Canon", "yay -S cndrvcups-lb --noconfirm", "printer"),
            ("📄 Generic Drivers", "sudo pacman -S cups-pdf gutenprint --noconfirm", "printer"),
            
            ("🔍 Detect Printers", "lpinfo -v", "system-search"),
            ("📋 List Printers", "lpstat -p -d", "view-list"),
            ("⚙️ Printer Test", "lp -d $(lpstat -d | cut -d' ' -f3) /etc/nsswitch.conf", "system-run"),
            ("🗑️ Remove Printer", "lpadmin -x $(lpstat -p | grep printer | cut -d' ' -f2)", "edit-delete")
        ]
        
        for i, (label, command, icon_name) in enumerate(commands):
            btn = ModernButton(label, command, icon_name)
            grid.addWidget(btn, i // 3, i % 3)
        
        layout.addLayout(grid)
        self.notebook.addTab(tab, "🖨️ Printers")
    
    def create_arch_university_tab(self):
        """Create Arch Linux learning tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        title = ModernLabel("📚 Arch Linux University", "large", True)
        layout.addWidget(title)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)
        
        # Quick links section
        links_label = ModernLabel("Quick Links & Resources:", "normal", True)
        layout.addWidget(links_label)
        
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        
        commands = [
            ("📖 Arch Wiki", "https://wiki.archlinux.org/", "internet-web-browser"),
            ("🌐 Arch Website", "https://archlinux.org/", "internet-web-browser"),
            ("📦 AUR Portal", "https://aur.archlinux.org/", "internet-web-browser"),
            ("🐧 Arch News", "https://archlinux.org/news/", "internet-web-browser"),
            
            ("📚 Pacman Guide", "https://wiki.archlinux.org/title/Pacman", "internet-web-browser"),
            ("🔧 Systemd Guide", "https://wiki.archlinux.org/title/Systemd", "internet-web-browser"),
            ("🛡️ Security Guide", "https://wiki.archlinux.org/title/Security", "internet-web-browser"),
            ("🔐 SSH Guide", "https://wiki.archlinux.org/title/SSH_keys", "internet-web-browser"),
            
            ("🎥 Pacman Tutorial", "https://www.youtube.com/watch?v=TQaHfQrwnXo", "applications-multimedia"),
            ("🎥 Advanced Pacman", "https://www.youtube.com/watch?v=-dEuXTMzRKs", "applications-multimedia"),
            ("🎥 Arch Install Guide", "https://www.youtube.com/watch?v=PQgWpGVwpE8", "applications-multimedia"),
            ("🎥 System Maintenance", "https://www.youtube.com/watch?v=2i1GQ8q1Y1o", "applications-multimedia"),
            
            ("💬 Arch Forums", "https://bbs.archlinux.org/", "internet-web-browser"),
            ("💭 Arch Subreddit", "https://reddit.com/r/archlinux", "internet-web-browser"),
            ("📝 Arch Tips", "https://wiki.archlinux.org/title/General_recommendations", "internet-web-browser"),
            ("🐛 Arch Bugs", "https://bugs.archlinux.org/", "internet-web-browser")
        ]
        
        for i, (label, command, icon_name) in enumerate(commands):
            btn = ModernButton(label, command, icon_name)
            grid.addWidget(btn, i // 4, i % 4)
        
        layout.addLayout(grid)
        self.notebook.addTab(tab, "📚 Arch University")
    
    def create_about_us_tab(self):
        """Create about/community tab with updated links"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        title = ModernLabel("🌟 EcoOS Community & Support", "large", True)
        layout.addWidget(title)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)
        
        # Community section
        community_label = ModernLabel("Join Our Community:", "normal", True)
        layout.addWidget(community_label)
        
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        
        commands = [
            ("💬 Discord Server", "https://discord.gg/stormos", "internet-chat"),
            ("📱 Install Discord", "sudo pacman -S discord --noconfirm", "internet-chat"),
            ("🌐 Official Website", "https://stormos.org", "internet-web-browser"),
            ("⭐ GitHub", "https://github.com/stormos-linux", "internet-web-browser"),
            
            ("📊 DistroWatch", "https://distrowatch.com/stormos", "internet-web-browser"),
            ("💖 Patreon", "https://patreon.com/stormos", "internet-web-browser"),
            ("💰 OpenCollective", "https://opencollective.com/stormos", "internet-web-browser"),
            ("☕ Buy Me a Coffee", "https://buymeacoffee.com/stormos", "internet-web-browser"),
            
            ("📧 Email List", "https://stormos.org/newsletter", "mail-message"),
            ("🐦 Twitter/X", "https://twitter.com/storm_os", "internet-web-browser"),
            ("📘 Facebook", "https://facebook.com/stormoslinux", "internet-web-browser"),
            ("📷 Instagram", "https://instagram.com/stormoslinux", "internet-web-browser"),
            
            ("📚 Documentation", "https://docs.stormos.org", "help-contents"),
            ("🐛 Issue Tracker", "https://github.com/stormos-linux/issues", "tools-report-bug"),
            ("💡 Feature Requests", "https://github.com/stormos-linux/ideas", "dialog-question"),
            ("🤝 Contributor Guide", "https://github.com/stormos-linux/contributing", "system-users")
        ]
        
        for i, (label, command, icon_name) in enumerate(commands):
            btn = ModernButton(label, command, icon_name)
            grid.addWidget(btn, i // 4, i % 4)
        
        layout.addLayout(grid)
        
        # Credits section
        credits_frame = QFrame()
        credits_layout = QVBoxLayout(credits_frame)
        credits_layout.setContentsMargins(10, 10, 10, 10)
        
        credits_label = ModernLabel("Credits & License:", "normal", True)
        credits_layout.addWidget(credits_label)
        
        credits_text = ModernLabel(
            "EcoOS Utilities v7.0 • Tokyo Night Theme\n"
            "© 2024 EcoOS Team • MIT License\n"
            "Arch Linux is an independently developed distribution\n"
            "Icons: Papirus Icon Theme • Fonts: JetBrains Mono",
            "small"
        )
        credits_layout.addWidget(credits_text)
        
        layout.addWidget(credits_frame)
        self.notebook.addTab(tab, "🌟 About")
    
    def create_system_info_tab(self):
        """New tab for system information"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        title = ModernLabel("💻 System Information & Tools", "large", True)
        layout.addWidget(title)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)
        
        # System info display
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(150)
        layout.addWidget(ModernLabel("System Overview:", "normal", True))
        layout.addWidget(info_text)
        
        # Update system info button
        info_btn = ModernButton("🔄 Refresh System Info", "inxi -Fxxxz", "view-refresh")
        info_btn.clicked.connect(lambda: self.update_system_info(info_text))
        layout.addWidget(info_btn)
        
        # Quick tools section
        tools_label = ModernLabel("Quick System Tools:", "normal", True)
        layout.addWidget(tools_label)
        
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        
        tools = [
            ("📊 System Monitor", "xfce4-taskmanager", "utilities-system-monitor"),
            ("💾 Disk Usage", "baobab", "drive-harddisk"),
            ("🌐 Network", "nm-connection-editor", "network-wired"),
            ("🎨 Display", "nvidia-settings", "video-display"),
            
            ("⚙️ Services", "systemctl --type=service", "applications-system"),
            ("📦 Packages", "pacman -Q | wc -l", "system-software-install"),
            ("🔍 Find File", "locate", "system-search"),
            ("📈 Process Viewer", "htop", "utilities-system-monitor"),
            
            ("🗑️ Cache Cleaner", "sudo pacman -Sc", "edit-clear"),
            ("🔧 Log Viewer", "journalctl -xe", "text-x-log"),
            ("📝 Boot Info", "systemd-analyze", "system-run"),
            ("🛡️ Firewall", "sudo ufw status verbose", "network-firewall")
        ]
        
        for i, (label, command, icon_name) in enumerate(tools):
            btn = ModernButton(label, command, icon_name)
            grid.addWidget(btn, i // 4, i % 4)
        
        layout.addLayout(grid)
        self.notebook.addTab(tab, "💻 System Info")
    
    def update_system_info(self, text_widget):
        """Update system information display"""
        try:
            import platform
            import psutil
            
            info = []
            info.append(f"System: {platform.system()} {platform.release()}")
            info.append(f"Node: {platform.node()}")
            info.append(f"Architecture: {platform.machine()}")
            info.append(f"Processor: {platform.processor()}")
            
            # CPU info
            cpu_freq = psutil.cpu_freq()
            info.append(f"CPU: {psutil.cpu_count()} cores @ {cpu_freq.current:.0f}MHz")
            
            # Memory info
            mem = psutil.virtual_memory()
            info.append(f"Memory: {mem.used//1024**2}MB / {mem.total//1024**2}MB ({mem.percent}%)")
            
            # Disk info
            disk = psutil.disk_usage('/')
            info.append(f"Disk: {disk.used//1024**3}GB / {disk.total//1024**3}GB ({disk.percent}%)")
            
            text_widget.setText('\n'.join(info))
            self.status_label.setText("System info updated")
            
        except ImportError:
            text_widget.setText("Install psutil for detailed system info:\nsudo pacman -S python-psutil")
            self.status_label.setText("Missing psutil package")
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self, 'Confirm Exit',
            'Do you want to keep running in system tray?',
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "EcoOS Utilities",
                "Running in system tray",
                QSystemTrayIcon.Information,
                2000
            )
        elif reply == QMessageBox.No:
            self.tray_icon.hide()
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application name and organization
    app.setApplicationName("EcoOS Utilities")
    app.setOrganizationName("EcoOS")
    app.setApplicationVersion("7.0")
    
    # Set Fusion style
    app.setStyle(QStyleFactory.create('Fusion'))
    
    # Set Tokyo Night palette
    palette = QPalette()
    
    # Base colors from Tokyo Night palette
    palette.setColor(QPalette.Window, QColor(0x1a, 0x1b, 0x26))
    palette.setColor(QPalette.WindowText, QColor(0xc0, 0xca, 0xf5))
    palette.setColor(QPalette.Base, QColor(0x24, 0x28, 0x3b))
    palette.setColor(QPalette.AlternateBase, QColor(0x1a, 0x1b, 0x26))
    palette.setColor(QPalette.ToolTipBase, QColor(0x24, 0x28, 0x3b))
    palette.setColor(QPalette.ToolTipText, QColor(0xc0, 0xca, 0xf5))
    palette.setColor(QPalette.Text, QColor(0xc0, 0xca, 0xf5))
    palette.setColor(QPalette.Button, QColor(0x29, 0x2e, 0x42))
    palette.setColor(QPalette.ButtonText, QColor(0xc0, 0xca, 0xf5))
    palette.setColor(QPalette.BrightText, QColor(0xff, 0x9e, 0x64))
    palette.setColor(QPalette.Link, QColor(0x7a, 0xa2, 0xf7))
    palette.setColor(QPalette.Highlight, QColor(0x7a, 0xa2, 0xf7))
    palette.setColor(QPalette.HighlightedText, QColor(0x1a, 0x1b, 0x26))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(0x54, 0x58, 0x6e))
    
    app.setPalette(palette)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())