#!/bin/bash -e
#
##############################################################################
#  PostInstall - EcoOS/StormOS setup script
#  Licensed under GPLv3 or later
##############################################################################

# Setup logging first
LOG_FILE="/var/log/stormos-postinstall.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "=================================================="
echo "EcoOS/StormOS Post-Installation Setup - $(date)"
echo "=================================================="

# Function to show progress
show_progress() {
    echo "→ $1"
}

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: This script must be run as root" >&2
    exit 1
fi

# Detect if we're in Calamares installation context
show_progress "Detecting installation context..."
if mount | grep -q "on /tmp/calamares-root" && [ -d "/tmp/calamares-root" ]; then
    TARGET_ROOT="/tmp/calamares-root"
    echo "✓ Running in Calamares installation context"
    IS_CALAMARES=true
else
    TARGET_ROOT=""
    echo "✓ Running in live system context"
    IS_CALAMARES=false
fi

# Only remove calamares.desktop in live system mode (not during Calamares installation)
if [ "$IS_CALAMARES" = false ]; then
    # Get the actual logged-in user (only works in live system)
    if command -v logname &>/dev/null; then
        USER_NAME=$(logname 2>/dev/null || echo "user")
    else
        USER_NAME="user"
    fi
    rm -f "/home/$USER_NAME/Desktop/calamares.desktop" 2>/dev/null || true
    echo "✓ Removed calamares.desktop from live system"
fi

# We only need user setup in Calamares mode
if [ "$IS_CALAMARES" = true ]; then
    show_progress "Finding target system user..."

    if [ -f "$TARGET_ROOT/etc/passwd" ]; then
        USER_NAME=$(awk -F: '$3 >= 1000 && $3 < 65000 && $1 != "nobody" {print $1; exit}' "$TARGET_ROOT/etc/passwd")
    fi

    if [ -z "$USER_NAME" ]; then
        # Fallback: check /home
        if [ -d "$TARGET_ROOT/home" ]; then
            USER_NAME=$(ls "$TARGET_ROOT/home" | grep -v "lost+found" | head -n1)
        fi
    fi

    if [ -z "$USER_NAME" ]; then
        USER_NAME="user"
        echo "⚠ No user found; using default username: $USER_NAME"
    else
        echo "✓ Found target user: $USER_NAME"
    fi

    USER_HOME="$TARGET_ROOT/home/$USER_NAME"
    mkdir -p "$USER_HOME"

else
    USER_NAME=""
    USER_HOME=""
    show_progress "Skipping user setup in live system."
fi

# === USER-SPECIFIC SETUP: ONLY IN CALAMARES ===
if [ "$IS_CALAMARES" = true ]; then
    show_progress "Creating standard user directories..."

    mkdir -p "$USER_HOME/Desktop"
    mkdir -p "$USER_HOME/Documents"
    mkdir -p "$USER_HOME/Downloads"
    mkdir -p "$USER_HOME/Music"
    mkdir -p "$USER_HOME/Pictures"
    mkdir -p "$USER_HOME/Public"
    mkdir -p "$USER_HOME/Templates"
    mkdir -p "$USER_HOME/Videos"

    echo "✓ Created standard user directories"

    # Create XDG config
    show_progress "Creating XDG configuration..."
    mkdir -p "$USER_HOME/.config"

    cat > "$USER_HOME/.config/user-dirs.dirs" << 'EOF'
XDG_DESKTOP_DIR="$HOME/Desktop"
XDG_DOWNLOAD_DIR="$HOME/Downloads"
XDG_TEMPLATES_DIR="$HOME/Templates"
XDG_PUBLICSHARE_DIR="$HOME/Public"
XDG_DOCUMENTS_DIR="$HOME/Documents"
XDG_MUSIC_DIR="$HOME/Music"
XDG_PICTURES_DIR="$HOME/Pictures"
XDG_VIDEOS_DIR="$HOME/Videos"
EOF

    cat > "$USER_HOME/.config/user-dirs.locale" << 'EOF'
