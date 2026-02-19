#!/usr/bin/env python3
"""
Entry point for PyInstaller builds.
This file has no relative imports so PyInstaller can use it as the main script.
"""

if __name__ == '__main__':
    from src.cli import main
    main()
