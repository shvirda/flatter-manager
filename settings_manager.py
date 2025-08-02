import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import platform

class SettingsManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.settings_file = "app_settings.json"
        self.load_settings()
    
    def load_settings(self):
        """Загрузка настроек из файла"""
        default_settings = {
            "editors": self.get_default_editors(),
            "default_editor": None,
            "hotkeys": {
                "select_directory": "Ctrl+O",
                "create_project": "Ctrl+N", 
                "create_snapshot": "Ctrl+S",
                "analyze_changes": "Ctrl+A",
                "open_file": "Enter",
                "refresh": "F5",
                "exit": "Ctrl+Q",
                "search_files": "Ctrl+F",
                "save_file": "Ctrl+S",
                "copy": "Ctrl+C",
                "paste": "Ctrl+V",
                "undo": "Ctrl+Z",
                "redo": "Ctrl+Y",
                "select_all": "Ctrl+A",
                "find_replace": "Ctrl+H"
            },
            "custom_hotkeys": {}
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                # Обновляем default_settings с загруженными настройками
                self.settings = {**default_settings, **loaded_settings}
                # Обеспечиваем наличие всех горячих клавиш
                if "hotkeys" in loaded_settings:
                    self.settings["hotkeys"] = {**default_settings["hotkeys"], **loaded_settings["hotkeys"]}
            else:
                self.settings = default_settings
                self.save_settings()
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
            self.settings = default_settings
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
            return False
    
    def get_default_editors(self):
        """Получение списка редакторов по умолчанию в зависимости от ОС"""
        system = platform.system().lower()
        
        if system == "windows":
            editors = [
                {"name": "Visual Studio Code", "path": "code", "args": ""},
                {"name": "Notepad++", "path": "notepad++", "args": ""},
                {"name": "Sublime Text", "path": "subl", "args": ""},
                {"name": "Atom", "path": "atom", "args": ""},
                {"name": "Notepad", "path": "notepad", "args": ""},
                {"name": "WordPad", "path": "write", "args": ""}
            ]
        elif system == "darwin":  # macOS
            editors = [
                {"name": "Visual Studio Code", "path": "code", "args": ""},
                {"name": "Sublime Text", "path": "subl", "args": ""},
                {"name": "Atom", "path": "atom", "args": ""},
                {"name": "TextEdit", "path": "open -a TextEdit", "args": ""},
                {"name": "Vim", "path": "vim", "args": ""}
            ]
        else:  # Linux
            editors = [
                {"name": "Visual Studio Code", "path": "code", "args": ""},
                {"name": "Sublime Text", "path": "subl", "args": ""},
                {"name": "Atom", "path": "atom", "args": ""},
                {"name": "Gedit", "path": "gedit", "args": ""},
                {"name": "Nano", "path": "nano", "args": ""},
                {"name": "Vim", "path": "vim", "args": ""}
            ]
        
        return editors
    
    def get_editors(self):
        """Получение списка редакторов"""
        return self.settings.get("editors", [])
    
    def add_editor(self, name, path, args=""):
        """Добавление нового редактора"""
        editors = self.get_editors()
        editors.append({"name": name, "path": path, "args": args})
        self.settings["editors"] = editors
        return self.save_settings()
    
    def remove_editor(self, index):
        """Удаление редактора по индексу"""
        editors = self.get_editors()
        if 0 <= index < len(editors):
            del editors[index]
            self.settings["editors"] = editors
            return self.save_settings()
        return False
    
    def set_default_editor(self, index):
        """Установка редактора по умолчанию"""
        editors = self.get_editors()
        if 0 <= index < len(editors):
            self.settings["default_editor"] = index
            return self.save_settings()
        return False
    
    def get_default_editor(self):
        """Получение редактора по умолчанию"""
        default_index = self.settings.get("default_editor")
        editors = self.get_editors()
        if default_index is not None and 0 <= default_index < len(editors):
            return editors[default_index]
        return None
    
    def open_file_with_editor(self, file_path, editor_index=None):
        """Открытие файла в редакторе"""
        editors = self.get_editors()
        
        if editor_index is not None:
            if 0 <= editor_index < len(editors):
                editor = editors[editor_index]
            else:
                return False
        else:
            editor = self.get_default_editor()
            if not editor:
                # Если нет редактора по умолчанию, используем системный
                return self.open_file_system_default(file_path)
        
        try:
            cmd = [editor["path"]]
            if editor["args"]:
                cmd.extend(editor["args"].split())
            cmd.append(file_path)
            
            subprocess.Popen(cmd, shell=True)
            return True
        except Exception as e:
            print(f"Ошибка открытия файла: {e}")
            return self.open_file_system_default(file_path)
    
    def open_file_system_default(self, file_path):
        """Открытие файла системным редактором по умолчанию"""
        try:
            system = platform.system().lower()
            if system == "windows":
                os.startfile(file_path)
            elif system == "darwin":
                subprocess.run(["open", file_path])
            else:
                subprocess.run(["xdg-open", file_path])
            return True
        except Exception as e:
            print(f"Ошибка открытия файла системным редактором: {e}")
            return False
    
    def get_hotkeys(self):
        """Получение горячих клавиш"""
        return self.settings.get("hotkeys", {})
    
    def get_custom_hotkeys(self):
        """Получение пользовательских горячих клавиш"""
        return self.settings.get("custom_hotkeys", {})
    
    def add_custom_hotkey(self, name, hotkey, command="", description=""):
        """Добавление пользовательской горячей клавиши"""
        if "custom_hotkeys" not in self.settings:
            self.settings["custom_hotkeys"] = {}
        
        self.settings["custom_hotkeys"][name] = {
            "hotkey": hotkey,
            "command": command,
            "description": description
        }
        return self.save_settings()
    
    def remove_custom_hotkey(self, name):
        """Удаление пользовательской горячей клавиши"""
        if "custom_hotkeys" in self.settings and name in self.settings["custom_hotkeys"]:
            del self.settings["custom_hotkeys"][name]
            return self.save_settings()
        return False
    
    def update_custom_hotkey(self, name, hotkey, command="", description=""):
        """Обновление пользовательской горячей клавиши"""
        if "custom_hotkeys" not in self.settings:
            self.settings["custom_hotkeys"] = {}
        
        self.settings["custom_hotkeys"][name] = {
            "hotkey": hotkey,
            "command": command,
            "description": description
        }
        return self.save_settings()
    
    def get_all_hotkeys(self):
        """Получение всех горячих клавиш (стандартных и пользовательских)"""
        all_hotkeys = {}
        
        # Стандартные горячие клавиши
        hotkeys = self.get_hotkeys()
        for action, hotkey in hotkeys.items():
            all_hotkeys[hotkey] = {
                "type": "system",
                "action": action,
                "description": self.get_action_description(action)
            }
        
        # Пользовательские горячие клавиши
        custom_hotkeys = self.get_custom_hotkeys()
        for name, data in custom_hotkeys.items():
            all_hotkeys[data["hotkey"]] = {
                "type": "custom",
                "name": name,
                "command": data.get("command", ""),
                "description": data.get("description", "")
            }
        
        return all_hotkeys
    
    def get_action_description(self, action):
        """Получение описания системного действия"""
        descriptions = {
            "select_directory": "Выбор директории",
            "create_project": "Создать новый проект",
            "create_snapshot": "Создать снапшот",
            "analyze_changes": "Анализ изменений",
            "open_file": "Открыть файл",
            "refresh": "Обновить",
            "exit": "Выход",
            "search_files": "Поиск файлов",
            "save_file": "Сохранить файл",
            "copy": "Копировать",
            "paste": "Вставить",
            "undo": "Отменить",
            "redo": "Повторить",
            "select_all": "Выделить всё",
            "find_replace": "Найти и заменить"
        }
        return descriptions.get(action, action)
    
    def set_hotkey(self, action, hotkey):
        """Установка горячей клавиши для действия"""
        if "hotkeys" not in self.settings:
            self.settings["hotkeys"] = {}
        self.settings["hotkeys"][action] = hotkey
        return self.save_settings()
    
    def parse_hotkey(self, hotkey_string):
        """Парсинг строки горячей клавиши в формат tkinter"""
        # Преобразование в нижний регистр для унификации
        hotkey = hotkey_string.lower()
        
        # Замена названий модификаторов
        replacements = {
            "ctrl": "Control",
            "alt": "Alt", 
            "shift": "Shift",
            "cmd": "Command",  # для macOS
            "super": "Super"   # для Linux
        }
        
        for old, new in replacements.items():
            hotkey = hotkey.replace(old, new)
        
        # Обработка специальных клавиш
        special_keys = {
            "enter": "Return",
            "space": "space",
            "tab": "Tab",
            "esc": "Escape",
            "escape": "Escape",
            "del": "Delete",
            "delete": "Delete",
            "backspace": "BackSpace",
            "home": "Home",
            "end": "End",
            "pageup": "Prior",
            "pagedown": "Next",
            "insert": "Insert",
            "f1": "F1", "f2": "F2", "f3": "F3", "f4": "F4",
            "f5": "F5", "f6": "F6", "f7": "F7", "f8": "F8",
            "f9": "F9", "f10": "F10", "f11": "F11", "f12": "F12",
            "up": "Up", "down": "Down", "left": "Left", "right": "Right",
            "print": "Print", "scroll": "Scroll_Lock", "pause": "Pause",
            "numlock": "Num_Lock", "capslock": "Caps_Lock"
        }
        
        for old, new in special_keys.items():
            if old in hotkey:
                hotkey = hotkey.replace(old, new)
        
        # Замена + на -
        hotkey = hotkey.replace("+", "-")
        
        return f"<{hotkey}>"
    
    def validate_hotkey(self, hotkey_string):
        """Проверка корректности горячей клавиши"""
        try:
            parsed = self.parse_hotkey(hotkey_string)
            # Простая проверка формата
            return parsed.startswith("<") and parsed.endswith(">") and "-" in parsed
        except:
            return False


class EditorSettingsDialog:
    def __init__(self, parent, settings_manager):
        self.parent = parent
        self.settings_manager = settings_manager
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройки редакторов")
        self.dialog.geometry("700x500")
        self.dialog.resizable(True, True)
        
        # Сделать диалог модальным
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_interface()
        self.refresh_editors_list()
        
        # Центрировать диалог
        self.center_dialog()
    
    def center_dialog(self):
        """Центрирование диалога на экране"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_interface(self):
        # Заголовок
        title_label = ttk.Label(self.dialog, text="Настройка редакторов", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(10, 5))
        
        # Основной фрейм
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Список редакторов
        editors_frame = ttk.LabelFrame(main_frame, text="Доступные редакторы")
        editors_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview для редакторов
        columns = ("Название", "Путь", "Аргументы", "По умолчанию")
        self.editors_tree = ttk.Treeview(editors_frame, columns=columns, show="headings", height=10)
        
        # Настройка заголовков
        self.editors_tree.heading("Название", text="Название")
        self.editors_tree.heading("Путь", text="Путь к исполняемому файлу")
        self.editors_tree.heading("Аргументы", text="Аргументы")
        self.editors_tree.heading("По умолчанию", text="По умолчанию")
        
        # Настройка ширины столбцов
        self.editors_tree.column("Название", width=150, minwidth=100)
        self.editors_tree.column("Путь", width=250, minwidth=150)
        self.editors_tree.column("Аргументы", width=100, minwidth=80)
        self.editors_tree.column("По умолчанию", width=100, minwidth=80)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(editors_frame, orient="vertical", command=self.editors_tree.yview)
        self.editors_tree.configure(yscrollcommand=scrollbar.set)
        
        self.editors_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления редакторами
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="➕ Добавить редактор", command=self.add_editor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="✏️ Редактировать", command=self.edit_editor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="🗑️ Удалить", command=self.remove_editor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="⭐ Сделать по умолчанию", command=self.set_default_editor).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="🔍 Найти редакторы", command=self.auto_detect_editors).pack(side=tk.LEFT)
        
        # Кнопки диалога
        dialog_buttons_frame = ttk.Frame(main_frame)
        dialog_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(dialog_buttons_frame, text="💾 Сохранить", command=self.save_and_close).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(dialog_buttons_frame, text="❌ Отмена", command=self.cancel).pack(side=tk.RIGHT)
    
    def refresh_editors_list(self):
        """Обновление списка редакторов"""
        # Очистка списка
        for item in self.editors_tree.get_children():
            self.editors_tree.delete(item)
        
        # Заполнение списка
        editors = self.settings_manager.get_editors()
        default_editor_index = self.settings_manager.settings.get("default_editor")
        
        for i, editor in enumerate(editors):
            is_default = "✅ Да" if i == default_editor_index else "❌ Нет"
            self.editors_tree.insert("", tk.END, values=(
                editor["name"],
                editor["path"],
                editor.get("args", ""),
                is_default
            ), tags=(i,))
    
    def add_editor(self):
        """Добавление нового редактора"""
        AddEditorDialog(self.dialog, self.settings_manager, self.refresh_editors_list)
    
    def edit_editor(self):
        """Редактирование выбранного редактора"""
        selection = self.editors_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите редактор для редактирования")
            return
        
        item = self.editors_tree.item(selection[0])
        editor_index = int(item['tags'][0])
        editors = self.settings_manager.get_editors()
        
        if 0 <= editor_index < len(editors):
            editor = editors[editor_index]
            EditEditorDialog(self.dialog, self.settings_manager, editor_index, editor, self.refresh_editors_list)
    
    def remove_editor(self):
        """Удаление выбранного редактора"""
        selection = self.editors_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите редактор для удаления")
            return
        
        item = self.editors_tree.item(selection[0])
        editor_index = int(item['tags'][0])
        editor_name = item['values'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить редактор '{editor_name}'?"):
            if self.settings_manager.remove_editor(editor_index):
                self.refresh_editors_list()
                messagebox.showinfo("Успех", "Редактор удален")
            else:
                messagebox.showerror("Ошибка", "Ошибка удаления редактора")
    
    def set_default_editor(self):
        """Установка редактора по умолчанию"""
        selection = self.editors_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите редактор для установки по умолчанию")
            return
        
        item = self.editors_tree.item(selection[0])
        editor_index = int(item['tags'][0])
        
        if self.settings_manager.set_default_editor(editor_index):
            self.refresh_editors_list()
            messagebox.showinfo("Успех", "Редактор по умолчанию установлен")
        else:
            messagebox.showerror("Ошибка", "Ошибка установки редактора по умолчанию")
    
    def auto_detect_editors(self):
        """Автоматическое обнаружение редакторов"""
        detected_count = 0
        editors = self.settings_manager.get_editors()
        existing_paths = {editor["path"] for editor in editors}
        
        # Проверка стандартных редакторов
        test_editors = self.settings_manager.get_default_editors()
        
        for editor in test_editors:
            if editor["path"] not in existing_paths:
                try:
                    # Проверка доступности команды
                    subprocess.run([editor["path"], "--version"], 
                                 capture_output=True, timeout=5)
                    self.settings_manager.add_editor(editor["name"], editor["path"], editor.get("args", ""))
                    detected_count += 1
                except:
                    continue
        
        if detected_count > 0:
            self.refresh_editors_list()
            messagebox.showinfo("Успех", f"Обнаружено и добавлено {detected_count} редакторов")
        else:
            messagebox.showinfo("Информация", "Новые редакторы не обнаружены")
    
    def save_and_close(self):
        """Сохранение и закрытие диалога"""
        self.dialog.grab_release()
        self.dialog.destroy()
    
    def cancel(self):
        """Отмена изменений"""
        self.dialog.grab_release()
        self.dialog.destroy()


class AddEditorDialog:
    def __init__(self, parent, settings_manager, refresh_callback):
        self.settings_manager = settings_manager
        self.refresh_callback = refresh_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавить редактор")
        self.dialog.geometry("500x300")
        self.dialog.resizable(False, False)
        
        # Сделать диалог модальным
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_interface()
        self.center_dialog()
    
    def center_dialog(self):
        """Центрирование диалога"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_interface(self):
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Название редактора:").pack(anchor="w", pady=(0, 5))
        self.name_entry = ttk.Entry(main_frame, width=50)
        self.name_entry.pack(fill="x", pady=(0, 15))
        
        ttk.Label(main_frame, text="Путь к исполняемому файлу:").pack(anchor="w", pady=(0, 5))
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill="x", pady=(0, 15))
        
        self.path_entry = ttk.Entry(path_frame)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(path_frame, text="Обзор...", command=self.browse_executable).pack(side="right")
        
        ttk.Label(main_frame, text="Аргументы командной строки (необязательно):").pack(anchor="w", pady=(0, 5))
        self.args_entry = ttk.Entry(main_frame, width=50)
        self.args_entry.pack(fill="x", pady=(0, 20))
        
        # Кнопки
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x")
        
        ttk.Button(buttons_frame, text="Добавить", command=self.add_editor).pack(side="right", padx=(5, 0))
        ttk.Button(buttons_frame, text="Отмена", command=self.cancel).pack(side="right")
    
    def browse_executable(self):
        """Выбор исполняемого файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите исполняемый файл редактора",
            filetypes=[
                ("Исполняемые файлы", "*.exe" if platform.system() == "Windows" else "*"),
                ("Все файлы", "*.*")
            ]
        )
        if file_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)
            
            # Автоматическое заполнение названия
            if not self.name_entry.get():
                name = os.path.splitext(os.path.basename(file_path))[0]
                self.name_entry.insert(0, name.title())
    
    def add_editor(self):
        """Добавление редактора"""
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip()
        args = self.args_entry.get().strip()
        
        if not name or not path:
            messagebox.showwarning("Предупреждение", "Заполните название и путь к редактору")
            return
        
        if self.settings_manager.add_editor(name, path, args):
            messagebox.showinfo("Успех", "Редактор добавлен")
            self.refresh_callback()
            self.dialog.grab_release()
            self.dialog.destroy()
        else:
            messagebox.showerror("Ошибка", "Ошибка добавления редактора")
    
    def cancel(self):
        """Отмена"""
        self.dialog.grab_release()
        self.dialog.destroy()


class EditEditorDialog:
    def __init__(self, parent, settings_manager, editor_index, editor_data, refresh_callback):
        self.settings_manager = settings_manager
        self.editor_index = editor_index
        self.refresh_callback = refresh_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Редактировать редактор")
        self.dialog.geometry("500x300")
        self.dialog.resizable(False, False)
        
        # Сделать диалог модальным
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_interface()
        self.load_editor_data(editor_data)
        self.center_dialog()
    
    def center_dialog(self):
        """Центрирование диалога"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_interface(self):
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Название редактора:").pack(anchor="w", pady=(0, 5))
        self.name_entry = ttk.Entry(main_frame, width=50)
        self.name_entry.pack(fill="x", pady=(0, 15))
        
        ttk.Label(main_frame, text="Путь к исполняемому файлу:").pack(anchor="w", pady=(0, 5))
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill="x", pady=(0, 15))
        
        self.path_entry = ttk.Entry(path_frame)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(path_frame, text="Обзор...", command=self.browse_executable).pack(side="right")
        
        ttk.Label(main_frame, text="Аргументы командной строки:").pack(anchor="w", pady=(0, 5))
        self.args_entry = ttk.Entry(main_frame, width=50)
        self.args_entry.pack(fill="x", pady=(0, 20))
        
        # Кнопки
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x")
        
        ttk.Button(buttons_frame, text="Сохранить", command=self.save_editor).pack(side="right", padx=(5, 0))
        ttk.Button(buttons_frame, text="Отмена", command=self.cancel).pack(side="right")
    
    def load_editor_data(self, editor_data):
        """Загрузка данных редактора"""
        self.name_entry.insert(0, editor_data["name"])
        self.path_entry.insert(0, editor_data["path"])
        self.args_entry.insert(0, editor_data.get("args", ""))
    
    def browse_executable(self):
        """Выбор исполняемого файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите исполняемый файл редактора",
            filetypes=[
                ("Исполняемые файлы", "*.exe" if platform.system() == "Windows" else "*"),
                ("Все файлы", "*.*")
            ]
        )
        if file_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)
    
    def save_editor(self):
        """Сохранение изменений редактора"""
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip()
        args = self.args_entry.get().strip()
        
        if not name or not path:
            messagebox.showwarning("Предупреждение", "Заполните название и путь к редактору")
            return
        
        # Обновление данных редактора
        editors = self.settings_manager.get_editors()
        if 0 <= self.editor_index < len(editors):
            editors[self.editor_index] = {"name": name, "path": path, "args": args}
            self.settings_manager.settings["editors"] = editors
            
            if self.settings_manager.save_settings():
                messagebox.showinfo("Успех", "Редактор обновлен")
                self.refresh_callback()
                self.dialog.grab_release()
                self.dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Ошибка сохранения редактора")
    
    def cancel(self):
        """Отмена"""
        self.dialog.grab_release()
        self.dialog.destroy()


class AdvancedHotkeySettingsDialog:
    """Расширенный диалог для управления всеми горячими клавишами"""
    
    def __init__(self, parent, settings_manager):
        self.parent = parent
        self.settings_manager = settings_manager
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Расширенные настройки горячих клавиш")
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)
        
        # Сделать диалог модальным
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_interface()
        self.refresh_hotkeys_list()
        self.center_dialog()
    
    def center_dialog(self):
        """Центрирование диалога"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_interface(self):
        # Заголовок
        title_label = ttk.Label(self.dialog, text="Управление горячими клавишами", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(10, 5))
        
        # Notebook для вкладок
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Вкладка системных горячих клавиш
        system_frame = ttk.Frame(notebook)
        notebook.add(system_frame, text="🔧 Системные клавиши")
        self.create_system_hotkeys_tab(system_frame)
        
        # Вкладка пользовательских горячих клавиш
        custom_frame = ttk.Frame(notebook)
        notebook.add(custom_frame, text="🎯 Пользовательские клавиши")
        self.create_custom_hotkeys_tab(custom_frame)
        
        # Вкладка просмотра всех горячих клавиш
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="📋 Обзор всех клавиш")
        self.create_overview_tab(overview_frame)
        
        # Кнопки диалога
        buttons_frame = ttk.Frame(self.dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        ttk.Button(buttons_frame, text="💾 Сохранить и закрыть", command=self.save_and_close).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(buttons_frame, text="❌ Отмена", command=self.cancel).pack(side=tk.RIGHT)
        ttk.Button(buttons_frame, text="🔄 Обновить", command=self.refresh_hotkeys_list).pack(side=tk.LEFT)
    
    def create_system_hotkeys_tab(self, parent_frame):
        """Создание вкладки системных горячих клавиш"""
        # Список системных горячих клавиш
        system_frame = ttk.LabelFrame(parent_frame, text="Системные горячие клавиши")
        system_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Действие", "Описание", "Горячая клавиша")
        self.system_tree = ttk.Treeview(system_frame, columns=columns, show="headings", height=12)
        
        # Настройка заголовков
        self.system_tree.heading("Действие", text="Action ID")
        self.system_tree.heading("Описание", text="Описание")
        self.system_tree.heading("Горячая клавиша", text="Горячая клавиша")
        
        # Настройка ширины столбцов
        self.system_tree.column("Действие", width=150, minwidth=100)
        self.system_tree.column("Описание", width=250, minwidth=150)
        self.system_tree.column("Горячая клавиша", width=150, minwidth=100)
        
        # Скроллбар для системных клавиш
        system_scrollbar = ttk.Scrollbar(system_frame, orient="vertical", command=self.system_tree.yview)
        self.system_tree.configure(yscrollcommand=system_scrollbar.set)
        
        self.system_tree.pack(side="left", fill="both", expand=True)
        system_scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления системными клавишами
        system_buttons_frame = ttk.Frame(parent_frame)
        system_buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(system_buttons_frame, text="✏️ Изменить", command=self.edit_system_hotkey).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(system_buttons_frame, text="🔄 Сбросить", command=self.reset_system_hotkey).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(system_buttons_frame, text="🔄 Сбросить все", command=self.reset_all_system_hotkeys).pack(side=tk.LEFT)
    
    def create_custom_hotkeys_tab(self, parent_frame):
        """Создание вкладки пользовательских горячих клавиш"""
        # Список пользовательских горячих клавиш
        custom_frame = ttk.LabelFrame(parent_frame, text="Пользовательские горячие клавиши")
        custom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Название", "Описание", "Горячая клавиша", "Команда")
        self.custom_tree = ttk.Treeview(custom_frame, columns=columns, show="headings", height=12)
        
        # Настройка заголовков
        self.custom_tree.heading("Название", text="Название")
        self.custom_tree.heading("Описание", text="Описание")
        self.custom_tree.heading("Горячая клавиша", text="Горячая клавиша")
        self.custom_tree.heading("Команда", text="Команда/Действие")
        
        # Настройка ширины столбцов
        self.custom_tree.column("Название", width=120, minwidth=80)
        self.custom_tree.column("Описание", width=200, minwidth=100)
        self.custom_tree.column("Горячая клавиша", width=120, minwidth=80)
        self.custom_tree.column("Команда", width=250, minwidth=150)
        
        # Скроллбар для пользовательских клавиш
        custom_scrollbar = ttk.Scrollbar(custom_frame, orient="vertical", command=self.custom_tree.yview)
        self.custom_tree.configure(yscrollcommand=custom_scrollbar.set)
        
        self.custom_tree.pack(side="left", fill="both", expand=True)
        custom_scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления пользовательскими клавишами
        custom_buttons_frame = ttk.Frame(parent_frame)
        custom_buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(custom_buttons_frame, text="➕ Добавить", command=self.add_custom_hotkey).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(custom_buttons_frame, text="✏️ Изменить", command=self.edit_custom_hotkey).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(custom_buttons_frame, text="🗑️ Удалить", command=self.remove_custom_hotkey).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(custom_buttons_frame, text="📄 Дублировать", command=self.duplicate_custom_hotkey).pack(side=tk.LEFT)
    
    def create_overview_tab(self, parent_frame):
        """Создание вкладки обзора всех горячих клавиш"""
        # Общий список всех горячих клавиш
        overview_frame = ttk.LabelFrame(parent_frame, text="Все горячие клавиши")
        overview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Тип", "Горячая клавиша", "Описание", "Действие/Команда")
        self.overview_tree = ttk.Treeview(overview_frame, columns=columns, show="headings", height=15)
        
        # Настройка заголовков
        self.overview_tree.heading("Тип", text="Тип")
        self.overview_tree.heading("Горячая клавиша", text="Горячая клавиша")
        self.overview_tree.heading("Описание", text="Описание")
        self.overview_tree.heading("Действие/Команда", text="Действие/Команда")
        
        # Настройка ширины столбцов
        self.overview_tree.column("Тип", width=80, minwidth=60)
        self.overview_tree.column("Горячая клавиша", width=120, minwidth=80)
        self.overview_tree.column("Описание", width=200, minwidth=120)
        self.overview_tree.column("Действие/Команда", width=300, minwidth=150)
        
        # Скроллбар для обзора
        overview_scrollbar = ttk.Scrollbar(overview_frame, orient="vertical", command=self.overview_tree.yview)
        self.overview_tree.configure(yscrollcommand=overview_scrollbar.set)
        
        self.overview_tree.pack(side="left", fill="both", expand=True)
        overview_scrollbar.pack(side="right", fill="y")
        
        # Информационная панель
        info_frame = ttk.LabelFrame(parent_frame, text="Статистика")
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.stats_label = ttk.Label(info_frame, text="Загрузка статистики...")
        self.stats_label.pack(padx=10, pady=10)
    
    def refresh_hotkeys_list(self):
        """Обновление всех списков горячих клавиш"""
        self.refresh_system_hotkeys()
        self.refresh_custom_hotkeys()
        self.refresh_overview()
        self.update_statistics()
    
    def refresh_system_hotkeys(self):
        """Обновление списка системных горячих клавиш"""
        # Очистка списка
        for item in self.system_tree.get_children():
            self.system_tree.delete(item)
        
        # Заполнение системными горячими клавишами
        system_hotkeys = self.settings_manager.get_hotkeys()
        for action, hotkey in system_hotkeys.items():
            description = self.settings_manager.get_action_description(action)
            self.system_tree.insert("", tk.END, values=(
                action, description, hotkey
            ), tags=(action,))
    
    def refresh_custom_hotkeys(self):
        """Обновление списка пользовательских горячих клавиш"""
        # Очистка списка
        for item in self.custom_tree.get_children():
            self.custom_tree.delete(item)
        
        # Заполнение пользовательскими горячими клавишами
        custom_hotkeys = self.settings_manager.get_custom_hotkeys()
        for name, data in custom_hotkeys.items():
            self.custom_tree.insert("", tk.END, values=(
                name,
                data.get("description", ""),
                data["hotkey"],
                data.get("command", "")
            ), tags=(name,))
    
    def refresh_overview(self):
        """Обновление обзора всех горячих клавиш"""
        # Очистка списка
        for item in self.overview_tree.get_children():
            self.overview_tree.delete(item)
        
        # Получение всех горячих клавиш
        all_hotkeys = self.settings_manager.get_all_hotkeys()
        
        # Сортировка по горячим клавишам
        sorted_hotkeys = sorted(all_hotkeys.items(), key=lambda x: x[0])
        
        for hotkey, data in sorted_hotkeys:
            if data["type"] == "system":
                type_text = "🔧 Система"
                action_text = data["action"]
            else:  # custom
                type_text = "🎯 Польз."
                action_text = data.get("command", data.get("name", ""))
            
            self.overview_tree.insert("", tk.END, values=(
                type_text,
                hotkey,
                data["description"],
                action_text
            ))
    
    def update_statistics(self):
        """Обновление статистики"""
        system_count = len(self.settings_manager.get_hotkeys())
        custom_count = len(self.settings_manager.get_custom_hotkeys())
        total_count = system_count + custom_count
        
        stats_text = f"Всего горячих клавиш: {total_count} (системных: {system_count}, пользовательских: {custom_count})"
        self.stats_label.config(text=stats_text)
    
    def edit_system_hotkey(self):
        """Редактирование системной горячей клавиши"""
        selection = self.system_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите системную горячую клавишу для редактирования")
            return
        
        item = self.system_tree.item(selection[0])
        action = item['tags'][0]
        current_hotkey = item['values'][2]
        
        # Простой диалог для ввода новой горячей клавиши
        SimpleHotkeyEditDialog(self.dialog, action, current_hotkey, self.settings_manager, self.refresh_hotkeys_list)
    
    def reset_system_hotkey(self):
        """Сброс системной горячей клавиши к значению по умолчанию"""
        selection = self.system_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите системную горячую клавишу для сброса")
            return
        
        item = self.system_tree.item(selection[0])
        action = item['tags'][0]
        
        # Значения по умолчанию
        default_hotkeys = {
            "select_directory": "Ctrl+O",
            "create_project": "Ctrl+N",
            "create_snapshot": "Ctrl+S",
            "analyze_changes": "Ctrl+A",
            "open_file": "Enter",
            "refresh": "F5",
            "exit": "Ctrl+Q",
            "search_files": "Ctrl+F",
            "save_file": "Ctrl+S",
            "copy": "Ctrl+C",
            "paste": "Ctrl+V",
            "undo": "Ctrl+Z",
            "redo": "Ctrl+Y",
            "select_all": "Ctrl+A",
            "find_replace": "Ctrl+H"
        }
        
        default_hotkey = default_hotkeys.get(action, "")
        if default_hotkey:
            self.settings_manager.set_hotkey(action, default_hotkey)
            self.refresh_hotkeys_list()
            messagebox.showinfo("Успех", f"Горячая клавиша для '{action}' сброшена к значению по умолчанию")
    
    def reset_all_system_hotkeys(self):
        """Сброс всех системных горячих клавиш к значениям по умолчанию"""
        if messagebox.askyesno("Подтверждение", "Сбросить все системные горячие клавиши к значениям по умолчанию?"):
            # Значения по умолчанию
            default_hotkeys = {
                "select_directory": "Ctrl+O",
                "create_project": "Ctrl+N",
                "create_snapshot": "Ctrl+S",
                "analyze_changes": "Ctrl+A",
                "open_file": "Enter",
                "refresh": "F5",
                "exit": "Ctrl+Q",
                "search_files": "Ctrl+F",
                "save_file": "Ctrl+S",
                "copy": "Ctrl+C",
                "paste": "Ctrl+V",
                "undo": "Ctrl+Z",
                "redo": "Ctrl+Y",
                "select_all": "Ctrl+A",
                "find_replace": "Ctrl+H"
            }
            
            for action, hotkey in default_hotkeys.items():
                self.settings_manager.set_hotkey(action, hotkey)
            
            self.refresh_hotkeys_list()
            messagebox.showinfo("Успех", "Все системные горячие клавиши сброшены к значениям по умолчанию")
    
    def add_custom_hotkey(self):
        """Добавление новой пользовательской горячей клавиши"""
        CustomHotkeyEditDialog(self.dialog, self.settings_manager, None, self.refresh_hotkeys_list)
    
    def edit_custom_hotkey(self):
        """Редактирование пользовательской горячей клавиши"""
        selection = self.custom_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользовательскую горячую клавишу для редактирования")
            return
        
        item = self.custom_tree.item(selection[0])
        name = item['tags'][0]
        
        custom_hotkeys = self.settings_manager.get_custom_hotkeys()
        if name in custom_hotkeys:
            CustomHotkeyEditDialog(self.dialog, self.settings_manager, (name, custom_hotkeys[name]), self.refresh_hotkeys_list)
    
    def remove_custom_hotkey(self):
        """Удаление пользовательской горячей клавиши"""
        selection = self.custom_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользовательскую горячую клавишу для удаления")
            return
        
        item = self.custom_tree.item(selection[0])
        name = item['tags'][0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить пользовательскую горячую клавишу '{name}'?"):
            if self.settings_manager.remove_custom_hotkey(name):
                self.refresh_hotkeys_list()
                messagebox.showinfo("Успех", "Пользовательская горячая клавиша удалена")
            else:
                messagebox.showerror("Ошибка", "Ошибка удаления горячей клавиши")
    
    def duplicate_custom_hotkey(self):
        """Дублирование пользовательской горячей клавиши"""
        selection = self.custom_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользовательскую горячую клавишу для дублирования")
            return
        
        item = self.custom_tree.item(selection[0])
        name = item['tags'][0]
        
        custom_hotkeys = self.settings_manager.get_custom_hotkeys()
        if name in custom_hotkeys:
            original_data = custom_hotkeys[name]
            new_name = f"{name}_copy"
            
            # Убеждаемся, что имя уникально
            counter = 1
            while new_name in custom_hotkeys:
                new_name = f"{name}_copy_{counter}"
                counter += 1
            
            # Создаем копию
            self.settings_manager.add_custom_hotkey(
                new_name,
                original_data["hotkey"] + "_copy",  # Изменяем горячую клавишу
                original_data.get("command", ""),
                f"Копия: {original_data.get('description', '')}"
            )
            
            self.refresh_hotkeys_list()
            messagebox.showinfo("Успех", f"Создана копия '{new_name}'")
    
    def save_and_close(self):
        """Сохранение и закрытие диалога"""
        messagebox.showinfo("Успех", "Настройки горячих клавиш сохранены!\nПерезапустите приложение для применения изменений.")
        self.dialog.grab_release()
        self.dialog.destroy()
    
    def cancel(self):
        """Отмена изменений"""
        self.dialog.grab_release()
        self.dialog.destroy()


class SimpleHotkeyEditDialog:
    """Простой диалог для редактирования горячей клавиши"""
    
    def __init__(self, parent, action, current_hotkey, settings_manager, refresh_callback):
        self.action = action
        self.settings_manager = settings_manager
        self.refresh_callback = refresh_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Изменить горячую клавишу: {action}")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        
        # Сделать диалог модальным
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_interface(current_hotkey)
        self.center_dialog()
    
    def center_dialog(self):
        """Центрирование диалога"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_interface(self, current_hotkey):
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Описание действия
        description = self.settings_manager.get_action_description(self.action)
        ttk.Label(main_frame, text=f"Действие: {description}", font=('Arial', 10, 'bold')).pack(pady=(0, 10))
        
        ttk.Label(main_frame, text="Новая горячая клавиша:").pack(anchor="w", pady=(0, 5))
        
        self.hotkey_entry = ttk.Entry(main_frame, width=30, font=('Arial', 11))
        self.hotkey_entry.pack(fill="x", pady=(0, 5))
        self.hotkey_entry.insert(0, current_hotkey)
        
        # Инструкция
        instruction_text = "Нажмите комбинацию клавиш в поле выше\nили введите вручную (например: Ctrl+F1)"
        ttk.Label(main_frame, text=instruction_text, foreground="gray", font=('Arial', 9)).pack(pady=(5, 15))
        
        # Привязываем события для записи горячих клавиш
        self.hotkey_entry.bind("<KeyPress>", self.on_hotkey_press)
        self.hotkey_entry.bind("<KeyRelease>", self.on_hotkey_release)
        
        # Кнопки
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Сохранить", command=self.save_hotkey).pack(side="right", padx=(5, 0))
        ttk.Button(buttons_frame, text="Отмена", command=self.cancel).pack(side="right")
    
    def on_hotkey_press(self, event):
        """Обработка нажатия клавиши для записи горячей клавиши"""
        # Отменяем стандартное поведение
        event.widget.delete(0, tk.END)
        
        # Собираем модификаторы
        modifiers = []
        if event.state & 0x4:  # Control
            modifiers.append("Ctrl")
        if event.state & 0x8:  # Alt
            modifiers.append("Alt")
        if event.state & 0x1:  # Shift
            modifiers.append("Shift")
        
        # Получаем основную клавишу
        key = event.keysym
        
        # Обработка специальных клавиш
        if key in ["Control_L", "Control_R", "Alt_L", "Alt_R", "Shift_L", "Shift_R"]:
            return "break"
        
        # Формируем строку горячей клавиши
        hotkey_parts = modifiers + [key]
        hotkey_string = "+".join(hotkey_parts)
        
        # Вставляем в поле
        event.widget.insert(0, hotkey_string)
        
        return "break"
    
    def on_hotkey_release(self, event):
        """Обработка отпускания клавиши"""
        return "break"
    
    def save_hotkey(self):
        """Сохранение горячей клавиши"""
        new_hotkey = self.hotkey_entry.get().strip()
        if not new_hotkey:
            messagebox.showwarning("Предупреждение", "Введите горячую клавишу")
            return
        
        # Проверка на дублирующиеся клавиши
        all_hotkeys = self.settings_manager.get_all_hotkeys()
        if new_hotkey in all_hotkeys and all_hotkeys[new_hotkey].get("action") != self.action:
            existing_desc = all_hotkeys[new_hotkey]["description"]
            messagebox.showerror("Ошибка", f"Горячая клавиша '{new_hotkey}' уже используется для: {existing_desc}")
            return
        
        # Сохранение
        if self.settings_manager.set_hotkey(self.action, new_hotkey):
            self.refresh_callback()
            messagebox.showinfo("Успех", "Горячая клавиша обновлена")
            self.dialog.grab_release()
            self.dialog.destroy()
        else:
            messagebox.showerror("Ошибка", "Ошибка сохранения горячей клавиши")
    
    def cancel(self):
        """Отмена"""
        self.dialog.grab_release()
        self.dialog.destroy()


class CustomHotkeyEditDialog:
    """Диалог для редактирования пользовательских горячих клавиш"""
    
    def __init__(self, parent, settings_manager, hotkey_data, refresh_callback):
        self.settings_manager = settings_manager
        self.refresh_callback = refresh_callback
        self.is_edit = hotkey_data is not None
        
        if self.is_edit:
            self.original_name, self.original_data = hotkey_data
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Редактировать пользовательскую горячую клавишу" if self.is_edit else "Добавить пользовательскую горячую клавишу")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Сделать диалог модальным
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_interface()
        if self.is_edit:
            self.load_data()
        self.center_dialog()
    
    def center_dialog(self):
        """Центрирование диалога"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_interface(self):
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Название
        ttk.Label(main_frame, text="Название:").pack(anchor="w", pady=(0, 5))
        self.name_entry = ttk.Entry(main_frame, width=50)
        self.name_entry.pack(fill="x", pady=(0, 15))
        
        # Описание
        ttk.Label(main_frame, text="Описание:").pack(anchor="w", pady=(0, 5))
        self.description_entry = ttk.Entry(main_frame, width=50)
        self.description_entry.pack(fill="x", pady=(0, 15))
        
        # Горячая клавиша
        ttk.Label(main_frame, text="Горячая клавиша:").pack(anchor="w", pady=(0, 5))
        hotkey_frame = ttk.Frame(main_frame)
        hotkey_frame.pack(fill="x", pady=(0, 10))
        
        self.hotkey_entry = ttk.Entry(hotkey_frame, width=30)
        self.hotkey_entry.pack(side="left", padx=(0, 10))
        
        ttk.Button(hotkey_frame, text="Записать", command=self.start_hotkey_recording).pack(side="left")
        
        # Инструкция для горячих клавиш
        instruction_text = "Введите вручную или нажмите 'Записать' и нажмите комбинацию клавиш"
        ttk.Label(main_frame, text=instruction_text, foreground="gray", font=('Arial', 9)).pack(anchor="w", pady=(0, 15))
        
        # Команда
        ttk.Label(main_frame, text="Команда/Действие:").pack(anchor="w", pady=(0, 5))
        self.command_text = tk.Text(main_frame, height=6, width=50)
        self.command_text.pack(fill="both", expand=True, pady=(0, 15))
        
        # Скроллбар для текстового поля
        command_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.command_text.yview)
        self.command_text.configure(yscrollcommand=command_scrollbar.set)
        
        # Инструкция для команд
        command_instruction = "Введите команду для выполнения при нажатии горячей клавиши\n(оставьте пустым для простой заглушки)"
        ttk.Label(main_frame, text=command_instruction, foreground="gray", font=('Arial', 9)).pack(anchor="w", pady=(0, 15))
        
        # Кнопки
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x")
        
        ttk.Button(buttons_frame, text="Сохранить", command=self.save_hotkey).pack(side="right", padx=(5, 0))
        ttk.Button(buttons_frame, text="Отмена", command=self.cancel).pack(side="right")
        ttk.Button(buttons_frame, text="Тест команды", command=self.test_command).pack(side="left")
    
    def load_data(self):
        """Загрузка данных для редактирования"""
        self.name_entry.insert(0, self.original_name)
        self.description_entry.insert(0, self.original_data.get("description", ""))
        self.hotkey_entry.insert(0, self.original_data["hotkey"])
        self.command_text.insert(1.0, self.original_data.get("command", ""))
    
    def start_hotkey_recording(self):
        """Начало записи горячей клавиши"""
        # Создаем временное окно для записи горячей клавиши
        record_dialog = tk.Toplevel(self.dialog)
        record_dialog.title("Запись горячей клавиши")
        record_dialog.geometry("300x150")
        record_dialog.resizable(False, False)
        record_dialog.transient(self.dialog)
        record_dialog.grab_set()
        
        # Центрирование
        record_dialog.update_idletasks()
        x = (record_dialog.winfo_screenwidth() // 2) - (record_dialog.winfo_width() // 2)
        y = (record_dialog.winfo_screenheight() // 2) - (record_dialog.winfo_height() // 2)
        record_dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(record_dialog, text="Нажмите комбинацию клавиш:", font=('Arial', 12)).pack(pady=20)
        
        result_label = ttk.Label(record_dialog, text="", font=('Arial', 10, 'bold'))
        result_label.pack(pady=10)
        
        def on_key_press(event):
            # Собираем модификаторы
            modifiers = []
            if event.state & 0x4:  # Control
                modifiers.append("Ctrl")
            if event.state & 0x8:  # Alt
                modifiers.append("Alt")
            if event.state & 0x1:  # Shift
                modifiers.append("Shift")
            
            # Получаем основную клавишу
            key = event.keysym
            
            # Обработка специальных клавиш
            if key in ["Control_L", "Control_R", "Alt_L", "Alt_R", "Shift_L", "Shift_R"]:
                return
            
            # Формируем строку горячей клавиши
            hotkey_parts = modifiers + [key]
            hotkey_string = "+".join(hotkey_parts)
            
            result_label.config(text=hotkey_string)
            
            # Сохраняем результат и закрываем диалог через секунду
            self.hotkey_entry.delete(0, tk.END)
            self.hotkey_entry.insert(0, hotkey_string)
            
            record_dialog.after(1000, lambda: (record_dialog.grab_release(), record_dialog.destroy()))
        
        record_dialog.bind("<KeyPress>", on_key_press)
        record_dialog.focus_set()
        
        # Кнопка отмены
        ttk.Button(record_dialog, text="Отмена", 
                  command=lambda: (record_dialog.grab_release(), record_dialog.destroy())).pack(pady=10)
    
    def test_command(self):
        """Тестирование команды"""
        command = self.command_text.get(1.0, tk.END).strip()
        if not command:
            messagebox.showinfo("Информация", "Команда не задана")
            return
        
        try:
            # Простое выполнение команды (осторожно!)
            import subprocess
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            
            # Показываем результат
            result_text = f"Код возврата: {result.returncode}\n\n"
            if result.stdout:
                result_text += f"Вывод:\n{result.stdout}\n\n"
            if result.stderr:
                result_text += f"Ошибки:\n{result.stderr}"
            
            # Создаем диалог для показа результата
            result_dialog = tk.Toplevel(self.dialog)
            result_dialog.title("Результат выполнения команды")
            result_dialog.geometry("500x300")
            result_dialog.transient(self.dialog)
            
            text_widget = tk.Text(result_dialog, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(1.0, result_text)
            text_widget.config(state=tk.DISABLED)
            
            ttk.Button(result_dialog, text="Закрыть", command=result_dialog.destroy).pack(pady=5)
            
        except subprocess.TimeoutExpired:
            messagebox.showerror("Ошибка", "Команда выполнялась слишком долго (таймаут 10 сек)")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка выполнения команды: {e}")
    
    def save_hotkey(self):
        """Сохранение пользовательской горячей клавиши"""
        name = self.name_entry.get().strip()
        description = self.description_entry.get().strip()
        hotkey = self.hotkey_entry.get().strip()
        command = self.command_text.get(1.0, tk.END).strip()
        
        if not name or not hotkey:
            messagebox.showwarning("Предупреждение", "Заполните название и горячую клавишу")
            return
        
        # Проверка на дублирующиеся имена (только для новых)
        if not self.is_edit or name != self.original_name:
            existing_custom = self.settings_manager.get_custom_hotkeys()
            if name in existing_custom:
                messagebox.showerror("Ошибка", f"Пользовательская горячая клавиша с именем '{name}' уже существует")
                return
        
        # Проверка на дублирующиеся горячие клавиши
        all_hotkeys = self.settings_manager.get_all_hotkeys()
        if hotkey in all_hotkeys:
            existing_info = all_hotkeys[hotkey]
            if not self.is_edit or hotkey != self.original_data["hotkey"]:
                messagebox.showerror("Ошибка", f"Горячая клавиша '{hotkey}' уже используется для: {existing_info['description']}")
                return
        
        # Удаляем старую запись при редактировании
        if self.is_edit and name != self.original_name:
            self.settings_manager.remove_custom_hotkey(self.original_name)
        
        # Сохранение
        if self.settings_manager.add_custom_hotkey(name, hotkey, command, description):
            self.refresh_callback()
            messagebox.showinfo("Успех", "Пользовательская горячая клавиша сохранена")
            self.dialog.grab_release()
            self.dialog.destroy()
        else:
            messagebox.showerror("Ошибка", "Ошибка сохранения горячей клавиши")
    
    def cancel(self):
        """Отмена"""
        self.dialog.grab_release()
        self.dialog.destroy()


class HotkeySettingsDialog:
    def __init__(self, parent, settings_manager):
        self.parent = parent
        self.settings_manager = settings_manager
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройки горячих клавиш")
        self.dialog.geometry("600x400")
        self.dialog.resizable(False, False)
        
        # Сделать диалог модальным
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_interface()
        self.load_hotkeys()
        self.center_dialog()
    
    def center_dialog(self):
        """Центрирование диалога"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_interface(self):
        # Заголовок
        title_label = ttk.Label(self.dialog, text="Настройка горячих клавиш", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(10, 5))
        
        # Подсказка
        hint_label = ttk.Label(self.dialog, text="Горячие клавиши работают независимо от языка ввода", 
                              foreground="gray", font=('Arial', 9))
        hint_label.pack(pady=(0, 10))
        
        # Основной фрейм
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Список горячих клавиш
        self.hotkey_entries = {}
        
        # Описания действий
        action_descriptions = {
            "select_directory": "Выбор директории",
            "create_project": "Создать новый проект",
            "create_snapshot": "Создать снапшот",
            "analyze_changes": "Анализ изменений",
            "open_file": "Открыть файл",
            "refresh": "Обновить",
            "exit": "Выход"
        }
        
        row = 0
        for action, description in action_descriptions.items():
            ttk.Label(main_frame, text=f"{description}:").grid(row=row, column=0, sticky="w", padx=(0, 10), pady=5)
            
            entry = ttk.Entry(main_frame, width=20)
            entry.grid(row=row, column=1, padx=(0, 5), pady=5)
            entry.bind("<KeyPress>", lambda e, a=action: self.on_hotkey_press(e, a))
            entry.bind("<KeyRelease>", lambda e: self.on_hotkey_release(e))
            
            self.hotkey_entries[action] = entry
            
            # Кнопка сброса
            ttk.Button(main_frame, text="Сброс", width=8,
                      command=lambda a=action: self.reset_hotkey(a)).grid(row=row, column=2, padx=5, pady=5)
            
            row += 1
        
        # Информация о форматах
        info_frame = ttk.LabelFrame(main_frame, text="Информация")
        info_frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(20, 10))
        
        info_text = """Примеры горячих клавиш:
• Ctrl+O, Ctrl+N, Ctrl+S
• Alt+F4, Shift+F10
• F5, F12, Enter, Esc
• Ctrl+Shift+A

Поддерживаемые модификаторы:
• Ctrl, Alt, Shift
• Комбинации модификаторов"""
        
        ttk.Label(info_frame, text=info_text, justify="left").pack(padx=10, pady=10)
        
        # Кнопки диалога
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=row+1, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Сохранить", command=self.save_hotkeys).pack(side="right", padx=(5, 0))
        ttk.Button(buttons_frame, text="Отмена", command=self.cancel).pack(side="right")
        ttk.Button(buttons_frame, text="Сброс всех", command=self.reset_all_hotkeys).pack(side="left")
    
    def load_hotkeys(self):
        """Загрузка текущих горячих клавиш"""
        hotkeys = self.settings_manager.get_hotkeys()
        for action, entry in self.hotkey_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, hotkeys.get(action, ""))
    
    def on_hotkey_press(self, event, action):
        """Обработка нажатия клавиши для записи горячей клавиши"""
        # Отменяем стандартное поведение
        event.widget.delete(0, tk.END)
        
        # Собираем модификаторы
        modifiers = []
        if event.state & 0x4:  # Control
            modifiers.append("Ctrl")
        if event.state & 0x8:  # Alt
            modifiers.append("Alt")
        if event.state & 0x1:  # Shift
            modifiers.append("Shift")
        
        # Получаем основную клавишу
        key = event.keysym
        
        # Обработка специальных клавиш
        if key in ["Control_L", "Control_R", "Alt_L", "Alt_R", "Shift_L", "Shift_R"]:
            return "break"
        
        # Формируем строку горячей клавиши
        hotkey_parts = modifiers + [key]
        hotkey_string = "+".join(hotkey_parts)
        
        # Вставляем в поле
        event.widget.insert(0, hotkey_string)
        
        return "break"
    
    def on_hotkey_release(self, event):
        """Обработка отпускания клавиши"""
        return "break"
    
    def reset_hotkey(self, action):
        """Сброс горячей клавиши к значению по умолчанию"""
        default_hotkeys = {
            "select_directory": "Ctrl+O",
            "create_project": "Ctrl+N",
            "create_snapshot": "Ctrl+S",
            "analyze_changes": "Ctrl+A",
            "open_file": "Enter",
            "refresh": "F5",
            "exit": "Ctrl+Q"
        }
        
        entry = self.hotkey_entries[action]
        entry.delete(0, tk.END)
        entry.insert(0, default_hotkeys.get(action, ""))
    
    def reset_all_hotkeys(self):
        """Сброс всех горячих клавиш к значениям по умолчанию"""
        if messagebox.askyesno("Подтверждение", "Сбросить все горячие клавиши к значениям по умолчанию?"):
            for action in self.hotkey_entries:
                self.reset_hotkey(action)
    
    def save_hotkeys(self):
        """Сохранение горячих клавиш"""
        # Проверка на дублирующиеся клавиши
        hotkeys = {}
        used_hotkeys = set()
        
        for action, entry in self.hotkey_entries.items():
            hotkey = entry.get().strip()
            if hotkey:
                if hotkey in used_hotkeys:
                    messagebox.showerror("Ошибка", f"Горячая клавиша '{hotkey}' уже используется!")
                    return
                used_hotkeys.add(hotkey)
                hotkeys[action] = hotkey
        
        # Сохранение настроек
        for action, hotkey in hotkeys.items():
            self.settings_manager.set_hotkey(action, hotkey)
        
        messagebox.showinfo("Успех", "Горячие клавиши сохранены!\nПерезапустите приложение для применения изменений.")
        self.dialog.grab_release()
        self.dialog.destroy()
    
    def cancel(self):
        """Отмена изменений"""
        self.dialog.grab_release()
        self.dialog.destroy()
