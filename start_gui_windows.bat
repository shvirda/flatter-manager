@echo off
echo ==========================================
echo Flutter Project Manager - GUI Launcher
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if main GUI file exists
if not exist "flutter_project_manager.py" (
    echo ERROR: flutter_project_manager.py not found!
    echo Make sure all program files are in the same directory.
    pause
    exit /b 1
)

REM Display Python version
echo Checking Python installation...
python --version

REM Check for tkinter availability
echo Checking GUI libraries...
python -c "import tkinter; print('✓ tkinter is available')" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: tkinter is not available!
    echo tkinter is required for GUI interface.
    echo Please reinstall Python with tkinter support.
    pause
    exit /b 1
)

REM Check for other required modules
python -c "import sqlite3; print('✓ sqlite3 is available')" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: sqlite3 is not available!
    pause
    exit /b 1
)

echo.
echo ✓ All dependencies are satisfied
echo Starting Flutter Project Manager GUI...
echo.

REM Start the GUI application
python flutter_project_manager.py

REM Check if there was an error
if %errorlevel% neq 0 (
    echo.
    echo ERROR: The application encountered an error!
    echo Please check the error messages above.
    pause
    exit /b %errorlevel%
)

echo.
echo Application closed successfully.
pause