en_US
EOF
    echo "✓ XDG configuration created"

    # Copy skel (if exists)
    show_progress "Copying skel configurations..."
    if [ -d "/etc/skel" ]; then
        rsync -a /etc/skel/ "$USER_HOME/" 2>/dev/null || true
        echo "✓ Copied skel configurations"
    else
        echo "⚠ /etc/skel not found, skipping"
    fi

    # Create basic .bashrc if missing
    if [ ! -f "$USER_HOME/.bashrc" ]; then
        cat > "$USER_HOME/.bashrc" << 'EOF'
# EcoOS/StormOS Bash Configuration
export EDITOR=nvim
export VISUAL=nvim

# Color support
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# Aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias update='sudo pacman -Syu'
alias upgrade='sudo pacman -Syu'
alias clean='sudo pacman -Scc'
alias install='sudo pacman -S'
alias remove='sudo pacman -Rns'
alias search='pacman -Ss'
alias orphans='pacman -Qtdq'
alias rmorphans='sudo pacman -Rns $(pacman -Qtdq)'
alias aur='yay'

# Source aliases if exists
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# History settings
HISTCONTROL=ignoreboth
HISTSIZE=1000
HISTFILESIZE=2000
shopt -s histappend
shopt -s checkwinsize

# Prompt
PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '

