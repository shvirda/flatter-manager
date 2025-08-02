import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import subprocess
import webbrowser
from database_manager import DatabaseManager
from project_analyzer import ProjectAnalyzer
from snapshot_manager import SnapshotManager
from settings_manager import SettingsManager, EditorSettingsDialog, HotkeySettingsDialog, AdvancedHotkeySettingsDialog
from search_manager import SearchManager, SearchDialog
from search_recipes_manager import SearchRecipesManager, SearchRecipeDialog

class FlutterProjectManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Flutter Project Manager - Полная версия")
        self.root.geometry("1200x800")
        
        # Initialize managers
        self.db_manager = DatabaseManager()
        self.analyzer = ProjectAnalyzer()
        self.snapshot_manager = SnapshotManager(self.db_manager)
        self.settings_manager = SettingsManager(self.db_manager)
        self.search_manager = SearchManager()
        self.search_recipes_manager = SearchRecipesManager(self.db_manager)
        
        # Variables
        self.current_directory = None
        self.project_mode = tk.StringVar(value="new")
        
        # Настройки анализа
        self.analysis_file_limit = None  # Без лимитов по умолчанию
        self.analysis_excluded_folders = ['.git', 'node_modules', '.dart_tool', 'build', '__pycache__', '.vscode', '.idea']
        
        # Настройки автопоиска
        self.auto_search_patterns = ['*.exe', '*.apk', '*.jar', '*.msi', '*.deb', '*.dmg', '*.app']
        self.auto_search_enabled_patterns = {pattern: True for pattern in self.auto_search_patterns}  # Включенные маски
        self.auto_search_results = {}  # Хранение результатов автопоиска
        
        self.create_main_interface()
        self.setup_hotkeys()
        self.load_initial_data()

    def create_main_interface(self):
        """Создание главного интерфейса"""
        # Главное меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Выбрать директорию", command=self.select_directory)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню поиск
        search_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Поиск", menu=search_menu)
        search_menu.add_command(label="Быстрый поиск", command=self.focus_search_tab)
        search_menu.add_command(label="Расширенный поиск файлов", command=self.open_advanced_search)
        search_menu.add_command(label="Поиск в файлах", command=self.search_in_files)
        search_menu.add_separator()
        search_menu.add_command(label="Очистить результаты", command=self.clear_search_results)
        
        # Меню настроек
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Настройки", menu=settings_menu)
        settings_menu.add_command(label="Редакторы", command=self.configure_editors)
        settings_menu.add_command(label="Горячие клавиши", command=self.configure_hotkeys)
        settings_menu.add_command(label="Расширенные горячие клавиши", command=self.configure_advanced_hotkeys)
        settings_menu.add_separator()
        settings_menu.add_command(label="Анализ проекта", command=self.configure_analysis)
        settings_menu.add_command(label="Автопоиск файлов", command=self.configure_auto_search)
        settings_menu.add_separator()
        settings_menu.add_command(label="Резервное копирование", command=self.backup_settings)
        
        # Меню базы данных
        database_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="База данных", menu=database_menu)
        database_menu.add_command(label="Информация о БД", command=self.show_database_info)
        database_menu.add_command(label="Очистить историю директорий", command=self.clear_directory_history)
        database_menu.add_command(label="Очистить команды", command=self.clear_commands)
        database_menu.add_command(label="Очистить снапшоты", command=self.clear_snapshots)
        database_menu.add_separator()
        database_menu.add_command(label="Экспорт БД", command=self.export_database)
        database_menu.add_command(label="Импорт БД", command=self.import_database)
        database_menu.add_separator()
        database_menu.add_command(label="Пересоздать БД", command=self.recreate_database)
        
        # Главный фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Верхняя панель - выбор директории
        dir_frame = ttk.LabelFrame(main_frame, text="Работа с директорией")
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.dir_label = ttk.Label(dir_frame, text="Директория не выбрана")
        self.dir_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        ttk.Button(dir_frame, text="Выбрать директорию", command=self.select_directory).pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Панель режимов работы
        mode_frame = ttk.LabelFrame(main_frame, text="Режим работы")
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="Создать новый проект", variable=self.project_mode, value="new").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Анализировать существующий", variable=self.project_mode, value="analyze").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Сравнить проекты", variable=self.project_mode, value="compare").pack(side=tk.LEFT, padx=10)
        
        # Основная рабочая область с вкладками
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка проектов
        self.create_project_tab()
        
        # Вкладка команд
        self.create_commands_tab()
        
        # Вкладка снапшотов
        self.create_snapshots_tab()
        
        # Вкладка сравнения
        self.create_comparison_tab()
        
        # Вкладка поиска
        self.create_search_tab()
        
        # Кнопки действий
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, text="Выполнить действие", command=self.execute_main_action).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Создать снапшот", command=self.create_snapshot_dialog).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Анализ изменений", command=self.analyze_changes).pack(side=tk.LEFT)
        
        # Статус-бар
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_label = ttk.Label(status_frame, text="Готов к работе", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=2, pady=2)
        
        # Обновить статистику БД в статус-баре
        self.update_database_status()

    def open_folder_in_explorer(self):
        """Открытие выбранной папки или папки файла в проводнике"""
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите файл или папку для открытия")
            return
        item = self.project_tree.item(selection[0])
        file_path = item['tags'][0] if item['tags'] else None
        folder_path = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)
        if os.path.exists(folder_path):
            os.startfile(folder_path)
        else:
            messagebox.showerror("Ошибка", "Путь не существует")
    
    def copy_folder_path(self):
        """Копирование пути к папке в буфер обмена"""
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите файл или папку")
            return
        item = self.project_tree.item(selection[0])
        if item['tags']:
            file_path = item['tags'][0]
            folder_path = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)
            self.root.clipboard_clear()
            self.root.clipboard_append(folder_path)
            messagebox.showinfo("Копирование", f"Путь к папке скопирован:\n{folder_path}")
        else:
            folder_path = self.get_folder_path_from_tree_item(selection[0])
            self.root.clipboard_clear()
            self.root.clipboard_append(folder_path)
            messagebox.showinfo("Копирование", f"Путь к папке скопирован:\n{folder_path}")
    
    def copy_full_file_path(self):
        """Копирование полного пути к файлу в буфер обмена"""
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите файл")
            return
        item = self.project_tree.item(selection[0])
        if item['tags']:
            file_path = item['tags'][0]
            self.root.clipboard_clear()
            self.root.clipboard_append(file_path)
            messagebox.showinfo("Копирование", f"Полный путь к файлу скопирован:\n{file_path}")
        else:
            messagebox.showwarning("Предупреждение", "Выбранный элемент не является файлом")
    
    def open_cmd_in_folder(self):
        """Открытие CMD в папке выбранного файла или папки"""
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите файл или папку")
            return
        item = self.project_tree.item(selection[0])
        if item['tags']:
            file_path = item['tags'][0]
            folder_path = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)
        else:
            folder_path = self.get_folder_path_from_tree_item(selection[0])
        
        if os.path.exists(folder_path):
            subprocess.Popen(['cmd', '/k', 'cd', '/d', folder_path], shell=True)
        else:
            messagebox.showerror("Ошибка", "Папка не существует")
    
    def open_powershell_in_folder(self):
        """Открытие PowerShell в папке выбранного файла или папки"""
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите файл или папку")
            return
        item = self.project_tree.item(selection[0])
        if item['tags']:
            file_path = item['tags'][0]
            folder_path = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)
        else:
            folder_path = self.get_folder_path_from_tree_item(selection[0])
        
        if os.path.exists(folder_path):
            subprocess.Popen(['powershell', '-Command', f'Set-Location "{folder_path}"; powershell'], shell=True)
        else:
            messagebox.showerror("Ошибка", "Папка не существует")

    def create_project_tab(self):
        """Создание вкладки проектов"""
        project_frame = ttk.Frame(self.notebook)
        self.notebook.add(project_frame, text="Проекты")
        
        # Список файлов проекта
        files_frame = ttk.LabelFrame(project_frame, text="Файлы проекта")
        files_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Дерево файлов
        self.project_tree = ttk.Treeview(files_frame, columns=("type", "size", "lines", "chars"), show="tree headings")
        self.project_tree.heading("#0", text="Имя")
        self.project_tree.heading("type", text="Тип")
        self.project_tree.heading("size", text="Размер")
        self.project_tree.heading("lines", text="Строки")
        self.project_tree.heading("chars", text="Символы")
        self.project_tree.pack(fill=tk.BOTH, expand=True)
        
        # Настройка цветовых тегов для файлов
        self.setup_file_colors()
        
        # Контекстное меню для файлов
        self.file_context_menu = tk.Menu(self.root, tearoff=0)
        self.file_context_menu.add_command(label="Открыть в редакторе", command=self.open_in_editor)
        self.file_context_menu.add_command(label="Показать изменения", command=self.show_file_diff)
        self.file_context_menu.add_separator()
        self.file_context_menu.add_command(label="📂 Открыть папку в проводнике", command=self.open_folder_in_explorer)
        self.file_context_menu.add_command(label="📝 Копировать путь к папке", command=self.copy_folder_path)
        self.file_context_menu.add_command(label="📋 Копировать полный путь к файлу", command=self.copy_full_file_path)
        self.file_context_menu.add_separator()
        self.file_context_menu.add_command(label="💻 Открыть CMD в папке", command=self.open_cmd_in_folder)
        self.file_context_menu.add_command(label="🔵 Открыть PowerShell в папке", command=self.open_powershell_in_folder)
        self.file_context_menu.add_separator()
        self.file_context_menu.add_command(label="🔍 Поиск в этой папке", command=self.search_in_selected_folder)
        self.file_context_menu.add_command(label="🔍 Поиск текста в файлах", command=self.search_text_in_selected_folder)
        self.file_context_menu.add_separator()
        
        # Подменю для исполняемых файлов будет добавляться динамически
        self.executable_submenu = tk.Menu(self.file_context_menu, tearoff=0)
        
        self.project_tree.bind("<Button-3>", self.show_file_context_menu)
        self.project_tree.bind("<Double-1>", self.open_in_editor)

    def create_commands_tab(self):
        """Создание вкладки команд"""
        commands_frame = ttk.Frame(self.notebook)
        self.notebook.add(commands_frame, text="Команды")
        
        # Список сохраненных команд
        saved_frame = ttk.LabelFrame(commands_frame, text="Сохраненные последовательности команд")
        saved_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        
        self.commands_listbox = tk.Listbox(saved_frame, selectmode=tk.MULTIPLE)
        self.commands_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Кнопки управления командами
        cmd_buttons_frame = ttk.Frame(commands_frame)
        cmd_buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(cmd_buttons_frame, text="Создать новую", command=self.create_command_sequence).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cmd_buttons_frame, text="Выполнить выбранные", command=self.execute_selected_commands).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cmd_buttons_frame, text="Удалить", command=self.delete_command).pack(side=tk.LEFT)

    def create_snapshots_tab(self):
        """Создание вкладки снапшотов"""
        snapshots_frame = ttk.Frame(self.notebook)
        self.notebook.add(snapshots_frame, text="Снапшоты")
        
        # Список снапшотов
        snap_list_frame = ttk.LabelFrame(snapshots_frame, text="Сохраненные снапшоты")
        snap_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.snapshots_tree = ttk.Treeview(snap_list_frame, columns=("description", "date", "compressed"), show="tree headings")
        self.snapshots_tree.heading("#0", text="Название")
        self.snapshots_tree.heading("description", text="Описание")
        self.snapshots_tree.heading("date", text="Дата создания")
        self.snapshots_tree.heading("compressed", text="Сжатый")
        self.snapshots_tree.pack(fill=tk.BOTH, expand=True)
        
        # Кнопки управления снапшотами
        snap_buttons_frame = ttk.Frame(snapshots_frame)
        snap_buttons_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        ttk.Button(snap_buttons_frame, text="Восстановить", command=self.restore_snapshot).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(snap_buttons_frame, text="Копировать в папку", command=self.copy_snapshot).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(snap_buttons_frame, text="Сравнить с проектом", command=self.compare_with_snapshot).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(snap_buttons_frame, text="Удалить", command=self.delete_snapshot).pack(side=tk.LEFT)

    def create_comparison_tab(self):
        """Создание вкладки сравнения проектов"""
        comparison_frame = ttk.Frame(self.notebook)
        self.notebook.add(comparison_frame, text="Сравнение")
        
        # Панель выбора проектов для сравнения
        select_frame = ttk.LabelFrame(comparison_frame, text="Выбор проектов для сравнения")
        select_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(select_frame, text="Проект 1:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.project1_var = tk.StringVar()
        ttk.Entry(select_frame, textvariable=self.project1_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(select_frame, text="Выбрать", command=lambda: self.select_project_for_comparison(1)).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(select_frame, text="Проект 2:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.project2_var = tk.StringVar()
        ttk.Entry(select_frame, textvariable=self.project2_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(select_frame, text="Выбрать", command=lambda: self.select_project_for_comparison(2)).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Button(select_frame, text="Сравнить проекты", command=self.compare_projects).grid(row=2, column=1, pady=10)
        
        # Результаты сравнения
        results_frame = ttk.LabelFrame(comparison_frame, text="Результаты сравнения")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Панель с деревьями проектов
        trees_frame = ttk.Frame(results_frame)
        trees_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левое дерево - проект 1
        left_frame = ttk.Frame(trees_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        ttk.Label(left_frame, text="Проект 1").pack()
        self.comparison_tree1 = ttk.Treeview(left_frame, columns=("folders", "files", "lines", "chars"), show="tree headings")
        self.comparison_tree1.heading("#0", text="Имя")
        self.comparison_tree1.heading("folders", text="Папки")
        self.comparison_tree1.heading("files", text="Файлы")
        self.comparison_tree1.heading("lines", text="Строки")
        self.comparison_tree1.heading("chars", text="Символы")
        self.comparison_tree1.pack(fill=tk.BOTH, expand=True)
        
        # Правое дерево - проект 2
        right_frame = ttk.Frame(trees_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        ttk.Label(right_frame, text="Проект 2").pack()
        self.comparison_tree2 = ttk.Treeview(right_frame, columns=("folders", "files", "lines", "chars"), show="tree headings")
        self.comparison_tree2.heading("#0", text="Имя")
        self.comparison_tree2.heading("folders", text="Папки")
        self.comparison_tree2.heading("files", text="Файлы")
        self.comparison_tree2.heading("lines", text="Строки")
        self.comparison_tree2.heading("chars", text="Символы")
        self.comparison_tree2.pack(fill=tk.BOTH, expand=True)
    
    def create_search_tab(self):
        """Создание вкладки поиска файлов и текста"""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="🔍 Поиск")
        
        # Быстрая панель поиска
        quick_search_frame = ttk.LabelFrame(search_frame, text="Быстрый поиск в текущей директории")
        quick_search_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Поле для поиска
        search_controls_frame = ttk.Frame(quick_search_frame)
        search_controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_controls_frame, text="Поиск:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.quick_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_controls_frame, textvariable=self.quick_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind('<Return>', self.quick_search)
        
        ttk.Button(search_controls_frame, text="🔍 Найти", command=self.quick_search).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(search_controls_frame, text="📂 Расширенный поиск", command=self.open_advanced_search).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(search_controls_frame, text="🗂️ Поиск в файлах", command=self.search_in_files).pack(side=tk.LEFT)
        
        # Опции быстрого поиска
        options_frame = ttk.Frame(quick_search_frame)
        options_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.search_case_sensitive = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Учитывать регистр", variable=self.search_case_sensitive).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_use_regex = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Регулярные выражения", variable=self.search_use_regex).pack(side=tk.LEFT, padx=(0, 10))
        
        self.search_filename_only = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Только имена файлов", variable=self.search_filename_only).pack(side=tk.LEFT)
        
        # Результаты поиска
        results_frame = ttk.LabelFrame(search_frame, text="Результаты поиска")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Дерево результатов
        columns = ("Тип", "Файл", "Путь", "Размер", "Строка", "Содержимое")
        self.search_results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
        
        # Настройка заголовков
        self.search_results_tree.heading("Тип", text="Тип")
        self.search_results_tree.heading("Файл", text="Файл")
        self.search_results_tree.heading("Путь", text="Путь")
        self.search_results_tree.heading("Размер", text="Размер")
        self.search_results_tree.heading("Строка", text="Строка")
        self.search_results_tree.heading("Содержимое", text="Найденное содержимое")
        
        # Настройка ширины столбцов
        self.search_results_tree.column("Тип", width=60, minwidth=50)
        self.search_results_tree.column("Файл", width=200, minwidth=150)
        self.search_results_tree.column("Путь", width=300, minwidth=200)
        self.search_results_tree.column("Размер", width=80, minwidth=60)
        self.search_results_tree.column("Строка", width=60, minwidth=50)
        self.search_results_tree.column("Содержимое", width=400, minwidth=250)
        
        # Скроллбары для результатов
        search_v_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.search_results_tree.yview)
        search_h_scrollbar = ttk.Scrollbar(results_frame, orient="horizontal", command=self.search_results_tree.xview)
        self.search_results_tree.configure(yscrollcommand=search_v_scrollbar.set, xscrollcommand=search_h_scrollbar.set)
        
        # Упаковка результатов
        self.search_results_tree.grid(row=0, column=0, sticky="nsew")
        search_v_scrollbar.grid(row=0, column=1, sticky="ns")
        search_h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        
        # Контекстное меню для результатов поиска
        self.search_context_menu = tk.Menu(self.root, tearoff=0)
        self.search_context_menu.add_command(label="Открыть файл", command=self.open_search_result_file)
        self.search_context_menu.add_command(label="Открыть папку", command=self.open_search_result_folder)
        self.search_context_menu.add_command(label="Копировать путь", command=self.copy_search_result_path)
        self.search_context_menu.add_separator()
        self.search_context_menu.add_command(label="Показать в проекте", command=self.show_in_project_tree)
        
        self.search_results_tree.bind("<Button-3>", self.show_search_context_menu)
        self.search_results_tree.bind("<Double-1>", self.open_search_result_file)
        
        # Статистика поиска
        search_stats_frame = ttk.Frame(results_frame)
        search_stats_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.search_stats_label = ttk.Label(search_stats_frame, text="Введите запрос для поиска")
        self.search_stats_label.pack(side=tk.LEFT)

    def load_initial_data(self):
        """Загрузка начальных данных"""
        self.refresh_commands_list()
        self.refresh_snapshots_list()

    def select_directory(self):
        """Выбор рабочей директории из истории или новой"""
        # Открыть диалог выбора директории
        DirectorySelectDialog(self.root, self.db_manager, self.on_directory_selected)
    
    def on_directory_selected(self, dir_path):
        """Callback для обработки выбранной директории"""
        if dir_path:
            self.current_directory = dir_path
            self.dir_label.config(text=f"Директория: {dir_path}")
            # Добавить в историю
            self.db_manager.add_directory_to_history(dir_path)
            self.refresh_project_files()
            # Выполнить автопоиск файлов
            self.perform_auto_search()
    
    def perform_auto_search(self):
        """Выполнение автоматического поиска файлов по настроенным маскам"""
        if not self.current_directory or not self.auto_search_patterns:
            return
        
        try:
            total_found = 0
            search_results = {}
            
            # Поиск по каждой включенной маске
            for pattern in self.auto_search_patterns:
                if self.auto_search_enabled_patterns.get(pattern, True):  # Проверяем, включена ли маска
                    found_files = self.search_files_by_pattern(self.current_directory, pattern)
                    search_results[pattern] = found_files
                    total_found += len(found_files)
            
            # Сохранить результаты
            self.auto_search_results = search_results
            
            # Обновить статус-бар с информацией о найденных файлах
            if total_found > 0:
                status_text = self.status_label.cget('text')
                status_text += f" | Найдено файлов: {total_found}"
                self.status_label.config(text=status_text)
                
        except Exception as e:
            print(f"Ошибка автопоиска: {e}")
    
    def search_files_by_pattern(self, directory, pattern):
        """Поиск файлов по маске"""
        import fnmatch
        found_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                for filename in files:
                    if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                        found_files.append(os.path.join(root, filename))
        except (PermissionError, OSError):
            pass  # Игнорировать ошибки доступа
        
        return found_files
    
    def update_database_status(self):
        """Обновление статистики базы данных в статус-баре"""
        try:
            # Получаем статистику БД
            db_stats = self.get_database_statistics()
            
            # Обновляем статус
            current_status = self.status_label.cget('text')
            if '|' in current_status:
                # Обновляем существующий статус
                parts = current_status.split('|')
                base_status = parts[0].strip()
            else:
                base_status = current_status
            
            db_info = f"БД: {db_stats['name']} ({db_stats['size']}) | Записей: {db_stats['total_records']}"
            new_status = f"{base_status} | {db_info}"
            
            self.status_label.config(text=new_status)
            
        except Exception as e:
            print(f"Ошибка обновления статистики БД: {e}")
    
    def get_database_statistics(self):
        """Получение статистики базы данных"""
        try:
            import sqlite3
            
            # Получаем путь к БД
            db_path = self.db_manager.db_path if hasattr(self.db_manager, 'db_path') else 'project_manager.db'
            
            # Получаем размер файла БД
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                if size_bytes > 1024 * 1024:
                    size_str = f"{size_bytes / (1024 * 1024):.1f} МБ"
                elif size_bytes > 1024:
                    size_str = f"{size_bytes / 1024:.1f} КБ"
                else:
                    size_str = f"{size_bytes} Б"
            else:
                size_str = "0 Б"
            
            # Подключаемся к БД для получения количества записей
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Считаем общее количество записей
            total_records = 0
            
            # Получаем список всех таблиц
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                if table_name != 'sqlite_sequence':  # Исключаем системную таблицу
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    total_records += count
            
            conn.close()
            
            return {
                'name': os.path.basename(db_path),
                'size': size_str,
                'total_records': total_records
            }
            
        except Exception as e:
            print(f"Ошибка получения статистики БД: {e}")
            return {
                'name': 'unknown.db',
                'size': '0 Б',
                'total_records': 0
            }
    
    # Методы для работы с базой данных
    def show_database_info(self):
        """Показать подробную информацию о базе данных"""
        try:
            DatabaseInfoDialog(self.root, self)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть диалог информации о БД:\n{str(e)}")
    
    def clear_directory_history(self):
        """Очистить историю директорий"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю директорий?"):
            try:
                self.db_manager.clear_directory_history()
                self.update_database_status()
                messagebox.showinfo("Успех", "История директорий очищена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка очистки истории: {str(e)}")
    
    def clear_commands(self):
        """Очистить все команды"""
        if messagebox.askyesno("Подтверждение", "Удалить все сохраненные команды?"):
            try:
                self.db_manager.clear_commands()
                self.refresh_commands_list()
                self.update_database_status()
                messagebox.showinfo("Успех", "Команды удалены")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка удаления команд: {str(e)}")
    
    def clear_snapshots(self):
        """Очистить все снапшоты"""
        if messagebox.askyesno("Подтверждение", "Удалить все снапшоты? Это действие необратимо!"):
            try:
                self.snapshot_manager.clear_all_snapshots()
                self.refresh_snapshots_list()
                self.update_database_status()
                messagebox.showinfo("Успех", "Снапшоты удалены")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка удаления снапшотов: {str(e)}")
    
    def export_database(self):
        """Экспорт базы данных"""
        file_path = filedialog.asksaveasfilename(
            title="Экспорт базы данных",
            defaultextension=".db",
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                import shutil
                db_path = self.db_manager.db_path if hasattr(self.db_manager, 'db_path') else 'project_manager.db'
                shutil.copy2(db_path, file_path)
                messagebox.showinfo("Успех", f"База данных экспортирована в {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта: {str(e)}")
    
    def import_database(self):
        """Импорт базы данных"""
        file_path = filedialog.askopenfilename(
            title="Импорт базы данных",
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")]
        )
        
        if file_path:
            if messagebox.askyesno("Подтверждение", 
                                  "Импорт заменит текущую базу данных. Продолжить?"):
                try:
                    import shutil
                    db_path = self.db_manager.db_path if hasattr(self.db_manager, 'db_path') else 'project_manager.db'
                    shutil.copy2(file_path, db_path)
                    
                    # Обновить интерфейс
                    self.refresh_commands_list()
                    self.refresh_snapshots_list()
                    self.update_database_status()
                    
                    messagebox.showinfo("Успех", "База данных импортирована")
                    
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка импорта: {str(e)}")
    
    def recreate_database(self):
        """Пересоздание базы данных"""
        if messagebox.askyesno("Подтверждение", 
                              "Пересоздать базу данных? Все данные будут потеряны!"):
            try:
                self.db_manager.recreate_database()
                
                # Обновить интерфейс
                self.refresh_commands_list()
                self.refresh_snapshots_list()
                self.update_database_status()
                
                messagebox.showinfo("Успех", "База данных пересоздана")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка пересоздания БД: {str(e)}")

    def refresh_project_files(self):
        """Обновление списка файлов проекта"""
        if not self.current_directory:
            return
        
        # Очистка дерева
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)
        
        # Показать индикатор загрузки
        self.project_tree.insert("", tk.END, text="Анализ директории...", values=('loading', '', '', ''))
        self.root.update()
        
        try:
            # Анализ директории
            stats = self.analyzer.analyze_directory(self.current_directory)
            
            # Очистка индикатора загрузки
            for item in self.project_tree.get_children():
                self.project_tree.delete(item)
            
            # Заполнение дерева
            self.populate_tree(self.project_tree, "", stats['file_tree'])
            
            # Обновить статистику в статус-баре
            status_text = f"Директория: {self.current_directory} | Файлов: {stats['files']} | Строк: {stats['lines']}"
            if stats.get('truncated'):
                status_text += " | ℹ️ Анализ ограничен (1000+ файлов)"
            self.status_label.config(text=status_text)
            
        except Exception as e:
            # Очистка индикатора загрузки
            for item in self.project_tree.get_children():
                self.project_tree.delete(item)
            
            # Показать ошибку
            self.project_tree.insert("", tk.END, text=f"Ошибка анализа: {str(e)}", values=('error', '', '', ''))
            messagebox.showerror("Ошибка", f"Ошибка при анализе директории:\n{str(e)}")

    def setup_file_colors(self):
        """Настройка цветовых тегов для файлов"""
        # Настройка цветов для разных типов файлов
        self.project_tree.tag_configure('folder', foreground='black')
        self.project_tree.tag_configure('folder_with_executables', foreground='darkgreen', font=('TkDefaultFont', 9, 'bold'))
        self.project_tree.tag_configure('exe_file', foreground='green', font=('TkDefaultFont', 9, 'bold'))
        self.project_tree.tag_configure('apk_file', foreground='green', font=('TkDefaultFont', 9, 'bold'))
        self.project_tree.tag_configure('dart_file', foreground='blue')
        self.project_tree.tag_configure('python_file', foreground='darkgreen')
        self.project_tree.tag_configure('yaml_file', foreground='purple')
        self.project_tree.tag_configure('json_file', foreground='orange')
        self.project_tree.tag_configure('image_file', foreground='darkcyan')
        self.project_tree.tag_configure('text_file', foreground='gray')
        self.project_tree.tag_configure('default_file', foreground='black')

    def find_executables_in_directory(self, directory_path, max_depth=2):
        """Поиск .exe и .apk файлов в директории с ограничением глубины"""
        executables = []
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            return executables
        
        try:
            for root, dirs, files in os.walk(directory_path):
                # Ограничиваем глубину поиска
                level = root.replace(directory_path, '').count(os.sep)
                if level >= max_depth:
                    dirs[:] = []  # Не идем глубже
                    continue
                
                for file in files:
                    if file.lower().endswith(('.exe', '.apk')):
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, directory_path)
                        executables.append({
                            'name': file,
                            'path': full_path,
                            'relative_path': rel_path,
                            'type': 'exe' if file.lower().endswith('.exe') else 'apk'
                        })
        except (PermissionError, OSError):
            pass  # Игнорируем ошибки доступа
        
        return executables
    
    def has_executables_in_subdirs(self, directory_path):
        """Проверяет, есть ли исполняемые файлы в поддиректориях"""
        executables = self.find_executables_in_directory(directory_path, max_depth=3)
        return len(executables) > 0

    def get_file_tag(self, filename):
        """Получение тега для файла на основе расширения"""
        _, ext = os.path.splitext(filename.lower())
        
        if ext == '.exe':
            return 'exe_file'
        elif ext == '.apk':
            return 'apk_file'
        elif ext == '.dart':
            return 'dart_file'
        elif ext == '.py':
            return 'python_file'
        elif ext in ['.yaml', '.yml']:
            return 'yaml_file'
        elif ext == '.json':
            return 'json_file'
        elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg']:
            return 'image_file'
        elif ext in ['.txt', '.md', '.log']:
            return 'text_file'
        else:
            return 'default_file'

    def populate_tree(self, tree, parent, file_tree):
        """Заполнение дерева файлами с цветовой дифференциацией"""
        for name, item in file_tree.items():
            if item['type'] == 'folder':
                # Определяем тег для папки
                folder_tag = 'folder'
                
                # Проверяем, содержит ли папка исполняемые файлы
                folder_path = item.get('path')
                if folder_path and self.has_executables_in_subdirs(folder_path):
                    folder_tag = 'folder_with_executables'
                
                folder_id = tree.insert(parent, tk.END, text=name, values=('folder', '', '', ''), tags=(folder_tag,))
                # Добавляем путь к папке как дополнительный тег для контекстного меню
                if folder_path:
                    tree.item(folder_id, tags=(folder_tag, folder_path))
                
                self.populate_tree(tree, folder_id, item['children'])
            else:
                stats = item['stats']
                file_tag = self.get_file_tag(name)
                tree.insert(parent, tk.END, text=name, 
                          values=('file', f"{stats['size']} б", stats['lines'], stats['characters']),
                          tags=(item['path'], file_tag))

    def execute_main_action(self):
        """Выполнение основного действия в зависимости от режима"""
        if not self.current_directory:
            messagebox.showwarning("Предупреждение", "Сначала выберите директорию!")
            return
        
        mode = self.project_mode.get()
        
        if mode == "new":
            self.create_flutter_project()
        elif mode == "analyze":
            self.analyze_changes()
        elif mode == "compare":
            if self.project1_var.get() and self.project2_var.get():
                self.compare_projects()
            else:
                messagebox.showwarning("Предупреждение", "Выберите оба проекта для сравнения!")

    def create_flutter_project(self):
        """Создание минимального Flutter проекта"""
        project_name = simpledialog.askstring("Создание проекта", "Введите название проекта:")
        if not project_name:
            return
        
        project_dir = os.path.join(self.current_directory, project_name)
        if os.path.exists(project_dir):
            if not messagebox.askyesno("Проект существует", f"Проект {project_name} уже существует. Продолжить?"):
                return
        else:
            os.makedirs(project_dir)
        
        # Создание базовой структуры Flutter проекта
        self.create_flutter_structure(project_dir, project_name)
        
        messagebox.showinfo("Успех", f"Проект {project_name} создан в {project_dir}")
        self.refresh_project_files()

    def create_flutter_structure(self, project_dir, project_name):
        """Создание базовой структуры Flutter проекта"""
        # Создание директорий
        os.makedirs(os.path.join(project_dir, 'lib'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'test'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'android'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'ios'), exist_ok=True)
        
        # Создание основных файлов
        self.create_file(os.path.join(project_dir, 'pubspec.yaml'), self.get_pubspec_template(project_name))
        self.create_file(os.path.join(project_dir, 'lib', 'main.dart'), self.get_main_dart_template())
        self.create_file(os.path.join(project_dir, 'README.md'), f"# {project_name}\n\nA Flutter project created by Flutter Project Manager.")
        self.create_file(os.path.join(project_dir, '.gitignore'), self.get_gitignore_template())

    def create_file(self, file_path, content):
        """Создание файла с содержимым"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def get_pubspec_template(self, project_name):
        return f"""name: {project_name}
description: A new Flutter project.

version: 1.0.0+1

environment:
  sdk: ">=2.12.0 <4.0.0"

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.2

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^2.0.0

flutter:
  uses-material-design: true
"""

    def get_main_dart_template(self):
        return """import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'Flutter Demo Home Page'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  int _counter = 0;

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text(
              'You have pushed the button this many times:',
            ),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ),
    );
  }
}
"""

    def get_gitignore_template(self):
        return """# Miscellaneous
*.class
*.log
*.pyc
*.swp
.DS_Store
.atom/
.buildlog/
.history
.svn/
migrate_working_dir/

# IntelliJ related
*.iml
*.ipr
*.iws
.idea/

# The .vscode folder contains launch configuration and tasks you configure in
# VS Code which you may wish to be included in version control, so this line
# is commented out by default.
#.vscode/

# Flutter/Dart/Pub related
**/doc/api/
**/ios/Flutter/.last_build_id
.dart_tool/
.flutter-plugins
.flutter-plugins-dependencies
.packages
.pub-cache/
.pub/
/build/

# Symbolication related
app.*.symbols

# Obfuscation related
app.*.map.json

# Android Studio will place build artifacts here
/android/app/debug
/android/app/profile
/android/app/release
"""

    # Остальные методы для работы с командами, снапшотами и сравнением...
    def show_file_context_menu(self, event):
        """Показ контекстного меню для файлов"""
        try:
            # Получаем выбранный элемент
            selected = self.project_tree.selection()
            if selected:
                item = self.project_tree.item(selected[0])
                
                # Удаляем предыдущие подменю исполняемых файлов
                try:
                    self.file_context_menu.delete("Исполняемые файлы")
                except tk.TclError:
                    pass
                
                # Проверяем, есть ли исполняемые файлы в выбранной папке
                selected_path = None
                if item['tags'] and len(item['tags']) > 1:
                    selected_path = item['tags'][1]  # Путь к папке
                elif item['tags']:
                    file_path = item['tags'][0]
                    if os.path.isdir(file_path):
                        selected_path = file_path
                    else:
                        selected_path = os.path.dirname(file_path)
                else:
                    selected_path = self.get_folder_path_from_tree_item(selected[0])
                
                if selected_path and os.path.isdir(selected_path):
                    executables = self.find_executables_in_directory(selected_path, max_depth=3)
                    
                    if executables:
                        # Создаем подменю для исполняемых файлов
                        exe_submenu = tk.Menu(self.file_context_menu, tearoff=0)
                        
                        for exe_info in executables[:10]:  # Ограничиваем до 10 файлов
                            icon = "🟢" if exe_info['type'] == 'exe' else "📱"
                            label = f"{icon} {exe_info['name']} ({exe_info['relative_path']})"
                            exe_submenu.add_command(
                                label=label,
                                command=lambda path=exe_info['path']: self.run_executable(path)
                            )
                        
                        if len(executables) > 10:
                            exe_submenu.add_separator()
                            exe_submenu.add_command(
                                label=f"... и еще {len(executables) - 10} файлов",
                                state="disabled"
                            )
                        
                        # Добавляем подменю к основному контекстному меню
                        self.file_context_menu.add_cascade(
                            label="🚀 Исполняемые файлы",
                            menu=exe_submenu
                        )
            
            self.file_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.file_context_menu.grab_release()

    def open_in_editor(self, event=None):
        """Открытие файла в редакторе"""
        selected = self.project_tree.selection()
        if selected:
            item = self.project_tree.item(selected[0])
            if item['tags']:
                file_path = item['tags'][0]
                # Использовать настроенный редактор
                if not self.settings_manager.open_file_with_editor(file_path):
                    messagebox.showerror("Ошибка", "Не удалось открыть файл в редакторе")

    def refresh_commands_list(self):
        """Обновление списка команд"""
        self.commands_listbox.delete(0, tk.END)
        commands = self.db_manager.get_commands()
        for cmd in commands:
            self.commands_listbox.insert(tk.END, f"{cmd['name']} - {cmd['description']}")

    def refresh_snapshots_list(self):
        """Обновление списка снапшотов"""
        for item in self.snapshots_tree.get_children():
            self.snapshots_tree.delete(item)
        
        snapshots = self.snapshot_manager.list_snapshots()
        for snap in snapshots:
            compressed_text = "Да" if snap['compressed'] else "Нет"
            self.snapshots_tree.insert("", tk.END, text=snap['name'],
                                     values=(snap['description'], snap['created_date'], compressed_text),
                                     tags=(snap['id'],))

    def create_command_sequence(self):
        """Создание новой последовательности команд"""
        # Открытие диалога для создания команд
        CommandDialog(self.root, self.db_manager, self.refresh_commands_list)

    def execute_selected_commands(self):
        """Выполнение выбранных команд"""
        selection = self.commands_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите команды для выполнения!")
            return
        
        commands = self.db_manager.get_commands()
        for index in selection:
            cmd = commands[index]
            self.execute_command_sequence(cmd['command_sequence'])

    def execute_command_sequence(self, commands):
        """Выполнение последовательности команд"""
        if not self.current_directory:
            messagebox.showwarning("Предупреждение", "Сначала выберите рабочую директорию!")
            return
        
        for cmd in commands:
            try:
                result = subprocess.run(cmd, shell=True, cwd=self.current_directory, 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    messagebox.showerror("Ошибка", f"Ошибка выполнения команды: {cmd}\n{result.stderr}")
                    break
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка выполнения команды: {cmd}\n{str(e)}")
                break

    def create_snapshot_dialog(self):
        """Диалог создания снапшота"""
        if not self.current_directory:
            messagebox.showwarning("Предупреждение", "Сначала выберите директорию!")
            return
        
        SnapshotDialog(self.root, self.snapshot_manager, self.current_directory, 
                      self.refresh_snapshots_list)

    def analyze_changes(self):
        """Анализ изменений в проекте"""
        if not self.current_directory:
            messagebox.showwarning("Предупреждение", "Сначала выберите директорию!")
            return
        
        # Показ результатов анализа
        AnalysisResultsDialog(self.root, self.analyzer, self.current_directory)

    def select_project_for_comparison(self, project_num):
        """Выбор проекта для сравнения"""
        dir_path = filedialog.askdirectory(title=f"Выберите проект {project_num}")
        if dir_path:
            if project_num == 1:
                self.project1_var.set(dir_path)
            else:
                self.project2_var.set(dir_path)

    def compare_projects(self):
        """Сравнение двух проектов"""
        project1 = self.project1_var.get()
        project2 = self.project2_var.get()
        
        if not project1 or not project2:
            messagebox.showwarning("Предупреждение", "Выберите оба проекта для сравнения!")
            return
        
        comparison = self.analyzer.compare_projects(project1, project2)
        
        # Заполнение деревьев сравнения
        self.populate_comparison_trees(comparison)

    def populate_comparison_trees(self, comparison):
        """Заполнение деревьев сравнения"""
        # Очистка деревьев
        for item in self.comparison_tree1.get_children():
            self.comparison_tree1.delete(item)
        for item in self.comparison_tree2.get_children():
            self.comparison_tree2.delete(item)
        
        # Заполнение статистикой
        stats1 = comparison['project1']['stats']
        stats2 = comparison['project2']['stats']
        
        # Добавление корневых элементов со статистикой
        self.comparison_tree1.insert("", tk.END, text="Проект 1", 
                                    values=(stats1['folders'], stats1['files'], stats1['lines'], stats1['characters']))
        self.comparison_tree2.insert("", tk.END, text="Проект 2", 
                                    values=(stats2['folders'], stats2['files'], stats2['lines'], stats2['characters']))

    def setup_hotkeys(self):
        """Настройка горячих клавиш"""
        hotkeys = self.settings_manager.get_hotkeys()
        
        # Привязка горячих клавиш
        for action, hotkey in hotkeys.items():
            if hotkey:
                try:
                    parsed_hotkey = self.settings_manager.parse_hotkey(hotkey)
                    if action == "select_directory":
                        self.root.bind_all(parsed_hotkey, lambda e: self.select_directory())
                    elif action == "create_project":
                        self.root.bind_all(parsed_hotkey, lambda e: self.create_flutter_project())
                    elif action == "create_snapshot":
                        self.root.bind_all(parsed_hotkey, lambda e: self.create_snapshot_dialog())
                    elif action == "analyze_changes":
                        self.root.bind_all(parsed_hotkey, lambda e: self.analyze_changes())
                    elif action == "open_file":
                        self.root.bind_all(parsed_hotkey, lambda e: self.open_in_editor())
                    elif action == "refresh":
                        self.root.bind_all(parsed_hotkey, lambda e: self.refresh_project_files())
                    elif action == "exit":
                        self.root.bind_all(parsed_hotkey, lambda e: self.root.quit())
                except Exception as e:
                    print(f"Ошибка привязки горячей клавиши {hotkey} для {action}: {e}")
    
    # Реализованные методы настроек
    def configure_editors(self):
        """Настройка редакторов"""
        EditorSettingsDialog(self.root, self.settings_manager)
    
    def configure_hotkeys(self):
        """Настройка горячих клавиш"""
        HotkeySettingsDialog(self.root, self.settings_manager)
    
    def configure_analysis(self):
        """Настройка анализа проекта"""
        AnalysisSettingsDialog(self.root, self)
    
    def configure_auto_search(self):
        """Настройка автопоиска файлов"""
        AutoSearchSettingsDialog(self.root, self)
    
    def backup_settings(self):
        messagebox.showinfo("Резервное копирование", "Функция резервного копирования будет реализована")
    
    def show_file_diff(self):
        messagebox.showinfo("Различия", "Функция показа различий будет реализована")
    
    def copy_file(self):
        messagebox.showinfo("Копирование", "Функция копирования файла будет реализована")
    
    def rename_file(self):
        messagebox.showinfo("Переименование", "Функция переименования файла будет реализована")
    
    def delete_command(self):
        messagebox.showinfo("Удаление", "Функция удаления команды будет реализована")
    
    def restore_snapshot(self):
        messagebox.showinfo("Восстановление", "Функция восстановления снапшота будет реализована")
    
    def copy_snapshot(self):
        messagebox.showinfo("Копирование", "Функция копирования снапшота будет реализована")
    
    def compare_with_snapshot(self):
        messagebox.showinfo("Сравнение", "Функция сравнения со снапшотом будет реализована")
    
    def delete_snapshot(self):
        messagebox.showinfo("Удаление", "Функция удаления снапшота будет реализована")

    # Методы поиска
    def focus_search_tab(self):
        """Переключение на вкладку поиска и фокус на поле ввода"""
        # Найти индекс вкладки поиска
        for i in range(self.notebook.index("end")):
            if "🔍 Поиск" in self.notebook.tab(i, "text"):
                self.notebook.select(i)
                # Установить фокус на поле поиска
                self.root.after(100, lambda: self.quick_search_var.get())
                break

    def quick_search(self, event=None):
        """Выполнение быстрого поиска"""
        # Устанавливаем директорию для поиска по умолчанию, если не выбрана
        search_directory = self.current_directory
        if not search_directory:
            messagebox.showwarning("Предупреждение", "Сначала выберите директорию проекта!")
            return

        query = self.quick_search_var.get().strip()
        if not query:
            messagebox.showwarning("Предупреждение", "Введите текст для поиска!")
            return

        # Параметры поиска из чекбоксов
        case_sensitive = self.search_case_sensitive.get()
        use_regex = self.search_use_regex.get()
        filename_only = self.search_filename_only.get()

        # Выполнение поиска с указанной директорией
        self.perform_search(query, case_sensitive, use_regex, filename_only, search_directory)

    def open_advanced_search(self):
        """Открытие диалога расширенного поиска"""
        if not self.current_directory:
            messagebox.showwarning("Предупреждение", "Сначала выберите директорию для поиска!")
            return

        # Открыть диалог расширенного поиска
        SearchDialog(self.root, self.search_manager, self.current_directory, self.on_search_results)

    def search_in_files(self):
        """Поиск в содержимом файлов"""
        if not self.current_directory:
            messagebox.showwarning("Предупреждение", "Сначала выберите директорию для поиска!")
            return

        # Запросить текст для поиска
        search_text = simpledialog.askstring("Поиск в файлах", "Введите текст для поиска в содержимом файлов:")
        if not search_text:
            return

        # Выполнить поиск в содержимом файлов
        self.perform_content_search(search_text)

    def perform_search(self, query, case_sensitive=False, use_regex=False, filename_only=False, search_directory=None):
        """Выполнение поиска с заданными параметрами"""
        try:
            # Очистить предыдущие результаты
            self.clear_search_results()

            # Обновить статус
            self.search_stats_label.config(text="Поиск...")
            self.root.update()

            # Использовать переданную директорию или текущую
            search_path = search_directory or self.current_directory
            if not search_path:
                messagebox.showwarning("Предупреждение", "Не указана директория для поиска!")
                return

            # Параметры поиска
            search_params = {
                'query': query,
                'path': search_path,
                'case_sensitive': case_sensitive,
                'use_regex': use_regex,
                'filename_only': filename_only,
                'max_results': 1000
            }

            # Выполнить поиск
            if filename_only:
                results = self.search_manager.search_files(**search_params)
            else:
                results = self.search_manager.search_in_files(**search_params)

            # Отобразить результаты
            self.display_search_results(results, query)

        except Exception as e:
            messagebox.showerror("Ошибка поиска", f"Произошла ошибка при поиске:\n{str(e)}")
            self.search_stats_label.config(text="Ошибка поиска")

    def perform_content_search(self, search_text, file_patterns=None, exclude_patterns=None, search_directory=None):
        """Выполнение поиска в содержимом файлов"""
        try:
            # Очистить предыдущие результаты
            self.clear_search_results()

            # Обновить статус
            self.search_stats_label.config(text="Поиск в файлах...")
            self.root.update()

            # Использовать переданную директорию или текущую
            search_path = search_directory or self.current_directory
            if not search_path:
                messagebox.showwarning("Предупреждение", "Не указана директория для поиска!")
                return

            # Параметры поиска
            search_params = {
                'query': search_text,
                'path': search_path,
                'file_patterns': file_patterns or ['*.py', '*.dart', '*.yaml', '*.json', '*.md', '*.txt'],
                'exclude_patterns': exclude_patterns or ['.git', 'node_modules', '.dart_tool', 'build'],
                'max_results': 1000
            }

            # Выполнить поиск
            results = self.search_manager.search_in_files(**search_params)

            # Отобразить результаты
            self.display_search_results(results, search_text)

        except Exception as e:
            messagebox.showerror("Ошибка поиска", f"Произошла ошибка при поиске:\n{str(e)}")
            self.search_stats_label.config(text="Ошибка поиска")

    def perform_content_search_in_directory(self, search_text, search_directory, file_patterns=None, exclude_patterns=None):
        """Выполнение поиска в содержимом файлов в указанной директории"""
        self.perform_content_search(search_text, file_patterns, exclude_patterns, search_directory)

    def display_search_results(self, results, query):
        """Отображение результатов поиска"""
        # Очистить предыдущие результаты
        for item in self.search_results_tree.get_children():
            self.search_results_tree.delete(item)

        if not results:
            self.search_stats_label.config(text=f"Ничего не найдено для '{query}'")
            return

        # Добавить результаты в дерево
        for result in results:
            result_type = result.get('type', 'file')
            filename = os.path.basename(result['path'])
            file_path = result['path']
            file_size = result.get('size', 0)
            line_number = result.get('line_number', '')
            content = result.get('content', '').strip() if result.get('content') else ''

            # Форматирование размера файла
            if file_size > 1024*1024:
                size_str = f"{file_size/(1024*1024):.1f} МБ"
            elif file_size > 1024:
                size_str = f"{file_size/1024:.1f} КБ"
            else:
                size_str = f"{file_size} Б"

            # Ограничить длину содержимого
            if len(content) > 100:
                content = content[:100] + "..."

            # Добавить в дерево
            item_id = self.search_results_tree.insert("", tk.END, values=(
                result_type.capitalize(),
                filename,
                file_path,
                size_str,
                str(line_number) if line_number else '',
                content
            ), tags=(file_path,))

        # Обновить статистику
        self.search_stats_label.config(text=f"Найдено {len(results)} результатов для '{query}'")

        # Переключиться на вкладку поиска, если она не активна
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        if "🔍 Поиск" not in current_tab:
            self.focus_search_tab()

    def on_search_results(self, results, query):
        """Callback для обработки результатов из диалога поиска"""
        self.display_search_results(results, query)

    def clear_search_results(self):
        """Очистка результатов поиска"""
        for item in self.search_results_tree.get_children():
            self.search_results_tree.delete(item)
        self.search_stats_label.config(text="Результаты поиска очищены")

    def show_search_context_menu(self, event):
        """Показ контекстного меню для результатов поиска"""
        try:
            self.search_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.search_context_menu.grab_release()

    def open_search_result_file(self, event=None):
        """Открытие файла из результатов поиска"""
        selection = self.search_results_tree.selection()
        if not selection:
            return

        item = self.search_results_tree.item(selection[0])
        if item['tags']:
            file_path = item['tags'][0]
            if os.path.isfile(file_path):
                # Использовать настроенный редактор
                if not self.settings_manager.open_file_with_editor(file_path):
                    messagebox.showerror("Ошибка", "Не удалось открыть файл в редакторе")
            else:
                messagebox.showwarning("Предупреждение", "Файл не найден")

    def open_search_result_folder(self):
        """Открытие папки из результатов поиска"""
        selection = self.search_results_tree.selection()
        if not selection:
            return

        item = self.search_results_tree.item(selection[0])
        if item['tags']:
            file_path = item['tags'][0]
            folder_path = os.path.dirname(file_path)
            if os.path.exists(folder_path):
                # Открыть папку в проводнике
                if os.name == 'nt':  # Windows
                    os.startfile(folder_path)
                elif os.name == 'posix':  # Linux/Mac
                    subprocess.run(['xdg-open', folder_path])
            else:
                messagebox.showwarning("Предупреждение", "Папка не найдена")

    def copy_search_result_path(self):
        """Копирование пути файла из результатов поиска"""
        selection = self.search_results_tree.selection()
        if not selection:
            return

        item = self.search_results_tree.item(selection[0])
        if item['tags']:
            file_path = item['tags'][0]
            # Копировать в буфер обмена
            self.root.clipboard_clear()
            self.root.clipboard_append(file_path)
            messagebox.showinfo("Копирование", f"Путь скопирован в буфер обмена:\n{file_path}")

    def show_in_project_tree(self):
        """Показать файл в дереве проекта"""
        selection = self.search_results_tree.selection()
        if not selection:
            return

        item = self.search_results_tree.item(selection[0])
        if item['tags']:
            file_path = item['tags'][0]
            # Переключиться на вкладку проектов
            self.notebook.select(0)

            # Найти и выделить файл в дереве проекта
            self.find_and_select_in_project_tree(file_path)

    def find_and_select_in_project_tree(self, file_path):
        """Поиск и выделение файла в дереве проекта"""
        def search_in_tree(tree, target_path):
            for item in tree.get_children():
                item_tags = tree.item(item)['tags']
                if item_tags and item_tags[0] == target_path:
                    tree.selection_set(item)
                    tree.focus(item)
                    tree.see(item)
                    return True
                # Рекурсивный поиск в дочерних элементах
                if search_in_tree(tree, target_path):
                    return True
            return False

        if not search_in_tree(self.project_tree, file_path):
            messagebox.showinfo("Информация", "Файл не найден в текущем дереве проекта")

    def configure_advanced_hotkeys(self):
        """Настройка расширенных горячих клавиш"""
        AdvancedHotkeySettingsDialog(self.root, self.settings_manager)
    
    # Методы поиска из контекстного меню
    def search_in_selected_folder(self):
        """Поиск в выбранной папке из контекстного меню"""
        selected = self.project_tree.selection()
        if not selected:
            return
        
        item = self.project_tree.item(selected[0])
        selected_path = None
        
        if item['tags']:
            # Выбран файл или папка с путем
            file_path = item['tags'][0]
            if os.path.isdir(file_path):
                selected_path = file_path
            else:
                selected_path = os.path.dirname(file_path)
        else:
            # Выбрана папка - найти полный путь
            selected_path = self.get_folder_path_from_tree_item(selected[0])
        
        if selected_path and os.path.exists(selected_path):
            # Переключиться на вкладку поиска
            self.focus_search_tab()
            
            # Запросить текст для поиска
            search_text = simpledialog.askstring(
                "Поиск в папке", 
                f"Введите текст для поиска в папке:\n{selected_path}"
            )
            
            if search_text:
                # Выполнить поиск файлов в выбранной папке
                self.perform_search(search_text, filename_only=True, search_directory=selected_path)
    
    def search_text_in_selected_folder(self):
        """Поиск текста в файлах выбранной папки"""
        selected = self.project_tree.selection()
        if not selected:
            return
        
        item = self.project_tree.item(selected[0])
        selected_path = None
        
        if item['tags']:
            # Выбран файл или папка с путем
            file_path = item['tags'][0]
            if os.path.isdir(file_path):
                selected_path = file_path
            else:
                selected_path = os.path.dirname(file_path)
        else:
            # Выбрана папка - найти полный путь
            selected_path = self.get_folder_path_from_tree_item(selected[0])
        
        if selected_path and os.path.exists(selected_path):
            # Переключиться на вкладку поиска
            self.focus_search_tab()
            
            # Запросить текст для поиска
            search_text = simpledialog.askstring(
                "Поиск текста в файлах", 
                f"Введите текст для поиска в содержимом файлов:\n{selected_path}"
            )
            
            if search_text:
                # Выполнить поиск в содержимом файлов в выбранной папке
                self.perform_content_search_in_directory(search_text, selected_path)
    
    def get_folder_path_from_tree_item(self, item_id):
        """Получение полного пути папки из элемента дерева"""
        path_parts = []
        current_item = item_id
        
        while current_item:
            item_text = self.project_tree.item(current_item)['text']
            if item_text:
                path_parts.append(item_text)
            current_item = self.project_tree.parent(current_item)
        
        if path_parts:
            path_parts.reverse()
            return os.path.join(self.current_directory, *path_parts)
        
        return self.current_directory
    
    def run_executable(self, exe_path):
        """Запуск исполняемого файла"""
        if not os.path.exists(exe_path):
            messagebox.showerror("Ошибка", f"Файл не найден:\n{exe_path}")
            return
        
        try:
            # Получаем директорию файла
            exe_dir = os.path.dirname(exe_path) 
            exe_name = os.path.basename(exe_path)
            
            # Запускаем файл в его директории
            if exe_path.lower().endswith('.exe'):
                # Для .exe файлов запускаем напрямую
                subprocess.Popen([exe_path], cwd=exe_dir, shell=False)
                messagebox.showinfo("Запуск программы", f"Запущена программа:\n{exe_name}")
            elif exe_path.lower().endswith('.apk'):
                # Для .apk файлов показываем информацию
                result = messagebox.askyesno(
                    "APK файл", 
                    f"Найден APK файл:\n{exe_name}\n\n" +
                    "Открыть папку с файлом для ручной установки?"
                )
                if result:
                    os.startfile(exe_dir)
        except Exception as e:
            messagebox.showerror(
                "Ошибка запуска", 
                f"Не удалось запустить файл:\n{exe_name}\n\nОшибка: {str(e)}"
            )


# Диалоговые окна
class CommandDialog:
    def __init__(self, parent, db_manager, refresh_callback):
        self.db_manager = db_manager
        self.refresh_callback = refresh_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Создание последовательности команд")
        self.dialog.geometry("600x400")
        
        self.create_interface()
    
    def create_interface(self):
        # Название и описание
        ttk.Label(self.dialog, text="Название:").pack(pady=5)
        self.name_entry = ttk.Entry(self.dialog, width=50)
        self.name_entry.pack(pady=5)
        
        ttk.Label(self.dialog, text="Описание:").pack(pady=5)
        self.desc_entry = ttk.Entry(self.dialog, width=50)
        self.desc_entry.pack(pady=5)
        
        # Список команд
        ttk.Label(self.dialog, text="Команды (по одной на строку):").pack(pady=(10, 5))
        self.commands_text = tk.Text(self.dialog, height=15, width=70)
        self.commands_text.pack(pady=5, fill=tk.BOTH, expand=True)
        
        # Кнопки
        buttons_frame = ttk.Frame(self.dialog)
        buttons_frame.pack(pady=10)
        
        ttk.Button(buttons_frame, text="Сохранить", command=self.save_commands).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_commands(self):
        name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip()
        commands_text = self.commands_text.get("1.0", tk.END).strip()
        
        if not name or not commands_text:
            messagebox.showwarning("Предупреждение", "Заполните название и команды!")
            return
        
        commands = [cmd.strip() for cmd in commands_text.split('\n') if cmd.strip()]
        
        if self.db_manager.save_command(name, description, commands):
            messagebox.showinfo("Успех", "Последовательность команд сохранена!")
            self.refresh_callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("Ошибка", "Ошибка сохранения команд!")


class SnapshotDialog:
    def __init__(self, parent, snapshot_manager, source_path, refresh_callback):
        self.snapshot_manager = snapshot_manager
        self.source_path = source_path
        self.refresh_callback = refresh_callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Создание снапшота")
        self.dialog.geometry("400x300")
        
        self.create_interface()
    
    def create_interface(self):
        ttk.Label(self.dialog, text="Название снапшота:").pack(pady=5)
        self.name_entry = ttk.Entry(self.dialog, width=40)
        self.name_entry.pack(pady=5)
        
        ttk.Label(self.dialog, text="Описание:").pack(pady=5)
        self.desc_text = tk.Text(self.dialog, height=5, width=40)
        self.desc_text.pack(pady=5)
        
        self.compress_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.dialog, text="Сжать снапшот", variable=self.compress_var).pack(pady=10)
        
        ttk.Button(self.dialog, text="Создать снапшот", command=self.create_snapshot).pack(pady=10)
    
    def create_snapshot(self):
        name = self.name_entry.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        compress = self.compress_var.get()
        
        if not name:
            messagebox.showwarning("Предупреждение", "Введите название снапшота!")
            return
        
        result = self.snapshot_manager.create_snapshot(self.source_path, name, description, compress)
        
        if result:
            messagebox.showinfo("Успех", f"Снапшот создан: {result}")
            self.refresh_callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("Ошибка", "Ошибка создания снапшота!")


class AnalysisResultsDialog:
    def __init__(self, parent, analyzer, project_path):
        self.analyzer = analyzer
        self.project_path = project_path
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Результаты анализа")
        self.dialog.geometry("800x600")
        
        self.create_interface()
        self.analyze_project()
    
    def create_interface(self):
        # Результаты анализа
        self.results_text = tk.Text(self.dialog, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def analyze_project(self):
        # Анализ проекта
        stats = self.analyzer.analyze_directory(self.project_path)
        
        results = f"""Анализ проекта: {self.project_path}

Статистика:
- Папок: {stats['folders']}
- Файлов: {stats['files']}
- Строк кода: {stats['lines']}
- Символов: {stats['characters']}

Структура проекта:
"""
        
        # Добавление структуры файлов
        def add_tree_to_results(tree, indent=0):
            result = ""
            for name, item in tree.items():
                prefix = "  " * indent + "├── "
                if item['type'] == 'folder':
                    result += f"{prefix}{name}/\n"
                    result += add_tree_to_results(item['children'], indent + 1)
                else:
                    stats = item['stats']
                    result += f"{prefix}{name} ({stats['lines']} строк, {stats['characters']} символов)\n"
            return result
        
        results += add_tree_to_results(stats['file_tree'])
        
        self.results_text.insert(tk.END, results)
        self.results_text.config(state=tk.DISABLED)


class DirectorySelectDialog:
    def __init__(self, parent, db_manager, callback):
        self.db_manager = db_manager
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Выбор директории")
        self.dialog.geometry("700x500")
        self.dialog.resizable(True, True)
        
        # Сделать диалог модальным
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.selected_directory = None
        
        self.create_interface()
        self.load_directory_history()
        
        # Центрировать диалог
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_interface(self):
        # Заголовок
        title_label = ttk.Label(self.dialog, text="Выберите директорию из истории или укажите новую", font=('Arial', 12, 'bold'))
        title_label.pack(pady=(10, 5))
        
        # Фрейм для списка директорий
        history_frame = ttk.LabelFrame(self.dialog, text="Ранее использованные директории")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Таблица с историей директорий
        columns = ("Путь", "Последнее использование", "Количество использований")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)
        
        # Настройка заголовков
        self.history_tree.heading("Путь", text="Путь к директории")
        self.history_tree.heading("Последнее использование", text="Последнее использование")
        self.history_tree.heading("Количество использований", text="Использований")
        
        # Настройка ширины столбцов
        self.history_tree.column("Путь", width=400, minwidth=300)
        self.history_tree.column("Последнее использование", width=150, minwidth=120)
        self.history_tree.column("Количество использований", width=100, minwidth=80)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Обработчик двойного клика
        self.history_tree.bind("<Double-1>", self.on_directory_double_click)
        
        # Кнопки
        buttons_frame = ttk.Frame(self.dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Левая часть - кнопка обзора
        left_frame = ttk.Frame(buttons_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(left_frame, text="📁 Обзор... (выбрать новую директорию)", 
               command=self.browse_new_directory).pack(side=tk.LEFT, padx=(0, 10))
        
        # Правая часть - кнопки действий
        right_frame = ttk.Frame(buttons_frame)
        right_frame.pack(side=tk.RIGHT)
        
        ttk.Button(right_frame, text="✅ Выбрать", command=self.select_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_frame, text="❌ Отмена", command=self.cancel).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(right_frame, text="🗑️ Удалить из истории", command=self.remove_from_history).pack(side=tk.LEFT)
        
        # Подсказка
        hint_label = ttk.Label(self.dialog, text="Подсказка: Двойной клик по строке для выбора директории", 
                           foreground="gray")
        hint_label.pack(pady=(0, 5))
    
    def load_directory_history(self):
        """Загрузка истории директорий"""
        # Очистка таблицы
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Получение истории из базы
        history = self.db_manager.get_directory_history(15)  # Получить последние 15 директорий
        
        if not history:
            # Если истории нет, показать сообщение
            self.history_tree.insert("", tk.END, values=(
                "История пуста. Нажмите 'Обзор...' для выбора первой директории",
                "-", "-"
            ))
            return
        
        # Заполнение таблицы
        for dir_info in history:
            # Форматирование даты
            try:
                from datetime import datetime
                last_used = datetime.fromisoformat(dir_info['last_used'])
                formatted_date = last_used.strftime("%d.%m.%Y %H:%M")
            except:
                formatted_date = dir_info['last_used']
            
            self.history_tree.insert("", tk.END, values=(
                dir_info['directory_path'],
                formatted_date,
                f"{dir_info['usage_count']} раз"
            ), tags=(dir_info['directory_path'],))
    
    def on_directory_double_click(self, event):
        """Обработка двойного клика по директории"""
        self.select_directory()
    
    def select_directory(self):
        """Выбор выделенной директории из списка"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите директорию из списка или нажмите 'Обзор...'")
            return
        
        item = self.history_tree.item(selection[0])
        if item['tags']:
            directory_path = item['tags'][0]
            
            # Проверить, что директория существует
            if not os.path.exists(directory_path):
                if messagebox.askyesno("Директория не найдена", 
                                      f"Директория {directory_path} больше не существует.\n\nУдалить её из истории?"):
                    self.db_manager.remove_directory_from_history(directory_path)
                    self.load_directory_history()
                return
            
            self.selected_directory = directory_path
            self.close_dialog()
    
    def browse_new_directory(self):
        """Открытие диалога выбора новой директории"""
        dir_path = filedialog.askdirectory(
            title="Выберите новую директорию",
            parent=self.dialog
        )
        
        if dir_path:
            self.selected_directory = dir_path
            self.close_dialog()
    
    def remove_from_history(self):
        """Удаление выбранной директории из истории"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите директорию для удаления из истории")
            return
        
        item = self.history_tree.item(selection[0])
        if item['tags']:
            directory_path = item['tags'][0]
            
            if messagebox.askyesno("Подтверждение", 
                                  f"Удалить директорию из истории?\n\n{directory_path}"):
                self.db_manager.remove_directory_from_history(directory_path)
                self.load_directory_history()
                messagebox.showinfo("Успех", "Директория удалена из истории")
    
    def cancel(self):
        """Отмена выбора"""
        self.selected_directory = None
        self.close_dialog()
    
    def close_dialog(self):
        """Закрытие диалога и вызов callback"""
        self.dialog.grab_release()
        self.dialog.destroy()
        if self.callback:
            self.callback(self.selected_directory)


class AnalysisSettingsDialog:
    """Диалог настроек анализа проекта"""
    def __init__(self, parent, main_app):
        self.main_app = main_app
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройки анализа проекта")
        self.dialog.geometry("500x350")
        self.dialog.resizable(False, False)
        
        # Сделать диалог модальным
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_interface()
        self.load_current_settings()
        
        # Центрировать диалог
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_interface(self):
        # Заголовок
        title_label = ttk.Label(self.dialog, text="Настройки анализа проекта", font=('Arial', 12, 'bold'))
        title_label.pack(pady=(10, 5))
        
        # Лимит файлов
        limit_frame = ttk.LabelFrame(self.dialog, text="Лимит анализа файлов")
        limit_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        self.no_limit_var = tk.BooleanVar()
        ttk.Checkbutton(limit_frame, text="Без лимитов (анализировать все файлы)", 
                        variable=self.no_limit_var, command=self.on_no_limit_toggle).pack(anchor="w", padx=10, pady=5)
        
        limit_controls_frame = ttk.Frame(limit_frame)
        limit_controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(limit_controls_frame, text="Максимум файлов:").pack(side=tk.LEFT)
        
        self.limit_var = tk.StringVar()
        self.limit_entry = ttk.Entry(limit_controls_frame, textvariable=self.limit_var, width=10)
        self.limit_entry.pack(side=tk.LEFT, padx=(10, 5))
        
        ttk.Label(limit_controls_frame, text="(0 = без лимитов)").pack(side=tk.LEFT)
        
        # Исключаемые папки
        exclude_frame = ttk.LabelFrame(self.dialog, text="Исключаемые папки")
        exclude_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        ttk.Label(exclude_frame, text="Папки, которые будут пропущены при анализе (по одной на строку):").pack(anchor="w", padx=10, pady=5)
        
        self.exclude_text = tk.Text(exclude_frame, height=8, width=50)
        exclude_scrollbar = ttk.Scrollbar(exclude_frame, orient="vertical", command=self.exclude_text.yview)
        self.exclude_text.configure(yscrollcommand=exclude_scrollbar.set)
        
        self.exclude_text.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)
        exclude_scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=5)
        
        # Кнопки
        buttons_frame = ttk.Frame(self.dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        ttk.Button(buttons_frame, text="Сохранить", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Отмена", command=self.cancel).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="По умолчанию", command=self.reset_to_defaults).pack(side=tk.LEFT)
    
    def on_no_limit_toggle(self):
        """Обработка чекбокса 'без лимитов'"""
        if self.no_limit_var.get():
            self.limit_entry.config(state='disabled')
            self.limit_var.set('0')
        else:
            self.limit_entry.config(state='normal')
            if self.limit_var.get() == '0':
                self.limit_var.set('1000')
    
    def load_current_settings(self):
        """Загрузка текущих настроек"""
        # Лимит файлов
        if self.main_app.analysis_file_limit is None or self.main_app.analysis_file_limit == 0:
            self.no_limit_var.set(True)
            self.limit_var.set('0')
            self.limit_entry.config(state='disabled')
        else:
            self.no_limit_var.set(False)
            self.limit_var.set(str(self.main_app.analysis_file_limit))
            self.limit_entry.config(state='normal')
        
        # Исключаемые папки
        excluded_folders = '\n'.join(self.main_app.analysis_excluded_folders)
        self.exclude_text.insert('1.0', excluded_folders)
    
    def save_settings(self):
        """Сохранение настроек"""
        try:
            # Лимит файлов
            if self.no_limit_var.get():
                self.main_app.analysis_file_limit = None
            else:
                limit_str = self.limit_var.get().strip()
                if limit_str == '' or limit_str == '0':
                    self.main_app.analysis_file_limit = None
                else:
                    limit = int(limit_str)
                    if limit <= 0:
                        self.main_app.analysis_file_limit = None
                    else:
                        self.main_app.analysis_file_limit = limit
            
            # Исключаемые папки
            excluded_text = self.exclude_text.get('1.0', tk.END).strip()
            if excluded_text:
                excluded_folders = [folder.strip() for folder in excluded_text.split('\n') if folder.strip()]
            else:
                excluded_folders = []
            self.main_app.analysis_excluded_folders = excluded_folders
            
            messagebox.showinfo("Успех", "Настройки анализа сохранены!")
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное значение лимита файлов. Введите число.")
    
    def reset_to_defaults(self):
        """Сброс к настройкам по умолчанию"""
        self.no_limit_var.set(True)
        self.limit_var.set('0')
        self.limit_entry.config(state='disabled')
        
        default_excluded = ['.git', 'node_modules', '.dart_tool', 'build', '__pycache__', '.vscode', '.idea']
        self.exclude_text.delete('1.0', tk.END)
        self.exclude_text.insert('1.0', '\n'.join(default_excluded))
    
    def cancel(self):
        """Отмена"""
        self.dialog.destroy()


class AutoSearchSettingsDialog:
    """Диалог настроек автопоиска файлов"""
    def __init__(self, parent, main_app):
        self.main_app = main_app
        self.pattern_vars = {}  # Словарь для хранения переменных чекбоксов
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройки автопоиска файлов")
        self.dialog.geometry("650x550")
        self.dialog.resizable(False, False)
        
        # Сделать диалог модальным
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_interface()
        self.load_current_settings()
        
        # Центрировать диалог
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_interface(self):
        # Заголовок
        title_label = ttk.Label(self.dialog, text="Настройки автоматического поиска файлов", font=('Arial', 12, 'bold'))
        title_label.pack(pady=(10, 5))
        
        # Описание
        desc_label = ttk.Label(self.dialog, text="При открытии проекта будет выполняться поиск файлов по указанным маскам.", 
                              wraplength=600, justify="left")
        desc_label.pack(pady=(0, 10))
        
        # Фрейм для настроек масок
        main_content = ttk.Frame(self.dialog)
        main_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Левая часть - список масок с чекбоксами
        left_frame = ttk.LabelFrame(main_content, text="Включенные маски поиска")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Фрейм для скролла списка масок
        masks_scroll_frame = ttk.Frame(left_frame)
        masks_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas и Scrollbar для прокрутки чекбоксов
        self.masks_canvas = tk.Canvas(masks_scroll_frame, height=300)
        masks_scrollbar = ttk.Scrollbar(masks_scroll_frame, orient="vertical", command=self.masks_canvas.yview)
        self.masks_canvas.configure(yscrollcommand=masks_scrollbar.set)
        
        self.masks_frame = ttk.Frame(self.masks_canvas)
        self.masks_canvas.create_window((0, 0), window=self.masks_frame, anchor="nw")
        
        self.masks_canvas.pack(side="left", fill="both", expand=True)
        masks_scrollbar.pack(side="right", fill="y")
        
        # Правая часть - управление масками
        right_frame = ttk.LabelFrame(main_content, text="Управление масками")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Поле для добавления новой маски
        ttk.Label(right_frame, text="Добавить маску:").pack(anchor="w", padx=5, pady=(10, 2))
        self.new_pattern_var = tk.StringVar()
        new_pattern_entry = ttk.Entry(right_frame, textvariable=self.new_pattern_var, width=15)
        new_pattern_entry.pack(padx=5, pady=(0, 5))
        new_pattern_entry.bind('<Return>', self.add_pattern)
        
        ttk.Button(right_frame, text="Добавить", command=self.add_pattern).pack(padx=5, pady=(0, 10))
        
        ttk.Separator(right_frame, orient='horizontal').pack(fill='x', padx=5, pady=5)
        
        # Кнопки управления
        ttk.Button(right_frame, text="Выбрать все", command=self.select_all_patterns).pack(padx=5, pady=2, fill='x')
        ttk.Button(right_frame, text="Снять все", command=self.deselect_all_patterns).pack(padx=5, pady=2, fill='x')
        ttk.Button(right_frame, text="Удалить выбранные", command=self.remove_selected_patterns).pack(padx=5, pady=2, fill='x')
        
        ttk.Separator(right_frame, orient='horizontal').pack(fill='x', padx=5, pady=5)
        
        # Примеры
        ttk.Label(right_frame, text="Примеры:", font=('Arial', 9, 'bold')).pack(anchor="w", padx=5, pady=(5, 2))
        examples_text = "*.exe\n*.apk\n*.jar\n*.msi\n*.deb\n*.dmg\n*.app\n*.zip\n*.rar"
        ttk.Label(right_frame, text=examples_text, font=('Arial', 8), foreground='gray').pack(anchor="w", padx=5)
        
        # Кнопки действий
        buttons_frame = ttk.Frame(self.dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        ttk.Button(buttons_frame, text="Сохранить", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Отмена", command=self.cancel).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="По умолчанию", command=self.reset_to_defaults).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Посмотреть результаты", command=self.show_current_results).pack(side=tk.LEFT)
    
    def create_pattern_checkboxes(self):
        """Создание чекбоксов для масок"""
        # Очистить предыдущие чекбоксы
        for widget in self.masks_frame.winfo_children():
            widget.destroy()
        
        self.pattern_vars.clear()
        
        # Создать чекбоксы для каждой маски
        for pattern in self.main_app.auto_search_patterns:
            var = tk.BooleanVar()
            var.set(self.main_app.auto_search_enabled_patterns.get(pattern, True))
            self.pattern_vars[pattern] = var
            
            cb = ttk.Checkbutton(self.masks_frame, text=pattern, variable=var)
            cb.pack(anchor="w", padx=5, pady=2)
        
        # Обновить размер canvas
        self.masks_frame.update_idletasks()
        self.masks_canvas.configure(scrollregion=self.masks_canvas.bbox("all"))
    
    def load_current_settings(self):
        """Загрузка текущих настроек"""
        # Убедиться, что у всех масок есть состояние включения
        for pattern in self.main_app.auto_search_patterns:
            if pattern not in self.main_app.auto_search_enabled_patterns:
                self.main_app.auto_search_enabled_patterns[pattern] = True
        
        self.create_pattern_checkboxes()
    
    def add_pattern(self, event=None):
        """Добавление новой маски"""
        new_pattern = self.new_pattern_var.get().strip()
        if not new_pattern:
            return
        
        # Проверить, что маска не дублируется
        if new_pattern in self.main_app.auto_search_patterns:
            messagebox.showwarning("Предупреждение", f"Маска '{new_pattern}' уже существует!")
            return
        
        # Добавить новую маску
        self.main_app.auto_search_patterns.append(new_pattern)
        self.main_app.auto_search_enabled_patterns[new_pattern] = True
        
        # Обновить интерфейс
        self.create_pattern_checkboxes()
        self.new_pattern_var.set("")
    
    def select_all_patterns(self):
        """Выбрать все маски"""
        for var in self.pattern_vars.values():
            var.set(True)
    
    def deselect_all_patterns(self):
        """Снять выбор со всех масок"""
        for var in self.pattern_vars.values():
            var.set(False)
    
    def remove_selected_patterns(self):
        """Удалить выбранные маски"""
        patterns_to_remove = []
        for pattern, var in self.pattern_vars.items():
            if var.get():  # Если маска выбрана
                patterns_to_remove.append(pattern)
        
        if not patterns_to_remove:
            messagebox.showwarning("Предупреждение", "Выберите маски для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", 
                              f"Удалить выбранные маски ({len(patterns_to_remove)} шт.)?\n\n" +
                              "\n".join(patterns_to_remove)):
            # Удалить маски
            for pattern in patterns_to_remove:
                if pattern in self.main_app.auto_search_patterns:
                    self.main_app.auto_search_patterns.remove(pattern)
                if pattern in self.main_app.auto_search_enabled_patterns:
                    del self.main_app.auto_search_enabled_patterns[pattern]
            
            # Обновить интерфейс
            self.create_pattern_checkboxes()
    
    def save_settings(self):
        """Сохранение настроек"""
        # Сохранить состояния чекбоксов
        for pattern, var in self.pattern_vars.items():
            self.main_app.auto_search_enabled_patterns[pattern] = var.get()
        
        # Обновить результаты поиска, если выбрана директория
        if self.main_app.current_directory:
            self.main_app.perform_auto_search()
        
        messagebox.showinfo("Успех", "Настройки автопоиска сохранены!")
        self.dialog.destroy()
    
    def reset_to_defaults(self):
        """Сброс к настройкам по умолчанию"""
        if messagebox.askyesno("Подтверждение", "Сбросить все настройки автопоиска к значениям по умолчанию?"):
            default_patterns = ['*.exe', '*.apk', '*.jar', '*.msi', '*.deb', '*.dmg', '*.app']
            
            self.main_app.auto_search_patterns = default_patterns.copy()
            self.main_app.auto_search_enabled_patterns = {pattern: True for pattern in default_patterns}
            
            # Обновить интерфейс
            self.create_pattern_checkboxes()
    
    def show_current_results(self):
        """Показать текущие результаты поиска"""
        if not self.main_app.current_directory:
            messagebox.showwarning("Предупреждение", "Сначала выберите директорию проекта!")
            return
        
        # Показать диалог с результатами
        AutoSearchResultsDialog(self.dialog, self.main_app)
    
    def cancel(self):
        """Отмена"""
        self.dialog.destroy()


class AutoSearchResultsDialog:
    """Диалог отображения результатов автопоиска"""
    def __init__(self, parent, main_app):
        self.main_app = main_app
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Результаты автопоиска")
        self.dialog.geometry("800x600")
        
        # Сделать диалог модальным
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_interface()
        self.perform_search_and_display()
        
        # Центрировать диалог
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_interface(self):
        # Заголовок
        title_label = ttk.Label(self.dialog, text="Результаты автоматического поиска файлов", font=('Arial', 12, 'bold'))
        title_label.pack(pady=(10, 5))
        
        # Информация о поиске
        self.info_label = ttk.Label(self.dialog, text="Поиск...")
        self.info_label.pack(pady=(0, 10))
        
        # Таблица результатов
        results_frame = ttk.Frame(self.dialog)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        columns = ("Маска", "Количество", "Примеры файлов")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
        
        # Настройка заголовков
        self.results_tree.heading("Маска", text="Маска")
        self.results_tree.heading("Количество", text="Найдено")
        self.results_tree.heading("Примеры файлов", text="Примеры файлов")
        
        # Настройка ширины столбцов
        self.results_tree.column("Маска", width=100, minwidth=80)
        self.results_tree.column("Количество", width=100, minwidth=80)
        self.results_tree.column("Примеры файлов", width=500, minwidth=300)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Контекстное меню
        self.context_menu = tk.Menu(self.dialog, tearoff=0)
        self.context_menu.add_command(label="Открыть файл", command=self.open_selected_file)
        self.context_menu.add_command(label="Открыть папку", command=self.open_file_folder)
        self.context_menu.add_command(label="Копировать путь", command=self.copy_file_path)
        
        self.results_tree.bind("<Button-3>", self.show_context_menu)
        self.results_tree.bind("<Double-1>", self.open_selected_file)
        
        # Кнопки
        buttons_frame = ttk.Frame(self.dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        ttk.Button(buttons_frame, text="Обновить", command=self.refresh_results).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Закрыть", command=self.dialog.destroy).pack(side=tk.LEFT)
    
    def perform_search_and_display(self):
        """Выполнение поиска и отображение результатов"""
        self.info_label.config(text="Поиск...")
        self.dialog.update()
        
        try:
            # Очистить предыдущие результаты
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            total_found = 0
            search_results = {}
            
            # Поиск по каждой маске
            for pattern in self.main_app.auto_search_patterns:
                found_files = self.search_files_by_pattern(self.main_app.current_directory, pattern)
                search_results[pattern] = found_files
                total_found += len(found_files)
            
            # Отобразить результаты
            for pattern, files in search_results.items():
                if files:
                    # Показать первые 3 файла как примеры
                    examples = [os.path.basename(f) for f in files[:3]]
                    if len(files) > 3:
                        examples.append(f"... и ещё {len(files) - 3}")
                    examples_text = ", ".join(examples)
                else:
                    examples_text = "Не найдено"
                
                item_id = self.results_tree.insert("", tk.END, values=(
                    pattern,
                    str(len(files)),
                    examples_text
                ), tags=(pattern,))
                
                # Добавить каждый файл как дочерний элемент
                for file_path in files:
                    file_name = os.path.basename(file_path)
                    relative_path = os.path.relpath(file_path, self.main_app.current_directory)
                    self.results_tree.insert(item_id, tk.END, values=(
                        "",
                        "",
                        f"{file_name} ({relative_path})"
                    ), tags=(file_path,))
            
            # Обновить информацию
            self.info_label.config(text=f"Поиск в {self.main_app.current_directory} | Всего найдено: {total_found} файлов")
            
            # Сохранить результаты в основном приложении
            self.main_app.auto_search_results = search_results
            
        except Exception as e:
            self.info_label.config(text=f"Ошибка поиска: {str(e)}")
    
    def search_files_by_pattern(self, directory, pattern):
        """Поиск файлов по маске"""
        import fnmatch
        found_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                for filename in files:
                    if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                        found_files.append(os.path.join(root, filename))
        except (PermissionError, OSError):
            pass  # Игнорировать ошибки доступа
        
        return found_files
    
    def refresh_results(self):
        """Обновление результатов"""
        self.perform_search_and_display()
    
    def show_context_menu(self, event):
        """Показ контекстного меню"""
        selection = self.results_tree.selection()
        if selection:
            item = self.results_tree.item(selection[0])
            if item['tags'] and os.path.isfile(item['tags'][0]):
                try:
                    self.context_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    self.context_menu.grab_release()
    
    def open_selected_file(self, event=None):
        """Открыть выбранный файл"""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = self.results_tree.item(selection[0])
        if item['tags'] and os.path.isfile(item['tags'][0]):
            file_path = item['tags'][0]
            self.main_app.run_executable(file_path)
    
    def open_file_folder(self):
        """Открыть папку с файлом"""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = self.results_tree.item(selection[0])
        if item['tags'] and os.path.isfile(item['tags'][0]):
            file_path = item['tags'][0]
            folder_path = os.path.dirname(file_path)
            if os.path.exists(folder_path):
                os.startfile(folder_path)
    
    def copy_file_path(self):
        """Копировать путь к файлу"""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = self.results_tree.item(selection[0])
        if item['tags'] and os.path.isfile(item['tags'][0]):
            file_path = item['tags'][0]
            self.main_app.root.clipboard_clear()
            self.main_app.root.clipboard_append(file_path)
            messagebox.showinfo("Копирование", f"Путь скопирован:\n{file_path}")


class DatabaseInfoDialog:
    """Диалог подробной информации о базе данных"""
    def __init__(self, parent, main_app):
        self.main_app = main_app
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Информация о базе данных")
        self.dialog.geometry("700x500")
        self.dialog.resizable(True, True)
        
        # Сделать диалог модальным
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_interface()
        self.load_database_info()
        
        # Центрировать диалог
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_interface(self):
        # Заголовок
        title_label = ttk.Label(self.dialog, text="Информация о базе данных", font=('Arial', 12, 'bold'))
        title_label.pack(pady=(10, 5))
        
        # Основная информация
        info_frame = ttk.LabelFrame(self.dialog, text="Основная информация")
        info_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        info_grid = ttk.Frame(info_frame)
        info_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Размещение информации в сетке
        row = 0
        
        ttk.Label(info_grid, text="Файл БД:", font=('Arial', 9, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=2)
        self.db_file_label = ttk.Label(info_grid, text="")
        self.db_file_label.grid(row=row, column=1, sticky="w", pady=2)
        
        row += 1
        ttk.Label(info_grid, text="Размер:", font=('Arial', 9, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=2)
        self.db_size_label = ttk.Label(info_grid, text="")
        self.db_size_label.grid(row=row, column=1, sticky="w", pady=2)
        
        row += 1
        ttk.Label(info_grid, text="Всего записей:", font=('Arial', 9, 'bold')).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=2)
        self.total_records_label = ttk.Label(info_grid, text="")
        self.total_records_label.grid(row=row, column=1, sticky="w", pady=2)
        
        # Статистика по таблицам
        tables_frame = ttk.LabelFrame(self.dialog, text="Статистика по таблицам")
        tables_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Таблица со статистикой
        columns = ("Таблица", "Записей", "Описание")
        self.tables_tree = ttk.Treeview(tables_frame, columns=columns, show="headings", height=12)
        
        # Настройка заголовков
        self.tables_tree.heading("Таблица", text="Таблица")
        self.tables_tree.heading("Записей", text="Записей")
        self.tables_tree.heading("Описание", text="Описание")
        
        # Настройка ширины столбцов
        self.tables_tree.column("Таблица", width=150, minwidth=120)
        self.tables_tree.column("Записей", width=80, minwidth=60)
        self.tables_tree.column("Описание", width=350, minwidth=250)
        
        # Скроллбар
        tables_scrollbar = ttk.Scrollbar(tables_frame, orient="vertical", command=self.tables_tree.yview)
        self.tables_tree.configure(yscrollcommand=tables_scrollbar.set)
        
        self.tables_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        tables_scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
        # Кнопки
        buttons_frame = ttk.Frame(self.dialog)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        ttk.Button(buttons_frame, text="Обновить", command=self.refresh_info).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Оптимизировать БД", command=self.optimize_database).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Закрыть", command=self.dialog.destroy).pack(side=tk.LEFT)
    
    def load_database_info(self):
        """Загрузка информации о базе данных"""
        try:
            import sqlite3
            
            # Получаем путь к БД
            db_path = self.main_app.db_manager.db_path if hasattr(self.main_app.db_manager, 'db_path') else 'project_manager.db'
            
            # Основная информация
            self.db_file_label.config(text=os.path.abspath(db_path))
            
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                if size_bytes > 1024 * 1024:
                    size_str = f"{size_bytes / (1024 * 1024):.2f} МБ ({size_bytes:,} байт)"
                elif size_bytes > 1024:
                    size_str = f"{size_bytes / 1024:.2f} КБ ({size_bytes:,} байт)"
                else:
                    size_str = f"{size_bytes:,} байт"
                self.db_size_label.config(text=size_str)
            else:
                self.db_size_label.config(text="Файл не найден")
                return
            
            # Подключаемся к БД
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Очищаем таблицу
            for item in self.tables_tree.get_children():
                self.tables_tree.delete(item)
            
            # Получаем список всех таблиц
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = cursor.fetchall()
            
            total_records = 0
            table_descriptions = {
                'directory_history': 'История выбранных директорий',
                'commands': 'Сохраненные последовательности команд',
                'snapshots': 'Снапшоты проектов',
                'settings': 'Настройки приложения',
                'hotkeys': 'Горячие клавиши',
                'search_recipes': 'Рецепты поиска',
                'sqlite_sequence': 'Системная таблица SQLite'
            }
            
            for table in tables:
                table_name = table[0]
                
                # Получаем количество записей
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                total_records += count
                
                # Описание таблицы
                description = table_descriptions.get(table_name, 'Пользовательская таблица')
                
                # Добавляем в дерево
                self.tables_tree.insert("", tk.END, values=(table_name, f"{count:,}", description))
            
            # Обновляем общее количество записей
            self.total_records_label.config(text=f"{total_records:,}")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить информацию о БД:\n{str(e)}")
    
    def refresh_info(self):
        """Обновление информации"""
        self.load_database_info()
        messagebox.showinfo("Обновление", "Информация о базе данных обновлена")
    
    def optimize_database(self):
        """Оптимизация базы данных"""
        if messagebox.askyesno("Оптимизация БД", 
                              "Выполнить оптимизацию базы данных?\n\n" +
                              "Это может занять некоторое время, но улучшит производительность."):
            try:
                import sqlite3
                
                db_path = self.main_app.db_manager.db_path if hasattr(self.main_app.db_manager, 'db_path') else 'project_manager.db'
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Выполняем VACUUM для оптимизации
                cursor.execute("VACUUM;")
                
                # Анализируем статистику
                cursor.execute("ANALYZE;")
                
                conn.close()
                
                # Обновляем информацию
                self.load_database_info()
                self.main_app.update_database_status()
                
                messagebox.showinfo("Успех", "База данных успешно оптимизирована!")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка оптимизации БД:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FlutterProjectManager(root)
    root.mainloop()
