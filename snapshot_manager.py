import os
import shutil
import zipfile
import tempfile
from datetime import datetime
from database_manager import DatabaseManager

class SnapshotManager:
    def __init__(self, db_manager=None):
        self.db_manager = db_manager or DatabaseManager()
        self.snapshots_dir = 'snapshots'
        if not os.path.exists(self.snapshots_dir):
            os.makedirs(self.snapshots_dir)
    
    def create_snapshot(self, source_path, name, description="", compress=True):
        """Create a snapshot of a directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_name = f"{name}_{timestamp}"
        
        if compress:
            snapshot_path = os.path.join(self.snapshots_dir, f"{snapshot_name}.zip")
            success = self._create_compressed_snapshot(source_path, snapshot_path)
        else:
            snapshot_path = os.path.join(self.snapshots_dir, snapshot_name)
            success = self._create_uncompressed_snapshot(source_path, snapshot_path)
        
        if success:
            # Save to database
            self.db_manager.save_snapshot(name, description, snapshot_path, compress)
            return snapshot_path
        return None
    
    def _create_compressed_snapshot(self, source_path, snapshot_path):
        """Create compressed snapshot using ZIP"""
        try:
            with zipfile.ZipFile(snapshot_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_path)
                        zipf.write(file_path, arcname)
            return True
        except Exception as e:
            print(f"Error creating compressed snapshot: {e}")
            return False
    
    def _create_uncompressed_snapshot(self, source_path, snapshot_path):
        """Create uncompressed snapshot by copying directory"""
        try:
            shutil.copytree(source_path, snapshot_path)
            return True
        except Exception as e:
            print(f"Error creating uncompressed snapshot: {e}")
            return False
    
    def restore_snapshot(self, snapshot_path, destination_path, compressed=True):
        """Restore snapshot to destination"""
        try:
            if compressed and snapshot_path.endswith('.zip'):
                with zipfile.ZipFile(snapshot_path, 'r') as zipf:
                    zipf.extractall(destination_path)
            else:
                shutil.copytree(snapshot_path, destination_path)
            return True
        except Exception as e:
            print(f"Error restoring snapshot: {e}")
            return False
    
    def list_snapshots(self):
        """List all available snapshots"""
        return self.db_manager.get_snapshots()
    
    def delete_snapshot(self, snapshot_id):
        """Delete a snapshot"""
        snapshots = self.db_manager.get_snapshots()
        snapshot = next((s for s in snapshots if s['id'] == snapshot_id), None)
        
        if snapshot:
            try:
                if os.path.exists(snapshot['directory_path']):
                    if snapshot['compressed']:
                        os.remove(snapshot['directory_path'])
                    else:
                        shutil.rmtree(snapshot['directory_path'])
                
                # Remove from database
                conn = sqlite3.connect(self.db_manager.db_path)
                c = conn.cursor()
                c.execute("DELETE FROM snapshots WHERE id = ?", (snapshot_id,))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Error deleting snapshot: {e}")
        return False
    
    def copy_snapshot_to_directory(self, snapshot_id, destination_base):
        """Copy snapshot to specified directory"""
        snapshots = self.db_manager.get_snapshots()
        snapshot = next((s for s in snapshots if s['id'] == snapshot_id), None)
        
        if snapshot:
            snapshot_path = snapshot['directory_path']
            dest_path = os.path.join(destination_base, f"snapshot_{snapshot['name']}")
            
            return self.restore_snapshot(snapshot_path, dest_path, snapshot['compressed'])
        return False
    
    def compare_with_snapshot(self, current_project_path, snapshot_id):
        """Compare current project with a snapshot"""
        from project_analyzer import ProjectAnalyzer
        
        snapshots = self.db_manager.get_snapshots()
        snapshot = next((s for s in snapshots if s['id'] == snapshot_id), None)
        
        if not snapshot:
            return None
        
        # Extract snapshot to temporary directory for comparison
        with tempfile.TemporaryDirectory() as temp_dir:
            if self.restore_snapshot(snapshot['directory_path'], temp_dir, snapshot['compressed']):
                analyzer = ProjectAnalyzer()
                return analyzer.compare_projects(temp_dir, current_project_path)
        
        return None