# Welcome message
echo "Welcome to EcoOS/StormOS!"
echo "System: $(uname -srm)"
echo "Date: $(date)"
echo ""
EOF
        echo "✓ Created enhanced .bashrc"
    else
        echo "✓ .bashrc already exists"
    fi

    # Set ownership
    show_progress "Setting proper ownership..."
    USER_UID=$(awk -F: -v user="$USER_NAME" '$1 == user {print $3}' "$TARGET_ROOT/etc/passwd")
    USER_GID=$(awk -F: -v user="$USER_NAME" '$1 == user {print $4}' "$TARGET_ROOT/etc/passwd")
    chown -R "${USER_UID:-1000}:${USER_GID:-1000}" "$USER_HOME" 2>/dev/null || true
    chmod 755 "$USER_HOME" 2>/dev/null || true
    echo "✓ Set ownership and permissions"
    
    # === PAMAC INSTALLATION ===
    show_progress "Installing pamac package manager..."
    
    # Function to install pamac
    install_pamac() {
        echo "=== Installing pamac package manager ==="
        
        # First, update package databases
        echo "Updating package databases..."
        pacman -Sy --noconfirm
        
        # Try to install from available repositories
        echo "Looking for pamac in repositories..."
        
        # Check various repositories for pamac
        if pacman -Sl stormos 2>/dev/null | grep -q "pamac "; then
            echo "Installing pamac from stormos repository..."
            pacman -S --noconfirm --needed pamac
        elif pacman -Sl extra 2>/dev/null | grep -q "pamac "; then
            echo "Installing pamac from extra repository..."
            pacman -S --noconfirm --needed pamac
        elif pacman -Sl community 2>/dev/null | grep -q "pamac "; then
            echo "Installing pamac from community repository..."
            pacman -S --noconfirm --needed pamac
        else
            # Try to install whatever pamac package is available
            echo "Installing pamac (any available version)..."
            pacman -S --noconfirm pamac 2>/dev/null || {
                echo "Standard pamac not available, trying alternative..."
                pacman -S --noconfirm pamac-aur 2>/dev/null || \
                pacman -S --noconfirm pamac-gtk 2>/dev/null || \
                echo "⚠ Could not find pamac in repositories"
            }
        fi
        
        # Verify pamac installation
        if pacman -Q pamac 2>/dev/null || pacman -Q pamac-aur 2>/dev/null || pacman -Q pamac-gtk 2>/dev/null; then
            echo "✓ pamac package installed successfully"
            
            # Enable pamac-tray autostart if it exists
            if [ -f /etc/xdg/autostart/org.manjaro.pamac-tray.desktop ]; then
                mkdir -p /home/$USER_NAME/.config/autostart
                cp /etc/xdg/autostart/org.manjaro.pamac-tray.desktop /home/$USER_NAME/.config/autostart/
                chown $USER_NAME:$USER_NAME /home/$USER_NAME/.config/autostart/org.manjaro.pamac-tray.desktop
                echo "✓ pamac-tray autostart configured"
            fi
        else
            echo "⚠ pamac installation may have failed"
        fi
        
        echo "=== pamac installation completed ==="
    }
    
    # Run pamac installation inside chroot
    arch-chroot "$TARGET_ROOT" bash -c "$(declare -f install_pamac); install_pamac" 2>&1 | tee -a "$LOG_FILE"
    
    # === YAY INSTALLATION (AFTER PAMAC) ===
    show_progress "Installing yay AUR helper (after pamac)..."
    
    # Function to install yay
    install_yay() {
        echo "=== Installing yay AUR helper ==="
        
        # First, ensure we have internet connectivity
        echo "Checking internet connectivity..."
        if ! ping -c 1 -W 2 archlinux.org &>/dev/null; then
            echo "⚠ No internet connection detected. yay installation may fail."
        fi
        
        # Install required dependencies (should already be there from pamac, but ensure)
        echo "Installing/verifying dependencies..."
        pacman -S --noconfirm --needed git base-devel go 2>/dev/null || true
        
        # Check if dependencies are installed
        if ! command -v git &>/dev/null; then
            echo "ERROR: git not installed!"
            return 1
        fi
        
        if ! command -v go &>/dev/null; then
            echo "ERROR: Go not installed!"
            return 1
        fi
        
        echo "Dependencies:"
        echo "  git: $(git --version)"
        echo "  go: $(go version)"
        
        # Check for libalpm.so.16 vs .so.15
        echo "Checking libalpm version..."
        if [ -f /usr/lib/libalpm.so.16 ]; then
            echo "Found libalpm.so.16"
            # Check if we need compatibility symlink
            if [ ! -f /usr/lib/libalpm.so.15 ] && [ ! -L /usr/lib/libalpm.so.15 ]; then
                echo "Creating temporary libalpm.so.15 symlink for yay compilation..."
                ln -sf /usr/lib/libalpm.so.16 /usr/lib/libalpm.so.15
                CREATED_SYMLINK=true
            else
                CREATED_SYMLINK=false
            fi
        elif [ -f /usr/lib/libalpm.so.15 ]; then
            echo "Found libalpm.so.15"
            CREATED_SYMLINK=false
        else
            echo "⚠ No libalpm.so files found"
            CREATED_SYMLINK=false
        fi
        
        # Clone and build yay
        echo "Cloning yay repository..."
        cd /tmp
        rm -rf yay-build 2>/dev/null || true
        
        # Try with timeout in case network is slow
        timeout 60 git clone https://github.com/Jguer/yay.git yay-build
        
        if [ ! -d "yay-build" ]; then
            echo "⚠ git clone failed, trying alternative method..."
            # Try alternative: download release binary
            curl -L -o yay.tar.gz https://github.com/Jguer/yay/releases/latest/download/yay_linux_x86_64.tar.gz 2>/dev/null || \
            wget -O yay.tar.gz https://github.com/Jguer/yay/releases/latest/download/yay_linux_x86_64.tar.gz 2>/dev/null
            
            if [ -f "yay.tar.gz" ]; then
                tar -xzf yay.tar.gz
                mv yay_linux_x86_64/yay /usr/local/bin/
                chmod +x /usr/local/bin/yay
                rm -rf yay_linux_x86_64 yay.tar.gz
                echo "✓ yay installed from binary release"
                return 0
            else
                echo "✗ Could not download yay"
                return 1
            fi
        fi
        
        cd yay-build
        
        echo "Building yay..."
        # Build with verbose output
        make
        
        echo "Installing yay..."
        sudo make install
        
        # Clean up
        cd /
        rm -rf /tmp/yay-build
        
        # Remove symlink if we created it
        if [ "$CREATED_SYMLINK" = true ] && [ -L /usr/lib/libalpm.so.15 ]; then
            rm -f /usr/lib/libalpm.so.15
            echo "Removed temporary libalpm symlink"
        fi
        
        # Verify installation
        if command -v yay &>/dev/null; then
            echo "✓ yay installed successfully!"
            echo "yay version: $(yay --version)"
            
            # Configure yay
            echo "Configuring yay..."
            mkdir -p /home/$USER_NAME/.config/yay
            chown $USER_NAME:$USER_NAME /home/$USER_NAME/.config/yay
            
            # Create basic yay config if it doesn't exist
            if [ ! -f /etc/yay.conf ]; then
                cat > /etc/yay.conf << 'YAYCONF'
# yay configuration
{
  "aururl": "https://aur.archlinux.org",
  "buildDir": "/tmp/yay-build",
  "editor": "",
  "editorflags": "",
  "makepkgbin": "makepkg",
  "makepkgconf": "",
  "pacmanbin": "pacman",
  "pacmanconf": "/etc/pacman.conf",
  "requestsplitn": 150,
  "sortby": "votes",
  "sudobin": "sudo",
  "sudoconf": "",
  "cleanAfter": false,
  "gitbin": "git",
  "gpgbin": "gpg",
  "gpgflags": "",
  "mflags": "",
  "redownload": "no",
  "rebuild": "no",
  "answerclean": "",
  "answerdiff": "",
  "answeredit": "",
  "answerupgrade": "",
  "noconfirm": false
}
YAYCONF
            fi
        else
            echo "✗ yay installation failed!"
            return 1
        fi
        
        echo "=== yay installation completed ==="
        return 0
    }
    
    # Run yay installation inside chroot
    if arch-chroot "$TARGET_ROOT" bash -c "$(declare -f install_yay); install_yay" 2>&1 | tee -a "$LOG_FILE"; then
        echo "✓ yay installation attempted"
    else
        echo "⚠ yay installation may have encountered errors"
    fi
    
    # Final verification of both installations
    show_progress "Verifying package manager installations..."
    
    # Check pamac
    if arch-chroot "$TARGET_ROOT" bash -c "pacman -Q pamac 2>/dev/null || pacman -Q pamac-aur 2>/dev/null || pacman -Q pamac-gtk 2>/dev/null" &>/dev/null; then
        echo "✓ pamac is installed"
    else
        echo "⚠ pamac is NOT installed"
    fi
    
    # Check yay
    if arch-chroot "$TARGET_ROOT" bash -c "command -v yay" &>/dev/null; then
        echo "✓ yay is installed"
        # Test yay
        if arch-chroot "$TARGET_ROOT" bash -c "yay --version" &>/dev/null; then
            echo "✓ yay is working"
        else
            echo "⚠ yay installed but not working properly"
        fi
    else
        echo "⚠ yay is NOT installed"
        
        # Create a fallback yay wrapper that installs on first use
        show_progress "Creating yay fallback wrapper..."
        cat > "$TARGET_ROOT/usr/local/bin/yay" << 'YAY_FALLBACK'
