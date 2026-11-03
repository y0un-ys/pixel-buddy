"""PyInstaller entry point for Pixel Buddy.

Run as a top-level script so package-relative imports resolve correctly.
"""
from pixel_buddy.main import main

if __name__ == "__main__":
    raise SystemExit(main())
