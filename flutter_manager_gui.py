#!/usr/bin/env python3
"""
Flutter Project Manager - Quick GUI Launcher
Простой альтернативный способ запуска GUI интерфейса
"""

import sys
import os
import subprocess

def check_dependencies():
    """Проверка наличия необходимых зависимостей"""
    try:
        import tkinter
        import sqlite3
        return True, "All dependencies available"
    except ImportError as e:
        return False, f"Missing dependency: {e}"

def main():
    print("🚀 Flutter Project Manager - Quick GUI Launcher")
    print("=" * 50)
    
    # Проверка наличия основного файла
    main_file = "flutter_project_manager.py"
    if not os.path.exists(main_file):
        print(f"❌ Error: {main_file} not found!")
        print("Make sure all program files are in the same directory.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Проверка зависимостей
    deps_ok, deps_msg = check_dependencies()
    if not deps_ok:
        print(f"❌ Error: {deps_msg}")
        print("\nRequired dependencies:")
        print("- tkinter (for GUI)")
        print("- sqlite3 (for database)")
        print("\nPlease install missing dependencies and try again.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("✅ Dependencies check passed")
    print("🎯 Starting Flutter Project Manager GUI...")
    print()
    
    try:
        # Запуск основного приложения
        if sys.platform.startswith('win'):
            subprocess.run([sys.executable, main_file], check=True)
        else:
            subprocess.run([sys.executable, main_file], check=True)
        
        print("\n✅ Application closed successfully.")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running application: {e}")
        print("Please check the error messages above.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user.")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
