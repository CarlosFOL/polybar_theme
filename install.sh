#!/bin/bash

# CFOL Polybar Theme Installer
# Automated installation script for the customized polybar theme with weather integration

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Check if running on Linux
check_system() {
    print_header "System Check"
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_error "This installer is designed for Linux systems only."
        exit 1
    fi
    print_success "Linux system detected"
}

# Check for required system dependencies
check_dependencies() {
    print_header "Checking Dependencies"

    local missing_deps=()
    local deps=("python3" "sqlite3" "i3" "polybar")

    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done

    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        print_info "Please install them using your package manager:"
        print_info "  Ubuntu/Debian: sudo apt install i3 polybar python3 python3-venv python3-pip sqlite3 pulseaudio"
        print_info "  Arch Linux: sudo pacman -S i3-wm polybar python python-pip sqlite pulseaudio"
        print_info "  Fedora: sudo dnf install i3 polybar python3 python3-venv python3-pip sqlite pulseaudio"
        exit 1
    fi

    print_success "All required dependencies are installed"
}

# Check for API keys
check_api_keys() {
    print_header "Checking API Configuration"

    if [ ! -f ".env" ]; then
        print_error "API keys configuration file (.env) not found!"
        echo
        print_info "Please create a .env file with your API keys:"
        print_info "1. Get MeteoGalicia API key: https://www.meteogalicia.gal/web/modelos-numericos/meteosix"
        print_info "2. Get IP Geolocation API key: https://ipgeolocation.io/"
        echo
        print_info "Create .env file with:"
        echo 'API_MG="your_meteogalicia_api_key"'
        echo 'API_IP="your_ip_geolocation_api_key"'
        exit 1
    fi

    # Check if API keys are present in .env file
    if ! grep -q "API_MG=" .env || ! grep -q "API_IP=" .env; then
        print_error ".env file exists but missing required API keys!"
        print_info "Make sure your .env file contains both:"
        print_info '  API_MG="your_meteogalicia_api_key"'
        print_info '  API_IP="your_ip_geolocation_api_key"'
        exit 1
    fi

    print_success "API keys configuration found"
}

