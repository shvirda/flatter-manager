@echo off
title Flutter Project Manager
color 0A

echo.
echo    █████▒██▓     █    ██ ▄▄▄█████▓▄▄▄█████▓▓█████  ██▀███  
echo  ▓██   ▒▓██▒     ██  ▓██▒▓  ██▒ ▓▒▓  ██▒ ▓▒▓█   ▀ ▓██ ▒ ██▒
echo  ▒████ ░▒██░    ▓██  ▒██░▒ ▓██░ ▒░▒ ▓██░ ▒░▒███   ▓██ ░▄█ ▒
echo  ░▓█▒  ░▒██░    ▓▓█  ░██░░ ▓██▓ ░ ░ ▓██▓ ░ ▒▓█  ▄ ▒██▀▀█▄  
echo  ░▒█░   ░██████▒▒▒█████▓   ▒██▒ ░   ▒██▒ ░ ░▒████▒░██▓ ▒██▒
echo   ▒ ░   ░ ▒░▓  ░░▒▓▒ ▒ ▒   ▒ ░░     ▒ ░░   ░░ ▒░ ░░ ▒▓ ░▒▓░
echo   ░     ░ ░ ▒  ░░░▒░ ░ ░     ░        ░     ░ ░  ░  ░▒ ░ ▒░
echo   ░ ░     ░ ░    ░░░ ░ ░   ░        ░         ░     ░░   ░ 
echo             ░  ░   ░                          ░  ░   ░     
echo.
echo                PROJECT MANAGER
echo           ========================
echo.

:MENU
echo Choose launch mode:
echo.
echo [1] 🖥️  Start GUI Interface
echo [2] 💻 Start Console Interface  
echo [3] ⚙️  Quick GUI Launcher (Python)
echo [4] 🔧 Check Dependencies
echo [5] 📖 Show Help
echo [0] ❌ Exit
echo.
set /p choice="Enter your choice (0-5): "

if "%choice%"=="1" goto GUI_MODE
if "%choice%"=="2" goto CONSOLE_MODE
if "%choice%"=="3" goto QUICK_GUI
if "%choice%"=="4" goto CHECK_DEPS
if "%choice%"=="5" goto SHOW_HELP
if "%choice%"=="0" goto EXIT
echo Invalid choice! Please try again.
goto MENU

:GUI_MODE
echo.
echo 🖥️ Starting GUI Interface...
echo.
if exist "start_gui_windows.bat" (
    call start_gui_windows.bat
) else (
    echo start_gui_windows.bat not found, using direct launch...
    python flutter_project_manager.py
)
goto END

:CONSOLE_MODE
echo.
echo 💻 Starting Console Interface...
echo.
if exist "run_windows.bat" (
    call run_windows.bat
) else (
    echo run_windows.bat not found, using direct launch...
    python console_manager.py
)
goto END

:QUICK_GUI
echo.
echo ⚙️ Starting Quick GUI Launcher...
echo.
python flutter_manager_gui.py
goto END

:CHECK_DEPS
echo.
echo 🔧 Checking dependencies...
echo.
python --version
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    goto PAUSE_END
)

python -c "import tkinter; print('✅ tkinter: OK')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ tkinter: NOT AVAILABLE
) else (
    echo ✅ tkinter: OK
)

python -c "import sqlite3; print('✅ sqlite3: OK')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ sqlite3: NOT AVAILABLE
) else (
    echo ✅ sqlite3: OK
)

echo.
echo Checking program files...
if exist "flutter_project_manager.py" (
    echo ✅ flutter_project_manager.py: OK
) else (
    echo ❌ flutter_project_manager.py: NOT FOUND
)

if exist "database_manager.py" (
    echo ✅ database_manager.py: OK
) else (
    echo ❌ database_manager.py: NOT FOUND
)

if exist "console_manager.py" (
    echo ✅ console_manager.py: OK
) else (
    echo ❌ console_manager.py: NOT FOUND
)

goto PAUSE_END

:SHOW_HELP
echo.
echo 📖 Flutter Project Manager - Help
echo =================================
echo.
echo Available launch modes:
echo.
echo 1. GUI Interface - Full graphical interface with all features
echo    - Project management with visual file tree
echo    - Command sequences with checkboxes
echo    - Snapshot management
echo    - Project comparison with statistics
echo.
echo 2. Console Interface - Terminal-based interface
echo    - Interactive menu system
echo    - Command-line arguments support
echo    - Colored output with emojis
echo    - Perfect for automation
echo.
echo 3. Quick GUI Launcher - Alternative GUI launcher
echo    - Simplified startup process
echo    - Dependency checking
echo    - Error handling
echo.
echo Files and directories:
echo - flutter_project_manager.py - Main GUI application
echo - console_manager.py - Console interface
echo - database_manager.py - Database operations
echo - project_analyzer.py - Project analysis
echo - snapshot_manager.py - Snapshot management
echo - flutter_manager.db - SQLite database (auto-created)
echo - snapshots/ - Snapshot storage directory
echo.
echo For more information, see README.md
echo.
goto PAUSE_END

:PAUSE_END
echo.
pause
goto MENU

:END
echo.
echo Program finished.
pause
goto MENU

:EXIT
echo.
echo Thank you for using Flutter Project Manager!
echo.
timeout /t 2 /nobreak >nul
exit /b 0
