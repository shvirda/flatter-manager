#!/bin/bash

echo "=========================================="
echo "Flutter Project Manager - GUI Launcher"
echo "=========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored text
print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-tk"
    echo "  CentOS/RHEL: sudo yum install python3 tkinter"
    echo "  Arch Linux: sudo pacman -S python python-tk"
    exit 1
fi

# Check if main GUI file exists
if [ ! -f "flutter_project_manager.py" ]; then
    print_error "flutter_project_manager.py not found!"
    echo "Make sure all program files are in the same directory."
    exit 1
fi

# Display Python version
echo "Checking Python installation..."
python3 --version

# Check for tkinter availability
echo "Checking GUI libraries..."
if python3 -c "import tkinter; print('tkinter is available')" 2>/dev/null; then
    print_success "tkinter is available"
else
    print_error "tkinter is not available!"
    echo "tkinter is required for GUI interface."
    echo "Install it using:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "  CentOS/RHEL: sudo yum install tkinter"
    echo "  Arch Linux: sudo pacman -S tk"
    exit 1
fi

# Check for sqlite3 availability
if python3 -c "import sqlite3; print('sqlite3 is available')" 2>/dev/null; then
    print_success "sqlite3 is available"
else
    print_error "sqlite3 is not available!"
    echo "sqlite3 should be included with Python, please check your Python installation."
    exit 1
fi

# Check for other required modules
echo "Checking additional modules..."
if python3 -c "import os, shutil, subprocess, tempfile, hashlib, difflib, zipfile, json, argparse" 2>/dev/null; then
    print_success "All required modules are available"
else
    print_error "Some required modules are missing!"
    echo "Please check your Python installation."
    exit 1
fi

echo
print_success "All dependencies are satisfied"
echo "Starting Flutter Project Manager GUI..."
echo

# Make the script executable if it's not
if [ ! -x "flutter_project_manager.py" ]; then
    chmod +x flutter_project_manager.py 2>/dev/null
fi

# Start the GUI application
python3 flutter_project_manager.py

# Check if there was an error
if [ $? -ne 0 ]; then
    echo
    print_error "The application encountered an error!"
    echo "Please check the error messages above."
    read -p "Press Enter to exit..."
    exit 1
fi

echo
print_success "Application closed successfully."
read -p "Press Enter to exit..."