# Setup Python virtual environment
setup_python_env() {
    print_header "Setting up Python Environment"

    if [ ! -d "venv" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi

    print_info "Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    print_success "Python dependencies installed"
}

# Backup existing configurations
backup_configs() {
    print_header "Backing up Existing Configurations"

    local backup_dir="$HOME/.config/polybar_theme_backup_$(date +%Y%m%d_%H%M%S)"
    local backed_up=false

    if [ -f "$HOME/.config/i3/config" ]; then
        mkdir -p "$backup_dir"
        cp "$HOME/.config/i3/config" "$backup_dir/i3_config.backup"
        print_info "Backed up i3 config to $backup_dir"
        backed_up=true
    fi

    if [ -f "$HOME/.config/polybar/config.ini" ]; then
        mkdir -p "$backup_dir"
        cp "$HOME/.config/polybar/config.ini" "$backup_dir/polybar_config.ini.backup"
        print_info "Backed up polybar config to $backup_dir"
        backed_up=true
    fi

    if [ "$backed_up" = true ]; then
        print_success "Configuration backups created in $backup_dir"
    else
        print_info "No existing configurations found to backup"
    fi
}

# Install configuration files
install_configs() {
    print_header "Installing Configuration Files"

    # Create config directories
    mkdir -p "$HOME/.config/i3" "$HOME/.config/polybar" "$HOME/.config/xwallpaper"

    # Copy configurations
    cp config_files/i3_config "$HOME/.config/i3/config"
    cp config_files/polybar_config.ini "$HOME/.config/polybar/config.ini"

    # Copy wallpaper
    if [ -f "assets/wallpapers/001.png" ]; then
        cp assets/wallpapers/001.png "$HOME/.config/xwallpaper/"
        print_info "Default wallpaper installed"
    else
        print_warning "Wallpaper file (001.png) not found, skipping wallpaper setup"
    fi

    # Update paths in polybar config
    local install_path=$(pwd)
    sed -i "s|/path/to/polybar_theme|$install_path|g" "$HOME/.config/polybar/config.ini"

    print_success "Configuration files installed"
}

# Make scripts executable
setup_scripts() {
    print_header "Setting up Scripts"

    chmod +x scripts/battery_status
    chmod +x scripts/get_wdata
    chmod +x app.py

    print_success "Scripts made executable"
}

# Create polybar launch script
create_polybar_launcher() {
    print_header "Creating Polybar Launch Script"

    mkdir -p "$HOME/.config/polybar"

    cat > "$HOME/.config/polybar/launch.sh" << 'EOF'
#!/usr/bin/env bash

# Terminate already running bar instances
killall -q polybar

# Wait until the processes have been shut down
while pgrep -u $UID -x polybar >/dev/null; do sleep 1; done

# Launch polybar
polybar i3wmthemer_bar &
EOF

    chmod +x "$HOME/.config/polybar/launch.sh"

    print_success "Polybar launch script created"
}

# Initialize weather database
init_weather_db() {
    print_header "Initializing Weather Database"

    source venv/bin/activate
    python app.py

    print_success "Weather database initialized"
}

# Setup systemd services
setup_systemd() {
    print_header "Setting up Systemd Weather Update Service"

    local install_path=$(pwd)
    mkdir -p "$HOME/.config/systemd/user"

    # Create service file
    cat > "$HOME/.config/systemd/user/weather-update.service" << EOF
[Unit]
Description=Weather Data Update Service
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=$install_path
ExecStart=$install_path/venv/bin/python app.py
Environment=PATH=$install_path/venv/bin:/usr/bin:/bin

[Install]
WantedBy=default.target
EOF

    # Create timer file
    cat > "$HOME/.config/systemd/user/weather-update.timer" << 'EOF'
[Unit]
Description=Weather Data Update Timer
Requires=weather-update.service

[Timer]
OnCalendar=*-*-* *:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

    # Enable and start the timer
    systemctl --user daemon-reload
    systemctl --user enable weather-update.timer
    systemctl --user start weather-update.timer

    print_success "Systemd weather update service configured and started"
}

# Final instructions
show_final_instructions() {
    print_header "Installation Complete!"

    echo -e "${GREEN}✅ CFOL Polybar Theme has been successfully installed!${NC}\n"

    print_info "Next steps:"
    print_info "1. Restart i3 window manager: Mod+Shift+R"
    print_info "2. Or logout and login again"
    print_info "3. Your polybar should automatically start with the new theme"

    echo
    print_info "Weather updates will run automatically every 5 minutes via systemd"
    print_info "You can check the service status with: systemctl --user status weather-update.timer"

    echo
    print_warning "Note: If you're using bash instead of zsh, consider updating the shebang"
    print_warning "in scripts/battery_status and scripts/get_wdata from #!/usr/bin/zsh to #!/bin/bash"

    echo
    print_success "Enjoy your new polybar theme! 🎉"
}

# Main installation function
main() {
    echo -e "${BLUE}"
    cat << "EOF"
╔═══════════════════════════════════════╗
║     CFOL Polybar Theme Installer      ║
║   Automated Setup for i3 + Polybar   ║
╚═══════════════════════════════════════╝
EOF
    echo -e "${NC}"

    print_info "Starting installation process..."
    echo

    # Check if we're in the right directory
    if [[ ! -f "app.py" || ! -d "config_files" ]]; then
        print_error "Please run this script from the polybar_theme directory"
        exit 1
    fi

    # Run installation steps
    check_system
    check_dependencies
    check_api_keys
    setup_python_env
    backup_configs
    install_configs
    setup_scripts
    create_polybar_launcher
    init_weather_db
    setup_systemd
    show_final_instructions
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${RED}Installation interrupted by user${NC}"; exit 1' INT

# Run main function
main "$@"
