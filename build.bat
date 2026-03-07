@echo off
setlocal enabledelayedexpansion

echo ==================================================
echo    Morzhaka Quest - Windows Build Script
echo ==================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

REM Check if we're in the correct directory
if not exist "game.py" (
    echo ERROR: game.py not found in current directory.
    echo Please run this script from the project root folder.
    pause
    exit /b 1
)

echo [OK] Project files found
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv_build" (
    echo Creating virtual environment...
    python -m venv venv_build
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv_build\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo [OK] Pip upgraded
echo.

REM Install dependencies
echo Installing pygame...
python -m pip install pygame>=2.5.0
if errorlevel 1 (
    echo ERROR: Failed to install pygame.
    pause
    exit /b 1
)
echo [OK] Pygame installed
echo.

echo Installing PyInstaller...
python -m pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller.
    pause
    exit /b 1
)
echo [OK] PyInstaller installed
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "MorzhakaQuest.spec" del /q MorzhakaQuest.spec
echo [OK] Cleaned previous builds
echo.

REM Build the executable
echo ==================================================
echo    Building executable...
echo ==================================================
echo.

python -m PyInstaller --onefile --windowed --name "MorzhakaQuest" game.py

if errorlevel 1 (
    echo.
    echo ==================================================
    echo    BUILD FAILED
    echo ==================================================
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ==================================================
echo    BUILD SUCCESSFUL!
echo ==================================================
echo.
echo Executable created at: dist\MorzhakaQuest.exe
echo.
echo You can now share this file with your friends!
echo.

REM Deactivate virtual environment
call deactivate 2>nul

REM Ask if user wants to open the dist folder
set /p OPEN_FOLDER="Open dist folder? (y/n): "
if /i "%OPEN_FOLDER%"=="y" (
    explorer dist
)

pause
exit /b 0
