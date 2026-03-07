#!/usr/bin/env python3
"""
Build script for Morzhaka Quest game.
Creates standalone executables for distribution.

Usage:
    python build.py

For Windows users:
    You can also run build.bat for an easier experience.
"""

import subprocess
import sys
import os
import shutil

GAME_NAME = "MorzhakaQuest"

def clean_build():
    """Remove previous build artifacts."""
    dirs_to_remove = ["dist", "build"]
    files_to_remove = [f"{GAME_NAME}.spec"]
    
    for d in dirs_to_remove:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"  Removed {d}/")
    
    for f in files_to_remove:
        if os.path.exists(f):
            os.remove(f)
            print(f"  Removed {f}")

def main():
    print("=" * 50)
    print("  Morzhaka Quest - Build Script")
    print("=" * 50)
    print()
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("[OK] PyInstaller found")
    except ImportError:
        print("[..] Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[OK] PyInstaller installed")
    
    # Check if Pygame is installed
    try:
        import pygame
        print("[OK] Pygame found")
    except ImportError:
        print("[..] Installing Pygame...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame>=2.5.0"])
        print("[OK] Pygame installed")
    
    print()
    print("[..] Cleaning previous builds...")
    clean_build()
    print("[OK] Cleaned")
    
    print()
    print("=" * 50)
    print("  Building executable...")
    print("=" * 50)
    print()
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", GAME_NAME,
        "game.py"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print()
        print("=" * 50)
        print("  BUILD SUCCESSFUL!")
        print("=" * 50)
        
        if sys.platform == "win32":
            exe_path = os.path.join("dist", f"{GAME_NAME}.exe")
        else:
            exe_path = os.path.join("dist", GAME_NAME)
        
        print()
        print(f"  Executable created at: {exe_path}")
        print()
        print("  You can now share this file with your friends!")
        print()
    else:
        print()
        print("BUILD FAILED. Check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