#!/bin/bash
# Yay wrapper that installs on first use if not present

# First, check if real yay exists
if command -v yay_real &>/dev/null; then
    exec yay_real "$@"
elif [ -x /usr/bin/yay ]; then
    exec /usr/bin/yay "$@"
elif [ -x /usr/local/bin/yay_real ]; then
    exec /usr/local/bin/yay_real "$@"
else
    echo "yay not found. Installing now (this will take a moment)..."
    
    # Install dependencies
    sudo pacman -S --noconfirm --needed git base-devel go
    
    # Build yay
    cd /tmp
    git clone https://github.com/Jguer/yay.git
    cd yay
    make
    sudo make install
    sudo mv /usr/local/bin/yay /usr/local/bin/yay_real
    
    # Clean up
    cd /
    sudo rm -rf /tmp/yay
    
    echo "yay installation complete. Running: yay_real $@"
    exec yay_real "$@"
fi
YAY_FALLBACK
        
        chmod +x "$TARGET_ROOT/usr/local/bin/yay"
        echo "✓ Created yay fallback wrapper"
    fi
    
fi
# === END USER-SPECIFIC SETUP ===

# Configure DNS — apply to target if Calamares, else live system
show_progress "Configuring DNS..."
if [ "$IS_CALAMARES" = true ]; then
    mkdir -p "$TARGET_ROOT/etc"
    cat > "$TARGET_ROOT/etc/resolv.conf" << 'EOF'
