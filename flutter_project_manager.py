import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import subprocess
import webbrowser
from database_manager import DatabaseManager
from project_analyzer import ProjectAnalyzer
from snapshot_manager import SnapshotManager

class FlutterProjectManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Flutter Project Manager - Полная версия")
        self.root.geometry("1200x800")
        
        # Initialize managers
        self.db_manager = DatabaseManager()
        self.analyzer = ProjectAnalyzer()
        self.snapshot_manager = SnapshotManager(self.db_manager)
        
        # Variables
        self.current_directory = None
        self.project_mode = tk.StringVar(value="new")
        
        self.create_main_interface()
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
        file_menu.add_command(label="Настройки редакторов", command=self.configure_editors)
        file_menu.add_separator()
        file_menu.add_command(label="Резервное копирование", command=self.backup_settings)
        file_menu.add_command(label="Выход", command=self.root.quit)
        
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
        
        # Кнопки действий
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, text="Выполнить действие", command=self.execute_main_action).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Создать снапшот", command=self.create_snapshot_dialog).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="Анализ изменений", command=self.analyze_changes).pack(side=tk.LEFT)

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
        
        # Контекстное меню для файлов
        self.file_context_menu = tk.Menu(self.root, tearoff=0)
        self.file_context_menu.add_command(label="Открыть в редакторе", command=self.open_in_editor)
        self.file_context_menu.add_command(label="Показать изменения", command=self.show_file_diff)
        self.file_context_menu.add_command(label="Копировать файл", command=self.copy_file)
        self.file_context_menu.add_command(label="Переименовать", command=self.rename_file)
        
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

    def refresh_project_files(self):
        """Обновление списка файлов проекта"""
        if not self.current_directory:
            return
        
        # Очистка дерева
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)
        
        # Анализ директории
        stats = self.analyzer.analyze_directory(self.current_directory)
        
        # Заполнение дерева
        self.populate_tree(self.project_tree, "", stats['file_tree'])

    def populate_tree(self, tree, parent, file_tree):
        """Заполнение дерева файлами"""
        for name, item in file_tree.items():
            if item['type'] == 'folder':
                folder_id = tree.insert(parent, tk.END, text=name, values=('folder', '', '', ''))
                self.populate_tree(tree, folder_id, item['children'])
            else:
                stats = item['stats']
                tree.insert(parent, tk.END, text=name, 
                          values=('file', f"{stats['size']} б", stats['lines'], stats['characters']),
                          tags=(item['path'],))

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
                try:
                    os.startfile(file_path)  # Windows
                except:
                    subprocess.run(['xdg-open', file_path])  # Linux

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

    # Заглушки для остальных методов
    def configure_editors(self):
        messagebox.showinfo("Настройки", "Функция настройки редакторов будет реализована")
    
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


if __name__ == "__main__":
    root = tk.Tk()
    app = FlutterProjectManager(root)
    root.mainloop()
