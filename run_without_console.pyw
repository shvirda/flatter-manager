#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт запуска Flutter Project Manager без консольного окна
"""

import sys
import os

# Добавить текущую директорию в путь поиска модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Импорт и запуск главного приложения
try:
    from flutter_project_manager import FlutterProjectManager
    import tkinter as tk
    
    if __name__ == "__main__":
        root = tk.Tk()
        app = FlutterProjectManager(root)
        root.mainloop()
        
except ImportError as e:
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Ошибка импорта", f"Не удалось импортировать модули:\n{str(e)}")
    root.destroy()
    
except Exception as e:
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Ошибка запуска", f"Произошла ошибка при запуске приложения:\n{str(e)}")
    root.destroy()
