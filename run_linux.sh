#!/bin/bash

echo "Flutter Project Manager - Console Mode (Linux)"
echo "==============================================="
echo
echo "Choose action:"
echo "1. Run GUI mode"
echo "2. Create new Flutter project (console)"
echo "3. Analyze project (console)"
echo "4. Create snapshot (console)"
echo "5. List snapshots"
echo "6. Restore snapshot"
echo "7. Compare projects"
echo "8. Execute command sequence"
echo "9. Backup settings"
echo "0. Exit"
echo
read -p "Enter your choice (0-9): " choice

case $choice in
    1)
        echo "Starting GUI mode..."
        python3 flutter_project_manager.py
        ;;
    2)
        echo "Creating new Flutter project..."
        python3 console_manager.py create_project
        ;;
    3)
        echo "Analyzing project..."
        python3 console_manager.py analyze
        ;;
    4)
        echo "Creating snapshot..."
        python3 console_manager.py create_snapshot
        ;;
    5)
        echo "Listing snapshots..."
        python3 console_manager.py list_snapshots
        ;;
    6)
        echo "Restoring snapshot..."
        python3 console_manager.py restore_snapshot
        ;;
    7)
        echo "Comparing projects..."
        python3 console_manager.py compare_projects
        ;;
    8)
        echo "Executing commands..."
        python3 console_manager.py execute_commands
        ;;
    9)
        echo "Backing up settings..."
        python3 console_manager.py backup
        ;;
    0)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice!"
        ;;
esac

read -p "Press Enter to continue..."
