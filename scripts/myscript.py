#!/usr/bin/env python3

"""
Example Python script for local pre-commit hooks
This script is not enabled by default but can be integrated via a local hook

To enable it, add a local hook in your .pre-commit-config.yaml:

- repo: local
  hooks:
    - id: custom-python-script
      name: Custom Python Script
      entry: ./scripts/myscript.py
      language: python
      files: \.py$
"""

import sys


def main():
    """Main function that prints script execution and arguments."""
    print("[myscript.py] Script Python exécuté")
    
    if len(sys.argv) > 1:
        print(f"Arguments reçus: {sys.argv[1:]}")
    else:
        print("Aucun argument fourni")
    
    # Add your custom Python logic here
    # For example: code analysis, custom linting, or file processing
    
    return 0


if __name__ == "__main__":
    sys.exit(main())