# EcoOS/StormOS - Reliable DNS Configuration
nameserver 1.1.1.1
nameserver 1.0.0.1
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 9.9.9.9
EOF
    echo "✓ DNS configured in target system"
else
    if [ ! -e /etc/resolv.conf ] || [ -L /etc/resolv.conf ]; then
        rm -f /etc/resolv.conf
        cat > /etc/resolv.conf << 'EOF'
# EcoOS/StormOS - Reliable DNS Configuration
nameserver 1.1.1.1
nameserver 1.0.0.1
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 9.9.9.9
EOF
        echo "✓ DNS configured in live system"
    else
        echo "✓ DNS already configured"
    fi
fi

# Set execute permissions on scripts/AppImages (global)
show_progress "Setting execute permissions on /usr/local/bin..."
if [ "$IS_CALAMARES" = true ]; then
    BIN_DIR="$TARGET_ROOT/usr/local/bin"
else
    BIN_DIR="/usr/local/bin"
fi

if [ -d "$BIN_DIR" ]; then
    find "$BIN_DIR" -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
    find "$BIN_DIR" -name "*.AppImage" -exec chmod +x {} \; 2>/dev/null || true
    find "$BIN_DIR" -name "*.*" -exec chmod +x {} \; 2>/dev/null || true
    echo "✓ Set execute permissions"
fi

# Configure sudo feedback
show_progress "Configuring sudo feedback..."
if [ "$IS_CALAMARES" = true ]; then
    SUDOERS_FILE="$TARGET_ROOT/etc/sudoers"
else
    SUDOERS_FILE="/etc/sudoers"
fi

if [ -f "$SUDOERS_FILE" ]; then
    if ! grep -q "Defaults pwfeedback" "$SUDOERS_FILE" 2>/dev/null; then
        if [ "$IS_CALAMARES" = true ]; then
            echo "Defaults pwfeedback" >> "$SUDOERS_FILE"
        else
            echo "Defaults pwfeedback" | EDITOR='tee -a' visudo >/dev/null 2>&1 || true
        fi
        echo "✓ Configured sudo feedback"
    fi
fi

# Enable essential services (only in Calamares)
if [ "$IS_CALAMARES" = true ]; then
    show_progress "Enabling essential services..."
    
    arch-chroot "$TARGET_ROOT" bash -c "
        # Enable NetworkManager
        systemctl enable NetworkManager 2>/dev/null || true
        
        # Enable lightdm display manager
        systemctl enable lightdm 2>/dev/null || true
        
        # Enable bluetooth
        systemctl enable bluetooth 2>/dev/null || true
        
        # Enable CUPS for printing
        systemctl enable cups.service 2>/dev/null || true
        
        # Enable fstrim for SSD optimization
        systemctl enable fstrim.timer 2>/dev/null || true
        
        # Enable paccache timer for automatic package cache cleanup
        systemctl enable paccache.timer 2>/dev/null || true
        
        echo '✓ Essential services enabled'
    "
fi

