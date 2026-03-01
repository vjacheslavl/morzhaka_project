#!/usr/bin/env python3
"""
Build script for Dungeon Crawler game.
Creates standalone executables for distribution.

Usage:
    python build.py
"""

import subprocess
import sys
import os

def main():
    print("=" * 50)
    print("Dungeon Crawler - Build Script")
    print("=" * 50)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Check if Pygame is installed
    try:
        import pygame
        print("✓ Pygame found")
    except ImportError:
        print("Installing Pygame...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    
    print("\nBuilding executable...")
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "DungeonCrawler",
        "game.py"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n" + "=" * 50)
        print("BUILD SUCCESSFUL!")
        print("=" * 50)
        
        if sys.platform == "win32":
            exe_path = os.path.join("dist", "DungeonCrawler.exe")
        else:
            exe_path = os.path.join("dist", "DungeonCrawler")
        
        print(f"\nExecutable created at: {exe_path}")
        print("\nYou can now share this file with your friends!")
    else:
        print("\nBuild failed. Check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
