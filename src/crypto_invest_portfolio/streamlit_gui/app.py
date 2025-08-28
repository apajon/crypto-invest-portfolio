"""Entry point script for the Streamlit GUI."""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from crypto_invest_portfolio.streamlit_gui.main import main

if __name__ == "__main__":
    main()
