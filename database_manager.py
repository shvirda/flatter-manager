import sqlite3
import json
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='flutter_manager.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Commands table
        c.execute('''CREATE TABLE IF NOT EXISTS commands
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT UNIQUE,
                      description TEXT,
                      command_sequence TEXT,
                      created_date TEXT)''')
        
        # Snapshots table
        c.execute('''CREATE TABLE IF NOT EXISTS snapshots
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT UNIQUE,
                      description TEXT,
                      directory_path TEXT,
                      compressed INTEGER,
                      created_date TEXT)''')
        
        # Project presets table
        c.execute('''CREATE TABLE IF NOT EXISTS project_presets
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT UNIQUE,
                      description TEXT,
                      file_structure TEXT,
                      created_date TEXT)''')
        
        # Settings table
        c.execute('''CREATE TABLE IF NOT EXISTS settings
                     (key TEXT PRIMARY KEY,
                      value TEXT)''')
        
        # Directory history table
        c.execute('''CREATE TABLE IF NOT EXISTS directory_history
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      directory_path TEXT UNIQUE,
                      last_used TEXT,
                      usage_count INTEGER DEFAULT 1,
                      created_date TEXT)''')
        
        conn.commit()
        conn.close()
    
    def save_command(self, name, description, command_sequence):
        """Save command sequence to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("INSERT OR REPLACE INTO commands (name, description, command_sequence, created_date) VALUES (?, ?, ?, ?)",
                     (name, description, json.dumps(command_sequence), datetime.now().isoformat()))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving command: {e}")
            return False
        finally:
            conn.close()
    
    def get_commands(self):
        """Get all saved commands"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT * FROM commands")
        commands = c.fetchall()
        conn.close()
        
        return [{'id': cmd[0], 'name': cmd[1], 'description': cmd[2], 
                'command_sequence': json.loads(cmd[3]), 'created_date': cmd[4]} 
                for cmd in commands]
    
    def save_snapshot(self, name, description, directory_path, compressed=False):
        """Save snapshot information to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("INSERT OR REPLACE INTO snapshots (name, description, directory_path, compressed, created_date) VALUES (?, ?, ?, ?, ?)",
                     (name, description, directory_path, 1 if compressed else 0, datetime.now().isoformat()))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving snapshot: {e}")
            return False
        finally:
            conn.close()
    
    def get_snapshots(self):
        """Get all saved snapshots"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT * FROM snapshots")
        snapshots = c.fetchall()
        conn.close()
        
        return [{'id': snap[0], 'name': snap[1], 'description': snap[2], 
                'directory_path': snap[3], 'compressed': bool(snap[4]), 
                'created_date': snap[5]} for snap in snapshots]
    
    def save_preset(self, name, description, file_structure):
        """Save project preset to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("INSERT OR REPLACE INTO project_presets (name, description, file_structure, created_date) VALUES (?, ?, ?, ?)",
                     (name, description, json.dumps(file_structure), datetime.now().isoformat()))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving preset: {e}")
            return False
        finally:
            conn.close()
    
    def get_presets(self):
        """Get all saved presets"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT * FROM project_presets")
        presets = c.fetchall()
        conn.close()
        
        return [{'id': preset[0], 'name': preset[1], 'description': preset[2], 
                'file_structure': json.loads(preset[3]), 'created_date': preset[4]} 
                for preset in presets]
    
    def save_setting(self, key, value):
        """Save setting to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                     (key, json.dumps(value)))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving setting: {e}")
            return False
        finally:
            conn.close()
    
    def get_setting(self, key, default=None):
        """Get setting from database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = c.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return default
    
    def add_directory_to_history(self, directory_path):
        """Add directory to history or update if exists"""
        if not os.path.exists(directory_path):
            return False
            
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        now = datetime.now().isoformat()
        
        try:
            # Check if directory already exists
            c.execute("SELECT id, usage_count FROM directory_history WHERE directory_path = ?", (directory_path,))
            existing = c.fetchone()
            
            if existing:
                # Update existing entry
                c.execute("UPDATE directory_history SET last_used = ?, usage_count = ? WHERE id = ?",
                         (now, existing[1] + 1, existing[0]))
            else:
                # Insert new entry
                c.execute("INSERT INTO directory_history (directory_path, last_used, usage_count, created_date) VALUES (?, ?, ?, ?)",
                         (directory_path, now, 1, now))
            
            # Keep only last 20 directories (remove oldest by last_used)
            c.execute("DELETE FROM directory_history WHERE id NOT IN (SELECT id FROM directory_history ORDER BY last_used DESC LIMIT 20)")
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding directory to history: {e}")
            return False
        finally:
            conn.close()
    
    def get_directory_history(self, limit=10):
        """Get directory history sorted by last used"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("SELECT * FROM directory_history ORDER BY last_used DESC LIMIT ?", (limit,))
            directories = c.fetchall()
            
            result = []
            for dir_info in directories:
                # Check if directory still exists
                if os.path.exists(dir_info[1]):
                    result.append({
                        'id': dir_info[0],
                        'directory_path': dir_info[1],
                        'last_used': dir_info[2],
                        'usage_count': dir_info[3],
                        'created_date': dir_info[4]
                    })
                else:
                    # Remove non-existent directory from history
                    c.execute("DELETE FROM directory_history WHERE id = ?", (dir_info[0],))
            
            conn.commit()
            return result
        except Exception as e:
            print(f"Error getting directory history: {e}")
            return []
        finally:
            conn.close()
    
    def remove_directory_from_history(self, directory_path):
        """Remove directory from history"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute("DELETE FROM directory_history WHERE directory_path = ?", (directory_path,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error removing directory from history: {e}")
            return False
        finally:
            conn.close()
