import os
import re
import fnmatch
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta

class SearchManager:
    def __init__(self):
        self.search_results = []
        self.search_cancelled = False
        
    def search_files(self, directories, filename_pattern="*", text_pattern="", 
                    file_extensions=None, exclude_dirs=None, 
                    modified_after=None, modified_before=None,
                    size_min=None, size_max=None, case_sensitive=False,
                    use_regex=False, progress_callback=None):
        """
        Массовый поиск файлов и текста
        """
        self.search_results = []
        self.search_cancelled = False
        
        if exclude_dirs is None:
            exclude_dirs = {'.git', '__pycache__', 'node_modules', '.dart_tool', 'build'}
        
        total_files = 0
        processed_files = 0
        
        # Подсчет общего количества файлов для прогресса
        for directory in directories:
            if not os.path.exists(directory):
                continue
            for root, dirs, files in os.walk(directory):
                # Исключение директорий
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                total_files += len(files)
        
        # Поиск файлов
        for directory in directories:
            if not os.path.exists(directory):
                continue
                
            for root, dirs, files in os.walk(directory):
                if self.search_cancelled:
                    break
                    
                # Исключение директорий
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    if self.search_cancelled:
                        break
                    
                    processed_files += 1
                    
                    # Обновление прогресса
                    if progress_callback and processed_files % 50 == 0:
                        progress = (processed_files / total_files) * 100 if total_files > 0 else 0
                        progress_callback(progress, f"Обработано файлов: {processed_files}/{total_files}")
                    
                    file_path = os.path.join(root, file)
                    
                    # Фильтр по имени файла
                    if not fnmatch.fnmatch(file, filename_pattern):
                        continue
                    
                    # Фильтр по расширению
                    if file_extensions:
                        _, ext = os.path.splitext(file)
                        if ext.lower() not in [e.lower() for e in file_extensions]:
                            continue
                    
                    try:
                        stat = os.stat(file_path)
                        
                        # Фильтр по дате модификации
                        if modified_after and datetime.fromtimestamp(stat.st_mtime) < modified_after:
                            continue
                        if modified_before and datetime.fromtimestamp(stat.st_mtime) > modified_before:
                            continue
                        
                        # Фильтр по размеру файла
                        if size_min and stat.st_size < size_min:
                            continue
                        if size_max and stat.st_size > size_max:
                            continue
                        
                        # Поиск текста в файле
                        text_matches = []
                        if text_pattern:
                            matches = self.search_text_in_file(file_path, text_pattern, 
                                                             case_sensitive, use_regex)
                            if matches:
                                text_matches = matches
                            else:
                                continue  # Текст не найден, пропускаем файл
                        
                        # Добавление результата
                        result = {
                            'path': file_path,
                            'name': file,
                            'directory': root,
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime),
                            'text_matches': text_matches
                        }
                        self.search_results.append(result)
                        
                    except (OSError, PermissionError) as e:
                        continue
        
        if progress_callback:
            progress_callback(100, f"Поиск завершен. Найдено файлов: {len(self.search_results)}")
        
        return self.search_results
    
    def search_text_in_file(self, file_path, pattern, case_sensitive=False, use_regex=False):
        """Поиск текста в файле"""
        matches = []
        
        try:
            # Определение кодировки
            encodings = ['utf-8', 'cp1251', 'latin1']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                return matches
            
            lines = content.split('\n')
            
            if use_regex:
                flags = 0 if case_sensitive else re.IGNORECASE
                try:
                    regex = re.compile(pattern, flags)
                except re.error:
                    return matches
                
                for line_num, line in enumerate(lines, 1):
                    for match in regex.finditer(line):
                        matches.append({
                            'line_number': line_num,
                            'line_text': line.strip(),
                            'match_start': match.start(),
                            'match_end': match.end(),
                            'match_text': match.group()
                        })
            else:
                search_pattern = pattern if case_sensitive else pattern.lower()
                
                for line_num, line in enumerate(lines, 1):
                    search_line = line if case_sensitive else line.lower()
                    if search_pattern in search_line:
                        matches.append({
                            'line_number': line_num,
                            'line_text': line.strip(),
                            'match_start': search_line.find(search_pattern),
                            'match_end': search_line.find(search_pattern) + len(search_pattern),
                            'match_text': pattern
                        })
        
        except Exception as e:
            pass
        
        return matches
    
    def cancel_search(self):
        """Отмена поиска"""
        self.search_cancelled = True
    
    def format_file_size(self, size_bytes):
        """Форматирование размера файла"""
        if size_bytes < 1024:
            return f"{size_bytes} Б"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} КБ"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} МБ"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} ГБ"