# Set up reflector for faster mirrors (only in installed system)
if [ "$IS_CALAMARES" = true ]; then
    show_progress "Setting up reflector for faster mirrors..."
    
    arch-chroot "$TARGET_ROOT" bash -c "
        # Install reflector if not present
        pacman -S --noconfirm reflector 2>/dev/null || true
        
        # Create reflector service file
        cat > /etc/xdg/reflector/reflector.conf << 'REFLECTOREOF'
--country 'United States,Canada'
--protocol https
--latest 20
--sort rate
--save /etc/pacman.d/mirrorlist
REFLECTOREOF
        
        # Enable and start reflector timer
        systemctl enable reflector.timer 2>/dev/null || true
        systemctl start reflector.timer 2>/dev/null || true
        
        echo '✓ Reflector configured for automatic mirror updates'
    "
fi

# Create desktop shortcut for installer (only in live system)
if [ "$IS_CALAMARES" = false ]; then
    show_progress "Creating installation shortcuts..."
    
    # Create desktop entry for installer
    cat > "/usr/share/applications/install-ecoos.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Install EcoOS
Comment=Install EcoOS to your hard drive
Exec=calamares
Icon=system-installer
Terminal=false
Categories=System;
EOF
    
    # Copy to desktop if user directory exists
    if [ -d "/home/$USER_NAME/Desktop" ]; then
        cp "/usr/share/applications/install-ecoos.desktop" "/home/$USER_NAME/Desktop/"
        chown "$USER_NAME:$USER_NAME" "/home/$USER_NAME/Desktop/install-ecoos.desktop"
    fi
    
    echo "✓ Installation shortcuts created"
fi

# Final verification (only in Calamares)
if [ "$IS_CALAMARES" = true ]; then
    show_progress "Running final verification..."
    SUCCESS=true
    
    # Check user directories
    for dir in Desktop Downloads; do
        if [ ! -d "$USER_HOME/$dir" ]; then
            echo "⚠ WARNING: $USER_HOME/$dir is missing"
            SUCCESS=false
        fi
    done

    if [ ! -f "$USER_HOME/.config/user-dirs.dirs" ]; then
        echo "⚠ WARNING: user-dirs.dirs is missing"
        SUCCESS=false
    fi
    
    if [ "$SUCCESS" = true ]; then
        echo "✓ All critical components verified"
    else
        echo "⚠ Some components missing, but setup completed"
    fi
fi

echo ""
echo "=================================================="
echo "EcoOS/StormOS post-installation setup COMPLETED!"
echo "Context: $( [ "$IS_CALAMARES" = true ] && echo "System Installation" || echo "Live System" )"
if [ -n "$USER_NAME" ]; then
    echo "User: $USER_NAME"
    echo "Home: $USER_HOME"
fi
echo "Log: $LOG_FILE"
echo "=================================================="

# Create reboot reminder (only in installed system)
if [ "$IS_CALAMARES" = true ]; then
    cat > "$USER_HOME/Desktop/README_FIRST.txt" << 'EOF'
Welcome to EcoOS/StormOS!

IMPORTANT: Please reboot your system after installation to ensure all
services and drivers are properly loaded.

After rebooting:
1. Log in with your username and password
2. Run 'sudo pacman -Syu' to update your system
3. Use 'yay' to install packages from AUR (yay -S package-name)
4. Use 'pamac' for GUI package management
5. Customize your system as needed

Installed package managers:
- pacman: Command line (sudo pacman -S package)
- yay: AUR helper (yay -S package)
- pamac: GUI package manager

If yay is not working on first try, it will automatically install
when you first use it.

For help and documentation, please visit:
- https://wiki.archlinux.org
- https://wiki.manjaro.org

Enjoy your new system!
EOF
    chown "${USER_UID:-1000}:${USER_GID:-1000}" "$USER_HOME/Desktop/README_FIRST.txt"
    echo "✓ Created reboot reminder on desktop"
fi

exit 0