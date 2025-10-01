#!/bin/bash

# This script installs the MyPW password manager.
# It creates a virtual environment, installs dependencies,
# and creates a command 'pw' in /usr/local/bin.

# --- Configuration ---
INSTALL_DIR="$HOME/.mypw"
VENV_DIR="$INSTALL_DIR/venv"
EXECUTABLE_PATH="/usr/local/bin/pw"
REPO_URL="https://github.com/ZRizT/MyPWonCLI" 

echo "--- MyPW Installer ---"

# --- Pre-flight Checks ---
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install it to continue."
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install it to continue."
    exit 1
fi

# --- Installation Steps ---
echo "1. Creating installation directory at $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR" || exit

echo "2. Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"

echo "3. Activating virtual environment and installing dependencies..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
pip3 install rich pyperclip cryptography

echo "4. Copying the main application script..."
# In a real scenario, you'd git clone or wget the script. For this setup, we'll copy it.
cp "$OLDPWD/mypw.py" "$INSTALL_DIR/mypw.py"
chmod +x "$INSTALL_DIR/mypw.py"

echo "5. Creating the 'pw' command..."
# Use sudo to write to /usr/local/bin
# The script will activate the venv and then run the python script
if [[ $EUID -ne 0 ]]; then
   echo "Sudo privileges are required to create the command in /usr/local/bin."
   sudo -s <<EOF
echo '#!/bin/bash
# Wrapper script for MyPW
source "$VENV_DIR/bin/activate"
python3 "$INSTALL_DIR/mypw.py" "\$@"
' > "$EXECUTABLE_PATH"
EOF
else
echo '#!/bin/bash
# Wrapper script for MyPW
source "$VENV_DIR/bin/activate"
python3 "$INSTALL_DIR/mypw.py" "\$@"
' > "$EXECUTABLE_PATH"
fi


# Make the wrapper executable
sudo chmod +x "$EXECUTABLE_PATH"

echo ""
echo "--- Installation Complete! ---"
echo "You can now use the 'pw' command from anywhere in your terminal."
echo ""
echo "Getting Started:"
echo "  pw init    - Create your secure password vault"
echo "  pw         - Start the interactive menu"
echo "  pw --help  - See all available commands"
echo ""

# Deactivate venv for the current shell
deactivate
