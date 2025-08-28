#!/usr/bin/env python3
"""Simple launcher for the crypto portfolio Streamlit GUI."""

import os
import subprocess
import sys


def main():
    """Launch the Streamlit GUI."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    # Change to project root directory
    os.chdir(project_root)

    # Set PYTHONPATH to include src directory
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    # Command to run Streamlit
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "src/crypto_invest_portfolio/streamlit_gui/main.py",
        "--server.address",
        "0.0.0.0",  # noqa: S104
        "--server.port",
        "8501",
    ]

    print("🚀 Starting Crypto Portfolio Tracker GUI...")
    print("📍 The application will open in your browser at http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the application")
    print()

    try:
        subprocess.run(cmd, env=env)  # noqa: S603
    except KeyboardInterrupt:
        print("\n👋 Crypto Portfolio Tracker GUI stopped.")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