class SearchDialog:
    def __init__(self, parent, search_manager, settings_manager):
        self.parent = parent
        self.search_manager = search_manager
        self.settings_manager = settings_manager
        self.search_thread = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Поиск файлов и текста")
        self.dialog.geometry("900x700")
        self.dialog.resizable(True, True)
        
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
        # Создание notebook для вкладок
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка настроек поиска
        search_frame = ttk.Frame(notebook)
        notebook.add(search_frame, text="Параметры поиска")
        
        # Вкладка результатов
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Результаты")
        
        self.create_search_tab(search_frame)
        self.create_results_tab(results_frame)
    
    def create_search_tab(self, parent):
        # Основной фрейм с прокруткой
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Директории для поиска
        dirs_frame = ttk.LabelFrame(scrollable_frame, text="Директории для поиска")
        dirs_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.directories_listbox = tk.Listbox(dirs_frame, height=4)
        self.directories_listbox.pack(fill=tk.X, padx=5, pady=5)
        
        dirs_buttons_frame = ttk.Frame(dirs_frame)
        dirs_buttons_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Button(dirs_buttons_frame, text="Добавить", command=self.add_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(dirs_buttons_frame, text="Удалить", command=self.remove_directory).pack(side=tk.LEFT)
        
        # Фильтры файлов
        files_frame = ttk.LabelFrame(scrollable_frame, text="Фильтры файлов")
        files_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Имя файла
        ttk.Label(files_frame, text="Шаблон имени файла:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.filename_pattern = tk.StringVar(value="*")
        ttk.Entry(files_frame, textvariable=self.filename_pattern, width=30).grid(row=0, column=1, padx=5, pady=2)
        
        # Расширения файлов
        ttk.Label(files_frame, text="Расширения (через запятую):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.extensions_var = tk.StringVar()
        ttk.Entry(files_frame, textvariable=self.extensions_var, width=30).grid(row=1, column=1, padx=5, pady=2)
        
        # Размер файла
        size_frame = ttk.Frame(files_frame)
        size_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        
        ttk.Label(size_frame, text="Размер от:").pack(side=tk.LEFT)
        self.size_min_var = tk.StringVar()
        ttk.Entry(size_frame, textvariable=self.size_min_var, width=10).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(size_frame, text="до:").pack(side=tk.LEFT)
        self.size_max_var = tk.StringVar()
        ttk.Entry(size_frame, textvariable=self.size_max_var, width=10).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(size_frame, text="байт").pack(side=tk.LEFT, padx=(5, 0))
        
        # Дата модификации
        date_frame = ttk.Frame(files_frame)
        date_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        
        ttk.Label(date_frame, text="Изменен после:").pack(side=tk.LEFT)
        self.date_after_var = tk.StringVar()
        ttk.Entry(date_frame, textvariable=self.date_after_var, width=12).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(date_frame, text="до:").pack(side=tk.LEFT)
        self.date_before_var = tk.StringVar()
        ttk.Entry(date_frame, textvariable=self.date_before_var, width=12).pack(side=tk.LEFT, padx=(5, 2))
        ttk.Label(date_frame, text="(дд.мм.гггг)").pack(side=tk.LEFT, padx=(5, 0))
        
        # Поиск текста
        text_frame = ttk.LabelFrame(scrollable_frame, text="Поиск текста в файлах")
        text_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(text_frame, text="Искомый текст:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.text_pattern = tk.StringVar()
        text_entry = ttk.Entry(text_frame, textvariable=self.text_pattern, width=40)
        text_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=2, sticky="ew")
        
        # Опции поиска текста
        options_frame = ttk.Frame(text_frame)
        options_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=2)
        
        self.case_sensitive = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Учитывать регистр", variable=self.case_sensitive).pack(side=tk.LEFT, padx=(0, 10))
        
        self.use_regex = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Регулярные выражения", variable=self.use_regex).pack(side=tk.LEFT)
        
        # Исключения
        exclude_frame = ttk.LabelFrame(scrollable_frame, text="Исключить директории")
        exclude_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.exclude_dirs = tk.StringVar(value=".git, __pycache__, node_modules, .dart_tool, build")
        ttk.Entry(exclude_frame, textvariable=self.exclude_dirs, width=60).pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопки управления
        buttons_frame = ttk.Frame(scrollable_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.search_button = ttk.Button(buttons_frame, text="🔍 Начать поиск", command=self.start_search)
        self.search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.cancel_button = ttk.Button(buttons_frame, text="❌ Отменить", command=self.cancel_search, state="disabled")
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(buttons_frame, text="💾 Сохранить результаты", command=self.save_results).pack(side=tk.RIGHT)
        
        # Прогресс-бар
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(scrollable_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        self.status_label = ttk.Label(scrollable_frame, text="Готов к поиску")
        self.status_label.pack(padx=10, pady=(0, 10))
        
        # Упаковка canvas и scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_results_tab(self, parent):
        # Дерево результатов
        columns = ("Имя", "Путь", "Размер", "Дата изменения", "Совпадения")
        self.results_tree = ttk.Treeview(parent, columns=columns, show="tree headings")
        
        # Настройка заголовков
        self.results_tree.heading("#0", text="Тип")
        for col in columns:
            self.results_tree.heading(col, text=col)
        
        # Настройка ширины столбцов
        self.results_tree.column("#0", width=50)
        self.results_tree.column("Имя", width=200)
        self.results_tree.column("Путь", width=350)
        self.results_tree.column("Размер", width=100)
        self.results_tree.column("Дата изменения", width=130)
        self.results_tree.column("Совпадения", width=100)
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Упаковка
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        # Контекстное меню
        self.context_menu = tk.Menu(self.dialog, tearoff=0)
        self.context_menu.add_command(label="Открыть файл", command=self.open_selected_file)
        self.context_menu.add_command(label="Открыть папку", command=self.open_file_folder)
        self.context_menu.add_command(label="Копировать путь", command=self.copy_file_path)
        
        self.results_tree.bind("<Button-3>", self.show_context_menu)
        self.results_tree.bind("<Double-1>", self.open_selected_file)
        
        # Статистика
        stats_frame = ttk.Frame(parent)
        stats_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, text="Результатов не найдено")
        self.stats_label.pack(side=tk.LEFT)
    
    def add_directory(self):
        """Добавление директории для поиска"""
        directory = filedialog.askdirectory(title="Выберите директорию для поиска")
        if directory:
            self.directories_listbox.insert(tk.END, directory)
    
    def remove_directory(self):
        """Удаление директории из списка"""
        selection = self.directories_listbox.curselection()
        if selection:
            self.directories_listbox.delete(selection[0])
    
    def start_search(self):
        """Начало поиска"""
        # Получение директорий
        directories = [self.directories_listbox.get(i) for i in range(self.directories_listbox.size())]
        if not directories:
            messagebox.showwarning("Предупреждение", "Выберите хотя бы одну директорию для поиска")
            return
        
        # Подготовка параметров
        filename_pattern = self.filename_pattern.get() or "*"
        text_pattern = self.text_pattern.get()
        
        # Расширения файлов
        extensions = None
        if self.extensions_var.get():
            extensions = [ext.strip() for ext in self.extensions_var.get().split(',')]
        
        # Размер файлов
        size_min = None
        size_max = None
        try:
            if self.size_min_var.get():
                size_min = int(self.size_min_var.get())
            if self.size_max_var.get():
                size_max = int(self.size_max_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный размер файла")
            return
        
        # Даты
        date_after = None
        date_before = None
        try:
            if self.date_after_var.get():
                date_after = datetime.strptime(self.date_after_var.get(), "%d.%m.%Y")
            if self.date_before_var.get():
                date_before = datetime.strptime(self.date_before_var.get(), "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный формат даты (дд.мм.гггг)")
            return
        
        # Исключения
        exclude_dirs = set()
        if self.exclude_dirs.get():
            exclude_dirs = {d.strip() for d in self.exclude_dirs.get().split(',')}
        
        # Включение режима поиска
        self.search_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        self.progress_var.set(0)
        
        # Очистка результатов
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Запуск поиска в отдельном потоке
        self.search_thread = threading.Thread(
            target=self._search_worker,
            args=(directories, filename_pattern, text_pattern, extensions,
                  exclude_dirs, date_after, date_before, size_min, size_max)
        )
        self.search_thread.daemon = True
        self.search_thread.start()
    
    def _search_worker(self, directories, filename_pattern, text_pattern, extensions,
                      exclude_dirs, date_after, date_before, size_min, size_max):
        """Рабочий поток поиска"""
        try:
            results = self.search_manager.search_files(
                directories=directories,
                filename_pattern=filename_pattern,
                text_pattern=text_pattern,
                file_extensions=extensions,
                exclude_dirs=exclude_dirs,
                modified_after=date_after,
                modified_before=date_before,
                size_min=size_min,
                size_max=size_max,
                case_sensitive=self.case_sensitive.get(),
                use_regex=self.use_regex.get(),
                progress_callback=self.update_progress
            )
            
            # Обновление результатов в главном потоке
            self.dialog.after(0, self.update_results, results)
            
        except Exception as e:
            self.dialog.after(0, self.search_error, str(e))
    
    def update_progress(self, progress, status):
        """Обновление прогресса поиска"""
        self.dialog.after(0, self._update_progress_ui, progress, status)
    
    def _update_progress_ui(self, progress, status):
        """Обновление UI прогресса"""
        self.progress_var.set(progress)
        self.status_label.config(text=status)
    
    def update_results(self, results):
        """Обновление результатов поиска"""
        # Группировка по директориям
        directories = {}
        
        for result in results:
            dir_path = result['directory']
            if dir_path not in directories:
                directories[dir_path] = []
            directories[dir_path].append(result)
        
        # Заполнение дерева
        for dir_path, files in directories.items():
            # Добавление директории
            dir_item = self.results_tree.insert("", tk.END, text="📁", values=(
                os.path.basename(dir_path) or dir_path,
                dir_path,
                f"{len(files)} файлов",
                "",
                ""
            ))
            
            # Добавление файлов
            for file_result in files:
                match_count = len(file_result['text_matches'])
                match_text = f"{match_count} совпадений" if match_count > 0 else ""
                
                file_item = self.results_tree.insert(dir_item, tk.END, text="📄", values=(
                    file_result['name'],
                    file_result['path'],
                    self.search_manager.format_file_size(file_result['size']),
                    file_result['modified'].strftime("%d.%m.%Y %H:%M"),
                    match_text
                ))
                
                # Добавление совпадений текста
                for match in file_result['text_matches']:
                    self.results_tree.insert(file_item, tk.END, text="🔍", values=(
                        f"Строка {match['line_number']}",
                        match['line_text'][:100] + "..." if len(match['line_text']) > 100 else match['line_text'],
                        "",
                        "",
                        match['match_text']
                    ))
        
        # Обновление статистики
        total_files = len(results)
        total_matches = sum(len(r['text_matches']) for r in results)
        
        stats_text = f"Найдено файлов: {total_files}"
        if total_matches > 0:
            stats_text += f", текстовых совпадений: {total_matches}"
        
        self.stats_label.config(text=stats_text)
        
        # Восстановление кнопок
        self.search_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        
        # Разворачивание первых результатов
        for item in self.results_tree.get_children()[:5]:
            self.results_tree.item(item, open=True)
    
    def search_error(self, error_message):
        """Обработка ошибки поиска"""
        messagebox.showerror("Ошибка поиска", f"Произошла ошибка при поиске:\n{error_message}")
        self.search_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        self.status_label.config(text="Ошибка поиска")
    
    def cancel_search(self):
        """Отмена поиска"""
        self.search_manager.cancel_search()
        self.search_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        self.status_label.config(text="Поиск отменен")
    
    def show_context_menu(self, event):
        """Показ контекстного меню"""
        item = self.results_tree.selection()[0] if self.results_tree.selection() else None
        if item and self.results_tree.item(item, "text") == "📄":
            self.context_menu.post(event.x_root, event.y_root)
    
    def open_selected_file(self, event=None):
        """Открытие выбранного файла"""
        item = self.results_tree.selection()[0] if self.results_tree.selection() else None
        if item and self.results_tree.item(item, "text") == "📄":
            file_path = self.results_tree.item(item, "values")[1]
            self.settings_manager.open_file_with_editor(file_path)
    
    def open_file_folder(self):
        """Открытие папки с файлом"""
        item = self.results_tree.selection()[0] if self.results_tree.selection() else None
        if item and self.results_tree.item(item, "text") == "📄":
            file_path = self.results_tree.item(item, "values")[1]
            folder_path = os.path.dirname(file_path)
            os.startfile(folder_path)
    
    def copy_file_path(self):
        """Копирование пути к файлу"""
        item = self.results_tree.selection()[0] if self.results_tree.selection() else None
        if item and self.results_tree.item(item, "text") == "📄":
            file_path = self.results_tree.item(item, "values")[1]
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(file_path)
            messagebox.showinfo("Скопировано", "Путь к файлу скопирован в буфер обмена")
    
    def save_results(self):
        """Сохранение результатов поиска"""
        if not hasattr(self.search_manager, 'search_results') or not self.search_manager.search_results:
            messagebox.showwarning("Предупреждение", "Нет результатов для сохранения")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить результаты поиска",
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("CSV файлы", "*.csv"), ("Все файлы", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("Результаты поиска файлов\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for result in self.search_manager.search_results:
                        f.write(f"Файл: {result['name']}\n")
                        f.write(f"Путь: {result['path']}\n")
                        f.write(f"Размер: {self.search_manager.format_file_size(result['size'])}\n")
                        f.write(f"Изменен: {result['modified'].strftime('%d.%m.%Y %H:%M')}\n")
                        
                        if result['text_matches']:
                            f.write("Текстовые совпадения:\n")
                            for match in result['text_matches']:
                                f.write(f"  Строка {match['line_number']}: {match['line_text']}\n")
                        
                        f.write("\n" + "-" * 50 + "\n\n")
                
                messagebox.showinfo("Успех", f"Результаты сохранены в файл:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
