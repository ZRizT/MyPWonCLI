# MyPWonCLI
## MyPW - Your Modern Terminal Password Manager
MyPW is a secure, command-line based password manager designed for developers and terminal enthusiasts. It provides a fast, modern, and interactive CLI to manage your passwords without ever leaving the terminal.
All your data is stored in a single, heavily encrypted file (~/.mypw_vault.enc) on your local machine.

### Features
- Advanced Security: Your vault is encrypted using AES-265 with a key derived from your master password using PBKDF2 with a high iteration count.
- Isolated Data Store: A single, portable, encrypted file holds all your data. No databases, no cloud sync.
- Modern Interactive CLI: A beautiful and user-friendly interface powered by the Rich library.
- Command-Line and Interactive Modes: Use direct commands like pw get github for quick access, or run pw to enter a full interactive menu.
- Secure Password Generator: Create strong, cryptographically secure passwords.
- Clipboard Integration: Safely copy passwords to your clipboard, with an automatic clear after 15 seconds to prevent exposure.

### Security Model
MyPW is designed with a security-first approach:
- Master Password: The only key to your vault. This password is never stored.
- Key Derivation (PBKDF2): We use your master password and a unique, randomly generated salt to create a strong encryption key. Using a salt prevents rainbow table attacks. The process is repeated hundreds of thousands of times to make brute-force attacks extremely slow and computationally expensive.
- AES-256 Encryption: The derived key is used to encrypt your data with the industry-standard AES-256 cipher.
- Local Storage: Your encrypted vault never leaves your machine.

### Installation
**Installation on Linux/macOS**
You can install MyPW using the provided installer script.
1. Save the files: Make sure you have mypw.py and install.sh in the same directory.
2. Make installer executable:
    chmod +x install.sh

3. Run the installer:
   ```
    ./install.sh
   ```
   
The script will ask for your sudo password to place the pw command in /usr/local/bin, making it accessible system-wide.

**Installation on Windows (PowerShell)**
The install.sh script is not compatible with Windows. Follow these steps to install MyPW manually using PowerShell.
1. Ensure Python is installed: Open PowerShell and check if Python 3 is installed and added to your PATH.
    ```bash
    python --version
    ```
    If it's not installed, download it from python.org (make sure to check "Add Python to PATH" during installation) or install it from the Microsoft Store.
2. Create a directory and save the files:
    ```bash
    mkdir ~\~mypw
    cd ~\~mypw
    ```
    
    Save mypw.py and requirements.txt into this new C:\Users\YourUser\~mypw directory.
3. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
    
    If you get an error about script execution being disabled, run this command first and then try activating again:
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    
6. Run MyPW: You can now run the application from within this directory:
    ```bash
    python mypw.py
    ```
    
7. (Optional) Create a permanent pw command: To use the pw command from anywhere, you can add a function to your PowerShell profile.
    - First, open your profile script for editing (it will be created if it doesn't exist):
        ```bash
        notepad $PROFILE
        ```
        
    - Add the following lines to the file and save it:
        ```bash
        function pw {
            & "$HOME\~mypw\venv\Scripts\python.exe" "$HOME\~mypw\mypw.py" $args
        }
        ```
        
    - Reload your profile by restarting PowerShell or running:
        ```bash
        . $PROFILE
        ```
        
    Now you can use pw init, pw list, etc., from any directory in PowerShell.

## Usage
Once installed, you can use the pw command.
First time? Initialize your vault:
    ```bash
    pw init
    ```
    
**Interactive Mode**
For a menu-driven experience, simply run the command by itself:
    ```bash
    pw
    ```
    
**Direct Commands**
For faster access, use direct commands:
- List all entries:
    ```bash
    pw list
    ```
    
- Add a new entry:
    ```bash
    pw add
    ```
    
- Get and copy a password:
    ```bash
    pw get github
    ```
    
- Delete an entry:
    ```bash
    pw delete "My Website"
    ```
    
- Generate a new password:
    ```bash
    pw gen
    \# Generate a 30-character password
    pw gen --length 30
    ```
    
- See all options:
    ```bash
    pw --help
    ```
    

## Manual Installation (Alternative for Linux/macOS)
If you prefer not to use the installer script on Linux/macOS:
1. Install Python 3 and Pip.
2. Install the dependencies:
    ```bash
    pip3 install -r requirements.txt
    ```
    
3. Run the application directly:
    ```bash
    python3 mypw.py
    ```
    
4. (Optional) Create a shell alias for convenience in your .bashrc or .zshrc:
    ```bash
    alias pw='python3 /path/to/mypw.py'
    ```    
