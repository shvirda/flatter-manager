import os
import difflib
import hashlib
from pathlib import Path

class ProjectAnalyzer:
    def __init__(self):
        pass
    
    def analyze_directory(self, directory_path, max_files=1000):
        """Analyze directory structure and return statistics"""
        stats = {
            'folders': 0,
            'files': 0,
            'lines': 0,
            'characters': 0,
            'file_tree': {},
            'truncated': False
        }
        
        processed_files = 0
        skip_extensions = {'.pyc', '.pyo', '.class', '.o', '.so', '.dll', '.exe', '.bin'}
        skip_folders = {'__pycache__', '.git', '.svn', 'node_modules', '.dart_tool', 'build'}
        
        for root, dirs, files in os.walk(directory_path):
            # Фильтрация папок
            dirs[:] = [d for d in dirs if d not in skip_folders]
            
            stats['folders'] += len(dirs)
            
            # Ограничение количества обрабатываемых файлов
            if processed_files >= max_files:
                stats['truncated'] = True
                break
            
            # Фильтрация файлов
            filtered_files = [f for f in files if not any(f.endswith(ext) for ext in skip_extensions)]
            stats['files'] += len(filtered_files)
            
            # Build file tree
            rel_root = os.path.relpath(root, directory_path)
            if rel_root == '.':
                rel_root = ''
            
            current_tree = stats['file_tree']
            if rel_root:
                current_path = directory_path
                for part in rel_root.split(os.sep):
                    current_path = os.path.join(current_path, part)
                    if part not in current_tree:
                        current_tree[part] = {
                            'type': 'folder', 
                            'children': {}, 
                            'path': current_path,  # Добавляем путь к папке
                            'stats': {'folders': 0, 'files': 0, 'lines': 0, 'characters': 0}
                        }
                    current_tree = current_tree[part]['children']
            
            # Add files to current tree level
            for file in filtered_files:
                if processed_files >= max_files:
                    stats['truncated'] = True
                    break
                    
                file_path = os.path.join(root, file)
                file_stats = self.analyze_file(file_path)
                
                current_tree[file] = {
                    'type': 'file',
                    'path': file_path,
                    'stats': file_stats
                }
                
                stats['lines'] += file_stats['lines']
                stats['characters'] += file_stats['characters']
                processed_files += 1
        
        return stats
    
    def analyze_file(self, file_path):
        """Analyze single file and return statistics"""
        stats = {'lines': 0, 'characters': 0, 'size': 0}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                stats['lines'] = len(content.splitlines())
                stats['characters'] = len(content)
                stats['size'] = os.path.getsize(file_path)
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")
        
        return stats
    
    def compare_projects(self, project1_path, project2_path):
        """Compare two projects and return differences"""
        project1_stats = self.analyze_directory(project1_path)
        project2_stats = self.analyze_directory(project2_path)
        
        comparison = {
            'project1': {
                'path': project1_path,
                'stats': project1_stats
            },
            'project2': {
                'path': project2_path,
                'stats': project2_stats
            },
            'differences': self.find_differences(project1_stats['file_tree'], project2_stats['file_tree'])
        }
        
        return comparison
    
    def find_differences(self, tree1, tree2):
        """Find differences between two file trees"""
        differences = {
            'added': [],
            'removed': [],
            'modified': [],
            'unchanged': []
        }
        
        all_items = set(tree1.keys()) | set(tree2.keys())
        
        for item in all_items:
            if item in tree1 and item in tree2:
                if tree1[item]['type'] == 'file' and tree2[item]['type'] == 'file':
                    # Compare file contents
                    if self.files_are_different(tree1[item]['path'], tree2[item]['path']):
                        differences['modified'].append({
                            'name': item,
                            'type': 'file',
                            'path1': tree1[item]['path'],
                            'path2': tree2[item]['path']
                        })
                    else:
                        differences['unchanged'].append({
                            'name': item,
                            'type': 'file',
                            'path1': tree1[item]['path'],
                            'path2': tree2[item]['path']
                        })
                elif tree1[item]['type'] == 'folder' and tree2[item]['type'] == 'folder':
                    # Recursively compare folders
                    sub_differences = self.find_differences(tree1[item]['children'], tree2[item]['children'])
                    for key in sub_differences:
                        differences[key].extend([{**diff, 'parent': item} for diff in sub_differences[key]])
            elif item in tree1:
                differences['removed'].append({
                    'name': item,
                    'type': tree1[item]['type'],
                    'path': tree1[item].get('path', '')
                })
            else:
                differences['added'].append({
                    'name': item,
                    'type': tree2[item]['type'],
                    'path': tree2[item].get('path', '')
                })
        
        return differences
    
    def files_are_different(self, file1_path, file2_path):
        """Check if two files are different"""
        try:
            with open(file1_path, 'rb') as f1, open(file2_path, 'rb') as f2:
                return hashlib.md5(f1.read()).hexdigest() != hashlib.md5(f2.read()).hexdigest()
        except Exception:
            return True
    
    def get_file_diff(self, file1_path, file2_path):
        """Get detailed diff between two files"""
        try:
            with open(file1_path, 'r', encoding='utf-8', errors='ignore') as f1:
                lines1 = f1.readlines()
            with open(file2_path, 'r', encoding='utf-8', errors='ignore') as f2:
                lines2 = f2.readlines()
            
            diff = list(difflib.unified_diff(lines1, lines2, 
                                          fromfile=file1_path, 
                                          tofile=file2_path, 
                                          lineterm=''))
            return diff
        except Exception as e:
            return [f"Error comparing files: {e}"]
    
    def analyze_changes(self, original_path, current_path):
        """Analyze what has changed in a project since original"""
        original_stats = self.analyze_directory(original_path) if os.path.exists(original_path) else None
        current_stats = self.analyze_directory(current_path)
        
        if not original_stats:
            return {
                'is_new_project': True,
                'current_stats': current_stats,
                'changes': None
            }
        
        changes = self.find_differences(original_stats['file_tree'], current_stats['file_tree'])
        
        return {
            'is_new_project': False,
            'original_stats': original_stats,
            'current_stats': current_stats,
            'changes': changes
        }
