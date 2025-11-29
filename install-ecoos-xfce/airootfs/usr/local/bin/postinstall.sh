#!/bin/bash -e
#
##############################################################################
#  PostInstall - StormOS setup script
#  Licensed under GPLv3 or later
##############################################################################


# Get the actual logged-in user, even if script runs as root
USER_NAME=$(logname)

# Remove unwanted launchers
rm -f "/home/$USER_NAME/Desktop/calamares.desktop" || true

reflector --protocol https --latest 20 --sort rate --save /etc/pacman.d/mirrorlist && pacman -Syu --noconfirm


# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: This script must be run as root" >&2
    exit 1
fi

# Setup logging
LOG_FILE="/var/log/stormos-postinstall.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "=================================================="
echo "StormOS Post-Installation Setup - $(date)"
echo "=================================================="

# Function to show progress
show_progress() {
    echo "→ $1"
}

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
# StormOS Bash Configuration
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi
EOF
        echo "✓ Created basic .bashrc"
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
fi
# === END USER-SPECIFIC SETUP ===

# Configure DNS — apply to target if Calamares, else live system
show_progress "Configuring DNS..."
if [ "$IS_CALAMARES" = true ]; then
    mkdir -p "$TARGET_ROOT/etc"
    cat > "$TARGET_ROOT/etc/resolv.conf" << 'EOF'
# StormOS - Reliable DNS Configuration
nameserver 8.8.8.8
nameserver 1.1.1.1
nameserver 9.9.9.9
nameserver 208.67.222.222
nameserver 8.8.4.4
EOF
    echo "✓ DNS configured in target system"
else
    if [ ! -e /etc/resolv.conf ] || [ -L /etc/resolv.conf ]; then
        rm -f /etc/resolv.conf
        cat > /etc/resolv.conf << 'EOF'
# StormOS - Reliable DNS Configuration
nameserver 8.8.8.8
nameserver 1.1.1.1
nameserver 9.9.9.9
nameserver 208.67.222.222
nameserver 8.8.4.4
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

# Final verification (only in Calamares)
if [ "$IS_CALAMARES" = true ]; then
    show_progress "Running final verification..."
    SUCCESS=true
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
echo "StormOS post-installation setup COMPLETED!"
echo "Context: $( [ "$IS_CALAMARES" = true ] && echo "Installation" || echo "Live System" )"
if [ -n "$USER_NAME" ]; then
    echo "User: $USER_NAME"
    echo "Home: $USER_HOME"
fi
echo "Log: $LOG_FILE"
echo "=================================================="

exit 0