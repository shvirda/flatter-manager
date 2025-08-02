@echo off
echo Flutter Project Manager - Console Mode (Windows)
echo ================================================
echo.
echo Choose action:
echo 1. Run GUI mode
echo 2. Create new Flutter project (console)
echo 3. Analyze project (console)
echo 4. Create snapshot (console)
echo 5. List snapshots
echo 6. Restore snapshot
echo 7. Compare projects
echo 8. Execute command sequence
echo 9. Backup settings
echo 0. Exit
echo.
set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" (
    echo Starting GUI mode...
    python flutter_project_manager.py
) else if "%choice%"=="2" (
    echo Creating new Flutter project...
    python console_manager.py create_project
) else if "%choice%"=="3" (
    echo Analyzing project...
    python console_manager.py analyze
) else if "%choice%"=="4" (
    echo Creating snapshot...
    python console_manager.py create_snapshot
) else if "%choice%"=="5" (
    echo Listing snapshots...
    python console_manager.py list_snapshots
) else if "%choice%"=="6" (
    echo Restoring snapshot...
    python console_manager.py restore_snapshot
) else if "%choice%"=="7" (
    echo Comparing projects...
    python console_manager.py compare_projects
) else if "%choice%"=="8" (
    echo Executing commands...
    python console_manager.py execute_commands
) else if "%choice%"=="9" (
    echo Backing up settings...
    python console_manager.py backup
) else if "%choice%"=="0" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice!
    pause
    goto :eof
)

pause
