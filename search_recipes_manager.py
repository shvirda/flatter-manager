#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер рецептов поиска для Flutter Project Manager
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class SearchRecipesManager:
    """Менеджер для сохранения и загрузки рецептов поиска"""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.recipes_file = "search_recipes.json"
        self.recipes = self.load_recipes()
    
    def load_recipes(self) -> Dict:
        """Загрузка рецептов поиска из файла"""
        try:
            if os.path.exists(self.recipes_file):
                with open(self.recipes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки рецептов поиска: {e}")
        
        # Возвращаем рецепты по умолчанию
        return {
            "recipes": [
                {
                    "name": "Поиск Dart файлов",
                    "description": "Поиск по Dart файлам проекта",
                    "query": "*.dart",
                    "file_patterns": ["*.dart"],
                    "exclude_patterns": [".dart_tool", "build"],
                    "case_sensitive": False,
                    "use_regex": False,
                    "filename_only": True,
                    "created_date": datetime.now().isoformat(),
                    "usage_count": 0
                },
                {
                    "name": "Поиск TODO комментариев",
                    "description": "Поиск TODO, FIXME, HACK комментариев",
                    "query": "(TODO|FIXME|HACK)",
                    "file_patterns": ["*.dart", "*.py", "*.js", "*.ts"],
                    "exclude_patterns": [".git", "node_modules", ".dart_tool", "build"],
                    "case_sensitive": False,
                    "use_regex": True,
                    "filename_only": False,
                    "created_date": datetime.now().isoformat(),
                    "usage_count": 0
                },
                {
                    "name": "Поиск конфигурационных файлов",
                    "description": "Поиск YAML, JSON конфигурационных файлов",
                    "query": "*",
                    "file_patterns": ["*.yaml", "*.yml", "*.json"],
                    "exclude_patterns": [".git", "node_modules", ".dart_tool", "build"],
                    "case_sensitive": False,
                    "use_regex": False,
                    "filename_only": True,
                    "created_date": datetime.now().isoformat(),
                    "usage_count": 0
                }
            ]
        }
    
    def save_recipes(self):
        """Сохранение рецептов поиска в файл"""
        try:
            with open(self.recipes_file, 'w', encoding='utf-8') as f:
                json.dump(self.recipes, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения рецептов поиска: {e}")
            return False
    
    def get_recipes(self) -> List[Dict]:
        """Получение списка всех рецептов"""
        return self.recipes.get("recipes", [])
    
    def add_recipe(self, name: str, description: str, query: str, 
                   file_patterns: List[str] = None, exclude_patterns: List[str] = None,
                   case_sensitive: bool = False, use_regex: bool = False, 
                   filename_only: bool = False) -> bool:
        """Добавление нового рецепта поиска"""
        try:
            recipe = {
                "name": name,
                "description": description,
                "query": query,
                "file_patterns": file_patterns or ["*"],
                "exclude_patterns": exclude_patterns or [],
                "case_sensitive": case_sensitive,
                "use_regex": use_regex,
                "filename_only": filename_only,
                "created_date": datetime.now().isoformat(),
                "usage_count": 0
            }
            
            self.recipes["recipes"].append(recipe)
            return self.save_recipes()
        except Exception as e:
            print(f"Ошибка добавления рецепта: {e}")
            return False
    
    def update_recipe(self, index: int, name: str, description: str, query: str,
                      file_patterns: List[str] = None, exclude_patterns: List[str] = None,
                      case_sensitive: bool = False, use_regex: bool = False,
                      filename_only: bool = False) -> bool:
        """Обновление существующего рецепта"""
        try:
            if 0 <= index < len(self.recipes["recipes"]):
                recipe = self.recipes["recipes"][index]
                recipe.update({
                    "name": name,
                    "description": description,
                    "query": query,
                    "file_patterns": file_patterns or ["*"],
                    "exclude_patterns": exclude_patterns or [],
                    "case_sensitive": case_sensitive,
                    "use_regex": use_regex,
                    "filename_only": filename_only
                })
                return self.save_recipes()
            return False
        except Exception as e:
            print(f"Ошибка обновления рецепта: {e}")
            return False
    
    def delete_recipe(self, index: int) -> bool:
        """Удаление рецепта по индексу"""
        try:
            if 0 <= index < len(self.recipes["recipes"]):
                del self.recipes["recipes"][index]
                return self.save_recipes()
            return False
        except Exception as e:
            print(f"Ошибка удаления рецепта: {e}")
            return False
    
    def get_recipe(self, index: int) -> Optional[Dict]:
        """Получение рецепта по индексу"""
        try:
            if 0 <= index < len(self.recipes["recipes"]):
                return self.recipes["recipes"][index]
            return None
        except Exception as e:
            print(f"Ошибка получения рецепта: {e}")
            return None
    
    def increment_usage(self, index: int):
        """Увеличение счетчика использования рецепта"""
        try:
            if 0 <= index < len(self.recipes["recipes"]):
                self.recipes["recipes"][index]["usage_count"] += 1
                self.save_recipes()
        except Exception as e:
            print(f"Ошибка увеличения счетчика: {e}")


class SearchRecipeDialog:
    """Диалог для создания/редактирования рецептов поиска"""
    
    def __init__(self, parent, recipes_manager, recipe_index=None, callback=None):
        self.recipes_manager = recipes_manager
        self.recipe_index = recipe_index
        self.callback = callback
        
        import tkinter as tk
        from tkinter import ttk
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Рецепт поиска" if recipe_index is None else "Редактировать рецепт")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        
        # Сделать диалог модальным
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_interface()
        
        # Если редактируем существующий рецепт
        if recipe_index is not None:
            self.load_recipe()
        
        # Центрировать диалог
        self.center_dialog()
    
    def create_interface(self):
        """Создание интерфейса диалога"""
        import tkinter as tk
        from tkinter import ttk
        
        # Главный фрейм
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Название и описание
        info_frame = ttk.LabelFrame(main_frame, text="Основная информация")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text="Название:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = ttk.Entry(info_frame, width=50)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(info_frame, text="Описание:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.desc_entry = ttk.Entry(info_frame, width=50)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Параметры поиска
        search_frame = ttk.LabelFrame(main_frame, text="Параметры поиска")
        search_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(search_frame, text="Поисковый запрос:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.query_entry = ttk.Entry(search_frame, width=50)
        self.query_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Паттерны файлов
        ttk.Label(search_frame, text="Шаблоны файлов:").grid(row=1, column=0, sticky="nw", padx=5, pady=5)
        self.file_patterns_text = tk.Text(search_frame, height=3, width=50)
        self.file_patterns_text.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(search_frame, text="Исключить шаблоны:").grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        self.exclude_patterns_text = tk.Text(search_frame, height=3, width=50)
        self.exclude_patterns_text.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        search_frame.grid_columnconfigure(1, weight=1)
        
        # Опции поиска
        options_frame = ttk.LabelFrame(main_frame, text="Опции поиска")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.case_sensitive_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Учитывать регистр", 
                       variable=self.case_sensitive_var).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.use_regex_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Регулярные выражения", 
                       variable=self.use_regex_var).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        self.filename_only_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Только имена файлов", 
                       variable=self.filename_only_var).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        # Кнопки
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Сохранить", command=self.save_recipe).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
        # Подсказки
        hints_frame = ttk.LabelFrame(main_frame, text="Подсказки")
        hints_frame.pack(fill=tk.X, pady=(10, 0))
        
        hints_text = """• Шаблоны файлов: по одному на строку (например: *.dart, *.py)
• Исключить шаблоны: директории/файлы для игнорирования
• Регулярные выражения: для сложных поисковых запросов
• Только имена файлов: поиск только по именам, игнорируя содержимое"""
        
        ttk.Label(hints_frame, text=hints_text, font=('Arial', 8), foreground='gray').pack(padx=5, pady=5)
    
    def load_recipe(self):
        """Загрузка данных рецепта для редактирования"""
        recipe = self.recipes_manager.get_recipe(self.recipe_index)
        if recipe:
            self.name_entry.insert(0, recipe.get("name", ""))
            self.desc_entry.insert(0, recipe.get("description", ""))
            self.query_entry.insert(0, recipe.get("query", ""))
            
            # Загрузка паттернов файлов
            file_patterns = recipe.get("file_patterns", [])
            self.file_patterns_text.insert("1.0", "\n".join(file_patterns))
            
            exclude_patterns = recipe.get("exclude_patterns", [])
            self.exclude_patterns_text.insert("1.0", "\n".join(exclude_patterns))
            
            # Загрузка опций
            self.case_sensitive_var.set(recipe.get("case_sensitive", False))
            self.use_regex_var.set(recipe.get("use_regex", False))
            self.filename_only_var.set(recipe.get("filename_only", False))
    
    def save_recipe(self):
        """Сохранение рецепта"""
        import tkinter.messagebox as messagebox
        
        name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip()
        query = self.query_entry.get().strip()
        
        if not name or not query:
            messagebox.showwarning("Предупреждение", "Заполните название и поисковый запрос!")
            return
        
        # Получение паттернов
        file_patterns_text = self.file_patterns_text.get("1.0", "end-1c").strip()
        file_patterns = [p.strip() for p in file_patterns_text.split('\n') if p.strip()] or ["*"]
        
        exclude_patterns_text = self.exclude_patterns_text.get("1.0", "end-1c").strip()
        exclude_patterns = [p.strip() for p in exclude_patterns_text.split('\n') if p.strip()]
        
        # Получение опций
        case_sensitive = self.case_sensitive_var.get()
        use_regex = self.use_regex_var.get()
        filename_only = self.filename_only_var.get()
        
        # Сохранение
        if self.recipe_index is None:
            # Создание нового рецепта
            success = self.recipes_manager.add_recipe(
                name, description, query, file_patterns, exclude_patterns,
                case_sensitive, use_regex, filename_only
            )
        else:
            # Обновление существующего рецепта
            success = self.recipes_manager.update_recipe(
                self.recipe_index, name, description, query, file_patterns, exclude_patterns,
                case_sensitive, use_regex, filename_only
            )
        
        if success:
            messagebox.showinfo("Успех", "Рецепт поиска сохранен!")
            if self.callback:
                self.callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("Ошибка", "Ошибка сохранения рецепта!")
    
    def center_dialog(self):
        """Центрирование диалога"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
