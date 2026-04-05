#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║       DEADLOCK PREVENTION & DETECTION TOOLKIT               ║
║              Unified Launcher                                ║
╚══════════════════════════════════════════════════════════════╝

Run:  python deadlock_combined.py

This launcher lets you choose between:
  1. Terminal UI  (Rich-based terminal interface)
  2. Desktop GUI  (CustomTkinter graphical interface)
"""

import os
import sys
import importlib


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def show_launcher():
    """Display the mode selection screen."""
    clear_screen()

    # ── ANSI colors for the launcher (no dependencies needed) ──
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    MAGENTA = "\033[95m"
    RED = "\033[91m"
    WHITE = "\033[97m"

    banner = f"""
{CYAN}{BOLD}    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                               ║
    ║   ██████╗ ███████╗ █████╗ ██████╗ ██╗      ██████╗  ██████╗██╗  ██╗           ║
    ║   ██╔══██╗██╔════╝██╔══██╗██╔══██╗██║     ██╔═══██╗██╔════╝██║ ██╔╝           ║
    ║   ██║  ██║█████╗  ███████║██║  ██║██║     ██║   ██║██║     █████╔╝            ║
    ║   ██║  ██║██╔══╝  ██╔══██║██║  ██║██║     ██║   ██║██║     ██╔═██╗            ║
    ║   ██████╔╝███████╗██║  ██║██████╔╝███████╗╚██████╔╝╚██████╗██║  ██╗           ║
    ║   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝           ║
    ║                                                                               ║{RESET}
{MAGENTA}{BOLD}    ║   ████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗██╗████████╗                     ║
    ║   ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║ ██╔╝██║╚══██╔══╝                     ║
    ║      ██║   ██║   ██║██║   ██║██║     █████╔╝ ██║   ██║                        ║
    ║      ██║   ██║   ██║██║   ██║██║     ██╔═██╗ ██║   ██║                        ║
    ║      ██║   ╚██████╔╝╚██████╔╝███████╗██║  ██╗██║   ██║                        ║
    ║      ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝                        ║{RESET}
{WHITE}{BOLD}    ║                                                                               ║
    ║            DEADLOCK PREVENTION & DETECTION TOOLKIT                             ║
    ║                                                                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)

    print(f"""
{BOLD}{WHITE}    ┌──────────────────────────────────────────────┐{RESET}
{BOLD}{WHITE}    │         SELECT YOUR INTERFACE MODE            │{RESET}
{BOLD}{WHITE}    └──────────────────────────────────────────────┘{RESET}

{CYAN}{BOLD}      [1]{RESET}  {GREEN}{BOLD}  Terminal Mode{RESET}


{CYAN}{BOLD}      [2]{RESET}  {MAGENTA}{BOLD}  GUI Mode{RESET}


{CYAN}{BOLD}      [3]{RESET}  {RED}{BOLD}  Exit{RESET}
""")

    while True:
        try:
            choice = input(f"{CYAN}{BOLD}    ➤ Enter your choice (1/2/3): {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{DIM}    Exited.{RESET}")
            sys.exit(0)

        if choice == '1':
            return 'terminal'
        elif choice == '2':
            return 'gui'
        elif choice == '3':
            print(f"\n{GREEN}{BOLD}    Thank you for using the Deadlock Toolkit! Goodbye.{RESET}\n")
            sys.exit(0)
        else:
            print(f"{RED}    Invalid choice. Please enter 1, 2, or 3.{RESET}")


def run_terminal_mode():
    """Launch the terminal (Rich) based toolkit."""
    # Get the directory of this script so we can import the module
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)

    try:
        # Import and run the terminal toolkit
        toolkit = importlib.import_module("deadlock_toolkit")
        toolkit.main_menu()
    except ImportError as e:
        print(f"\n  [ERROR] Could not load terminal toolkit: {e}")
        print("  Make sure 'deadlock_toolkit.py' is in the same directory.")
        print("  Also install dependencies: pip install rich psutil")
        sys.exit(1)


def run_gui_mode():
    """Launch the GUI (CustomTkinter) based toolkit."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)

    try:
        # Import and run the GUI toolkit
        gui = importlib.import_module("deadlock_gui")
        app = gui.DeadlockApp()
        app.mainloop()
    except ImportError as e:
        print(f"\n  [ERROR] Could not load GUI toolkit: {e}")
        print("  Make sure 'deadlock_gui.py' is in the same directory.")
        print("  Also install dependencies: pip install customtkinter psutil")
        sys.exit(1)


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mode = show_launcher()

    if mode == 'terminal':
        run_terminal_mode()
    elif mode == 'gui':
        run_gui_mode()
