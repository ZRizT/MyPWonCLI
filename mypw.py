#!/usr/bin/env python3

import os
import json
import base64
import getpass
import argparse
import secrets
import string
import pyperclip
import time

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

# --- Constants ---
VAULT_PATH = os.path.expanduser("~/.mypw_vault.enc")
SALT_SIZE = 16
KDF_ITERATIONS = 480_000  # High number of iterations for security

# --- Rich Console Initialization ---
console = Console()

# --- Core Cryptography Functions ---

def derive_key(password: str, salt: bytes) -> bytes:
    """Derives a secure encryption key from a password and salt using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_data(data: dict, password: str) -> bytes:
    """Encrypts a data dictionary into a secure, storable format."""
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    f = Fernet(key)
    encrypted_data = f.encrypt(json.dumps(data).encode())
    # Return salt and encrypted data, concatenated and base64 encoded for safe storage
    return base64.b64encode(salt + encrypted_data)

def decrypt_data(encrypted_blob: bytes, password: str) -> dict:
    """Decrypts the vault data and returns the dictionary."""
    try:
        decoded_blob = base64.b64decode(encrypted_blob)
        salt = decoded_blob[:SALT_SIZE]
        encrypted_data = decoded_blob[SALT_SIZE:]
        key = derive_key(password, salt)
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data)
        return json.loads(decrypted_data)
    except Exception as e:
        # Catching broad exceptions because various crypto errors can occur
        console.print("[bold red]Error: Decryption failed. Incorrect master password or corrupt vault.[/bold red]")
        return None

# --- Vault Management ---

def initialize_vault():
    """Initializes a new, empty password vault."""
    if os.path.exists(VAULT_PATH):
        console.print("[bold yellow]Warning:[/bold yellow] Vault already exists. Aborting initialization.")
        return

    console.print(Panel.fit("[bold cyan]Welcome to MyPW Setup[/bold cyan]\nLet's create your secure vault.", title="Initialization"))
    password = getpass.getpass("Enter a strong master password: ")
    password_confirm = getpass.getpass("Confirm master password: ")

    if password != password_confirm:
        console.print("[bold red]Error: Passwords do not match.[/bold red]")
        return

    if not password:
        console.print("[bold red]Error: Master password cannot be empty.[/bold red]")
        return

    empty_vault = {"accounts": {}}
    encrypted_vault = encrypt_data(empty_vault, password)

    with open(VAULT_PATH, "wb") as f:
        f.write(encrypted_vault)

    console.print("[bold green]✓ Vault initialized successfully at:[/bold green]", VAULT_PATH)

def reset_vault():
    if not os.path.exists(VAULT_PATH):
        console.print("[yellow]No vault found. Nothing to reset.[/yellow]")
        return

    console.print(Panel.fit(
        "[bold red]⚠️ WARNING ⚠️[/bold red]\n\n"
        "Resetting the master password will:\n"
        "- Permanently delete ALL stored passwords\n"
        "- Create a new empty vault\n\n"
        "[bold]This action CANNOT be undone.[/bold]",
        title="Vault Reset"
    ))

    if not Confirm.ask("Do you really want to reset the vault?", default=False):
        console.print("[dim]Reset cancelled.[/dim]")
        return

    confirmation = Prompt.ask(
        "[bold red]Type 'RESET' to confirm[/bold red]"
    )

    if confirmation != "RESET":
        console.print("[bold yellow]Confirmation failed. Vault was NOT reset.[/bold yellow]")
        return

    try:
        os.remove(VAULT_PATH)
        console.print("[green]✓ Old vault deleted.[/green]")
        initialize_vault()
    except Exception as e:
        console.print(f"[bold red]Reset failed: {e}[/bold red]")


def load_vault(password: str) -> dict:
    """Loads and decrypts the vault from disk."""
    if not os.path.exists(VAULT_PATH):
        console.print("[bold red]Error:[/bold red] Vault not found. Please run `pw init` first.")
        return None

    with open(VAULT_PATH, "rb") as f:
        encrypted_blob = f.read()

    return decrypt_data(encrypted_blob, password)

def save_vault(data: dict, password: str):
    """Encrypts and saves the vault to disk."""
    encrypted_vault = encrypt_data(data, password)
    with open(VAULT_PATH, "wb") as f:
        f.write(encrypted_vault)

# --- CLI Application Class ---

class MyPW:
    def __init__(self):
        self.master_password = None
        self.vault_data = None

    def login(self):
        """Prompts for master password and loads vault."""
        if not os.path.exists(VAULT_PATH):
             console.print("[bold red]Error:[/bold red] No vault found. Please run `pw init` to get started.")
             exit(1)
        self.master_password = getpass.getpass("Enter master password: ")
        self.vault_data = load_vault(self.master_password)
        if self.vault_data is None:
            exit(1)

    def display_banner(self):
        """Displays the ASCII art banner."""
        console.print(Panel("""[bold cyan]

