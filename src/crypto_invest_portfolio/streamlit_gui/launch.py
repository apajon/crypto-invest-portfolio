#!/usr/bin/env python3
"""Launch script for Streamlit GUI."""

import os
import subprocess
import sys


def main():
    """Launch the Streamlit GUI application."""
    # Get the path to the main.py file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # main_py = os.path.join(current_dir, "main.py")

    # Ensure we're in the project root for imports to work
    project_root = os.path.join(current_dir, "..", "..", "..")

    # Change to project root directory
    os.chdir(project_root)

    # Run streamlit with the main.py file using module execution
    cmd = [sys.executable, "-m", "streamlit", "run", "src/crypto_invest_portfolio/streamlit_gui/main.py"]

    try:
        subprocess.run(cmd, check=True)  # noqa: S603
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStreamlit GUI stopped by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
