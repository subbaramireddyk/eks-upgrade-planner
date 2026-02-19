#!/usr/bin/env python3
"""
Entry point for PyInstaller builds.
This file has no relative imports so PyInstaller can use it as the main script.
"""
import sys

if __name__ == '__main__':
    # Import from the installed package
    from src.cli import main
    sys.exit(main())