███╗░░░███╗  ██╗░░░██╗  ██████╗░  ██╗░░░░░██╗
████╗░████║  ╚██╗░██╔╝  ██╔══██╗  ██║░██░░██║
██╔████╔██║  ░╚████╔╝░  ██████╔╝  ██║░██░░██║
██║╚██╔╝██║  ░░╚██╔╝░░  ██╔═══╝░  ██╚╗██ ╔██║
██║░╚═╝░██║  ░░░██║░░░  ██║░░░░░  ╚███╔═███╔╝
╚═╝░░░░░╚═╝  ░░░╚═╝░░░  ╚═╝░░░░░  ░╚══╝ ╚══╝

[/bold cyan]
 [dim]Your Modern Terminal Password Manager[/dim]""", title="MyPW", expand=False))

    def generate_password(self, length=20, include_symbols=True, include_uppercase=True, include_lowercase=True, include_numbers=True):
        """Generates a strong, random password."""
        alphabet = ""
        if include_uppercase:
            alphabet += string.ascii_uppercase
        if include_lowercase:
            alphabet += string.ascii_lowercase
        if include_numbers:
            alphabet += string.digits
        if include_symbols:
            alphabet += string.punctuation

        if not alphabet:
            console.print("[bold red]Cannot generate password with no character types selected.[/bold red]")
            return None

        return ''.join(secrets.choice(alphabet) for i in range(length))

    def add_entry(self):
        """Adds a new password entry to the vault."""
        console.print("\n[bold underline cyan]Add New Entry[/bold underline cyan]")
        service = Prompt.ask("Enter service name (e.g., Google, GitHub)")
        
        if service.lower() in self.vault_data['accounts']:
            if not Confirm.ask(f"[yellow]Service '{service}' already exists. Overwrite?[/yellow]"):
                console.print("[dim]Operation cancelled.[/dim]")
                return

        username = Prompt.ask("Enter username/email")
        
        if Confirm.ask("Generate a strong password automatically?", default=True):
            password = self.generate_password()
            console.print(f"Generated password: [bold green]{password}[/bold green]")
        else:
            password = getpass.getpass("Enter password: ")

        self.vault_data['accounts'][service.lower()] = {"username": username, "password": password}
        save_vault(self.vault_data, self.master_password)
        console.print(f"[bold green]✓ Entry for '{service}' added successfully.[/bold green]")

    def get_entry(self, service_name):
        """Retrieves and displays a specific entry."""
        entry = self.vault_data['accounts'].get(service_name.lower())
        if not entry:
            console.print(f"[bold red]Error:[/bold red] No entry found for '{service_name}'.")
            return
            
        table = Table(title=f"Details for '{service_name}'", show_header=False, box=None)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Username", entry['username'])
        table.add_row("Password", "********")
        console.print(table)

        if Confirm.ask("\nCopy password to clipboard? (clears in 15s)", default=True):
            pyperclip.copy(entry['password'])
            console.print("[green]Password copied to clipboard. It will be cleared in 15 seconds.[/green]", end="")
            for i in range(15, 0, -1):
                time.sleep(1)
                print(f"\r[green]Password copied to clipboard. It will be cleared in {i:2d} seconds.[/green]", end="")
            pyperclip.copy("") # Clear clipboard
            print("\r[bold yellow]Clipboard cleared.                                              [/bold yellow]")

    def list_entries(self):
        """Lists all entries in a table."""
        accounts = self.vault_data.get('accounts', {})
        if not accounts:
            console.print("[yellow]Your vault is empty. Use `pw add` to add an entry.[/yellow]")
            return
            
        table = Table(title="MyPW Vault", show_header=True, header_style="bold magenta")
        table.add_column("Service", style="cyan", no_wrap=True)
        table.add_column("Username", style="green")
        
        for service, details in sorted(accounts.items()):
            table.add_row(service, details['username'])
            
        console.print(table)

    def delete_entry(self, service_name):
        """Deletes an entry from the vault."""
        if service_name.lower() not in self.vault_data['accounts']:
            console.print(f"[bold red]Error:[/bold red] No entry found for '{service_name}'.")
            return
            
        if Confirm.ask(f"Are you sure you want to delete the entry for '{service_name}'?"):
            del self.vault_data['accounts'][service_name.lower()]
            save_vault(self.vault_data, self.master_password)
            console.print(f"[bold green]✓ Entry for '{service_name}' deleted.[/bold green]")
        else:
            console.print("[dim]Operation cancelled.[/dim]")

    def interactive_mode(self):
        """Runs the main interactive menu loop."""
        self.display_banner()
        self.login()

        while True:
            console.print("\n[bold]Main Menu:[/bold]")
            choice = Prompt.ask(
                "Choose an action",
                choices=["list", "add", "get", "delete", "generate", "quit"],
                default="list"
            )

            if choice == "list":
                self.list_entries()
            elif choice == "add":
                self.add_entry()
            elif choice == "get":
                service = Prompt.ask("Enter service name to get")
                self.get_entry(service)
            elif choice == "delete":
                service = Prompt.ask("Enter service name to delete")
                self.delete_entry(service)
            elif choice == "generate":
                password = self.generate_password()
                console.print(f"Generated Password: [bold green]{password}[/bold green]")
                pyperclip.copy(password)
                console.print("[dim]Copied to clipboard.[/dim]")
            elif choice == "quit":
                console.print("[bold cyan]Goodbye![/bold cyan]")
                break
# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(description="MyPW: A modern terminal password manager.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("init", help="Initialize a new password vault.")
    subparsers.add_parser("add", help="Add a new password entry.")
    subparsers.add_parser("reset", help="Reset master password (DESTROYS all stored data).")

    
    get_parser = subparsers.add_parser("get", help="Get a password for a service.")
    get_parser.add_argument("service", help="Name of the service.")
    
    list_parser = subparsers.add_parser("list", help="List all services in the vault.")
    
    delete_parser = subparsers.add_parser("delete", help="Delete a password entry.")
    delete_parser.add_argument("service", help="Name of the service to delete.")

    gen_parser = subparsers.add_parser("gen", help="Generate a new secure password.")
    gen_parser.add_argument("-l", "--length", type=int, default=20, help="Password length.")

    args = parser.parse_args()
    app = MyPW()

    if args.command == "init":
        initialize_vault()

    elif args.command == "reset":
    reset_vault()

    elif args.command in ["add", "get", "list", "delete"]:
        app.login()
        if args.command == "add":
            app.add_entry()
        elif args.command == "get":
            app.get_entry(args.service)
        elif args.command == "list":
            app.list_entries()
        elif args.command == "delete":
            app.delete_entry(args.service)
    elif args.command == "gen":
        password = app.generate_password(length=args.length)
        console.print(f"Generated Password: [bold green]{password}[/bold green]")
        pyperclip.copy(password)
        console.print("[dim]Copied to clipboard.[/dim]")
    else:
        # Interactive Mode
        try:
            app.interactive_mode()
        except KeyboardInterrupt:
            console.print("\n[bold cyan]Goodbye![/bold cyan]")
        except Exception as e:
            console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")

if __name__ == "__main__":
    main()


