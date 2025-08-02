#!/usr/bin/env python3
"""
Console Manager for Flutter Project Manager
Provides console-based interface for all operations
"""

import sys
import os
import argparse
from database_manager import DatabaseManager
from project_analyzer import ProjectAnalyzer
from snapshot_manager import SnapshotManager

class ConsoleManager:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.analyzer = ProjectAnalyzer()
        self.snapshot_manager = SnapshotManager(self.db_manager)
    
    def create_flutter_project(self, project_path, project_name):
        """Create a minimal Flutter project"""
        project_dir = os.path.join(project_path, project_name)
        
        if os.path.exists(project_dir):
            response = input(f"Project {project_name} already exists. Continue? (y/n): ")
            if response.lower() != 'y':
                return False
        else:
            os.makedirs(project_dir)
        
        # Create directory structure
        os.makedirs(os.path.join(project_dir, 'lib'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'test'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'android'), exist_ok=True)
        os.makedirs(os.path.join(project_dir, 'ios'), exist_ok=True)
        
        # Create basic files
        self.create_file(os.path.join(project_dir, 'pubspec.yaml'), self.get_pubspec_template(project_name))
        self.create_file(os.path.join(project_dir, 'lib', 'main.dart'), self.get_main_dart_template())
        self.create_file(os.path.join(project_dir, 'README.md'), f"# {project_name}\n\nA Flutter project created by Flutter Project Manager.")
        self.create_file(os.path.join(project_dir, '.gitignore'), self.get_gitignore_template())
        
        print(f"✓ Flutter project '{project_name}' created successfully at {project_dir}")
        return True
    
    def create_file(self, file_path, content):
        """Create file with content"""
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

    def analyze_project(self, project_path):
        """Analyze project and display statistics"""
        if not os.path.exists(project_path):
            print(f"❌ Error: Directory {project_path} does not exist")
            return False
        
        print(f"📊 Analyzing project: {project_path}")
        stats = self.analyzer.analyze_directory(project_path)
        
        print("\n📈 Project Statistics:")
        print(f"   Folders: {stats['folders']}")
        print(f"   Files: {stats['files']}")
        print(f"   Lines of code: {stats['lines']}")
        print(f"   Characters: {stats['characters']}")
        
        print("\n📁 Project Structure:")
        self.print_tree(stats['file_tree'])
        
        return True
    
    def print_tree(self, tree, indent=0):
        """Print file tree structure"""
        for name, item in tree.items():
            prefix = "  " * indent + "├── "
            if item['type'] == 'folder':
                print(f"{prefix}{name}/")
                self.print_tree(item['children'], indent + 1)
            else:
                stats = item['stats']
                print(f"{prefix}{name} ({stats['lines']} lines, {stats['characters']} chars)")
    
    def create_snapshot(self, source_path):
        """Create snapshot of directory"""
        if not os.path.exists(source_path):
            print(f"❌ Error: Directory {source_path} does not exist")
            return False
        
        name = input("Enter snapshot name: ").strip()
        if not name:
            print("❌ Error: Snapshot name cannot be empty")
            return False
        
        description = input("Enter description (optional): ").strip()
        
        compress_input = input("Compress snapshot? (y/n, default: y): ").strip().lower()
        compress = compress_input != 'n'
        
        print(f"🔄 Creating snapshot '{name}'...")
        result = self.snapshot_manager.create_snapshot(source_path, name, description, compress)
        
        if result:
            print(f"✓ Snapshot created successfully: {result}")
            return True
        else:
            print("❌ Error creating snapshot")
            return False
    
    def list_snapshots(self):
        """List all available snapshots"""
        snapshots = self.snapshot_manager.list_snapshots()
        
        if not snapshots:
            print("📦 No snapshots found")
            return
        
        print("📦 Available Snapshots:")
        print("=" * 80)
        
        for i, snap in enumerate(snapshots, 1):
            compressed_text = "✓" if snap['compressed'] else "✗"
            print(f"{i:2d}. {snap['name']}")
            print(f"    Description: {snap['description'] or 'No description'}")
            print(f"    Created: {snap['created_date']}")
            print(f"    Compressed: {compressed_text}")
            print(f"    Path: {snap['directory_path']}")
            print("-" * 40)
    
    def restore_snapshot(self):
        """Restore snapshot to directory"""
        snapshots = self.snapshot_manager.list_snapshots()
        
        if not snapshots:
            print("📦 No snapshots available")
            return False
        
        self.list_snapshots()
        
        try:
            choice = int(input("Enter snapshot number to restore: ")) - 1
            if choice < 0 or choice >= len(snapshots):
                print("❌ Invalid snapshot number")
                return False
        except ValueError:
            print("❌ Invalid input")
            return False
        
        snapshot = snapshots[choice]
        destination = input("Enter destination directory: ").strip()
        
        if not destination:
            print("❌ Destination directory cannot be empty")
            return False
        
        print(f"🔄 Restoring snapshot '{snapshot['name']}' to {destination}...")
        success = self.snapshot_manager.restore_snapshot(
            snapshot['directory_path'], 
            destination, 
            snapshot['compressed']
        )
        
        if success:
            print(f"✓ Snapshot restored successfully to {destination}")
            return True
        else:
            print("❌ Error restoring snapshot")
            return False
    
    def compare_projects(self):
        """Compare two projects"""
        project1 = input("Enter first project path: ").strip()
        project2 = input("Enter second project path: ").strip()
        
        if not os.path.exists(project1):
            print(f"❌ Error: First project path {project1} does not exist")
            return False
        
        if not os.path.exists(project2):
            print(f"❌ Error: Second project path {project2} does not exist")
            return False
        
        print(f"🔍 Comparing projects...")
        print(f"   Project 1: {project1}")
        print(f"   Project 2: {project2}")
        
        comparison = self.analyzer.compare_projects(project1, project2)
        
        print("\n📊 Comparison Results:")
        print("=" * 60)
        
        stats1 = comparison['project1']['stats']
        stats2 = comparison['project2']['stats']
        
        print("Project 1 Statistics:")
        print(f"   Folders: {stats1['folders']}")
        print(f"   Files: {stats1['files']}")
        print(f"   Lines: {stats1['lines']}")
        print(f"   Characters: {stats1['characters']}")
        print()
        
        print("Project 2 Statistics:")
        print(f"   Folders: {stats2['folders']}")
        print(f"   Files: {stats2['files']}")
        print(f"   Lines: {stats2['lines']}")
        print(f"   Characters: {stats2['characters']}")
        print()
        
        differences = comparison['differences']
        
        if differences['added']:
            print(f"➕ Added files ({len(differences['added'])}):")
            for item in differences['added'][:10]:  # Show first 10
                print(f"   + {item['name']} ({item['type']})")
            if len(differences['added']) > 10:
                print(f"   ... and {len(differences['added']) - 10} more")
            print()
        
        if differences['removed']:
            print(f"➖ Removed files ({len(differences['removed'])}):")
            for item in differences['removed'][:10]:  # Show first 10
                print(f"   - {item['name']} ({item['type']})")
            if len(differences['removed']) > 10:
                print(f"   ... and {len(differences['removed']) - 10} more")
            print()
        
        if differences['modified']:
            print(f"✏️  Modified files ({len(differences['modified'])}):")
            for item in differences['modified'][:10]:  # Show first 10
                print(f"   ~ {item['name']}")
            if len(differences['modified']) > 10:
                print(f"   ... and {len(differences['modified']) - 10} more")
            print()
        
        return True
    
    def execute_commands(self):
        """Execute saved command sequences"""
        commands = self.db_manager.get_commands()
        
        if not commands:
            print("📋 No saved command sequences found")
            return False
        
        print("📋 Available Command Sequences:")
        print("=" * 50)
        
        for i, cmd in enumerate(commands, 1):
            print(f"{i:2d}. {cmd['name']}")
            print(f"    Description: {cmd['description'] or 'No description'}")
            print(f"    Commands: {len(cmd['command_sequence'])} commands")
            print("-" * 30)
        
        try:
            choice = int(input("Enter command sequence number to execute (0 to cancel): "))
            if choice == 0:
                return False
            if choice < 1 or choice > len(commands):
                print("❌ Invalid command sequence number")
                return False
        except ValueError:
            print("❌ Invalid input")
            return False
        
        cmd_sequence = commands[choice - 1]
        working_dir = input("Enter working directory (default: current): ").strip()
        if not working_dir:
            working_dir = os.getcwd()
        
        print(f"🔄 Executing command sequence '{cmd_sequence['name']}'...")
        print(f"   Working directory: {working_dir}")
        
        import subprocess
        
        for i, cmd in enumerate(cmd_sequence['command_sequence'], 1):
            print(f"   [{i}/{len(cmd_sequence['command_sequence'])}] {cmd}")
            try:
                result = subprocess.run(cmd, shell=True, cwd=working_dir, 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"❌ Command failed: {cmd}")
                    print(f"   Error: {result.stderr}")
                    return False
                elif result.stdout:
                    print(f"   Output: {result.stdout.strip()}")
            except Exception as e:
                print(f"❌ Error executing command: {cmd}")
                print(f"   Error: {str(e)}")
                return False
        
        print("✓ All commands executed successfully")
        return True
    
    def backup_settings(self):
        """Backup application settings and data"""
        backup_dir = input("Enter backup directory path: ").strip()
        if not backup_dir:
            print("❌ Backup directory cannot be empty")
            return False
        
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"flutter_manager_backup_{timestamp}")
        
        try:
            os.makedirs(backup_path, exist_ok=True)
            
            # Copy database
            if os.path.exists(self.db_manager.db_path):
                shutil.copy2(self.db_manager.db_path, backup_path)
                print(f"✓ Database backed up")
            
            # Copy snapshots directory
            if os.path.exists('snapshots'):
                shutil.copytree('snapshots', os.path.join(backup_path, 'snapshots'))
                print(f"✓ Snapshots backed up")
            
            # Create backup info
            with open(os.path.join(backup_path, 'backup_info.txt'), 'w') as f:
                f.write(f"Flutter Project Manager Backup\n")
                f.write(f"Created: {datetime.now().isoformat()}\n")
                f.write(f"Database: {self.db_manager.db_path}\n")
            
            print(f"✓ Backup created successfully at: {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating backup: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Flutter Project Manager Console Interface')
    parser.add_argument('action', choices=[
        'create_project', 'analyze', 'create_snapshot', 'list_snapshots',
        'restore_snapshot', 'compare_projects', 'execute_commands', 'backup'
    ], help='Action to perform')
    parser.add_argument('--path', help='Path for operations')
    parser.add_argument('--name', help='Name for operations')
    
    if len(sys.argv) == 1:
        # Interactive mode
        console = ConsoleManager()
        
        print("Flutter Project Manager - Console Mode")
        print("=====================================")
        
        while True:
            print("\nAvailable actions:")
            print("1. Create Flutter project")
            print("2. Analyze project")
            print("3. Create snapshot")
            print("4. List snapshots")
            print("5. Restore snapshot")
            print("6. Compare projects")
            print("7. Execute commands")
            print("8. Backup settings")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-8): ").strip()
            
            if choice == '0':
                print("Goodbye!")
                break
            elif choice == '1':
                path = input("Enter project directory path: ").strip()
                name = input("Enter project name: ").strip()
                if path and name:
                    console.create_flutter_project(path, name)
            elif choice == '2':
                path = input("Enter project path to analyze: ").strip()
                if path:
                    console.analyze_project(path)
            elif choice == '3':
                path = input("Enter directory path to snapshot: ").strip()
                if path:
                    console.create_snapshot(path)
            elif choice == '4':
                console.list_snapshots()
            elif choice == '5':
                console.restore_snapshot()
            elif choice == '6':
                console.compare_projects()
            elif choice == '7':
                console.execute_commands()
            elif choice == '8':
                console.backup_settings()
            else:
                print("Invalid choice!")
            
            input("\nPress Enter to continue...")
        
        return
    
    args = parser.parse_args()
    console = ConsoleManager()
    
    if args.action == 'create_project':
        if not args.path or not args.name:
            print("❌ Error: --path and --name are required for create_project")
            sys.exit(1)
        console.create_flutter_project(args.path, args.name)
    
    elif args.action == 'analyze':
        if not args.path:
            print("❌ Error: --path is required for analyze")
            sys.exit(1)
        console.analyze_project(args.path)
    
    elif args.action == 'create_snapshot':
        if not args.path:
            print("❌ Error: --path is required for create_snapshot")
            sys.exit(1)
        console.create_snapshot(args.path)
    
    elif args.action == 'list_snapshots':
        console.list_snapshots()
    
    elif args.action == 'restore_snapshot':
        console.restore_snapshot()
    
    elif args.action == 'compare_projects':
        console.compare_projects()
    
    elif args.action == 'execute_commands':
        console.execute_commands()
    
    elif args.action == 'backup':
        console.backup_settings()

if __name__ == '__main__':
    main()
