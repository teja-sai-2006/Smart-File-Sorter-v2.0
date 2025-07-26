import time
import threading
import os
from pathlib import Path

class DirectoryWatcher:
    def __init__(self, watch_directory, callback=None):
        self.watch_directory = watch_directory
        self.callback = callback
        self.watching = False
        self.watch_thread = None
        self.last_scan = {}
        
    def start_watching(self):
        """Start watching the directory for changes."""
        if self.watching:
            return False
        
        self.watching = True
        self.watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.watch_thread.start()
        return True
    
    def stop_watching(self):
        """Stop watching the directory."""
        self.watching = False
        if self.watch_thread:
            self.watch_thread.join(timeout=1)
    
    def _watch_loop(self):
        """Main watching loop."""
        while self.watching:
            try:
                current_files = self._scan_directory()
                changes = self._detect_changes(current_files)
                
                if changes and self.callback:
                    self.callback(changes)
                
                self.last_scan = current_files
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                print(f"Directory watcher error: {e}")
                time.sleep(5)  # Wait longer if there's an error
    
    def _scan_directory(self):
        """Scan directory and return file information."""
        files = {}
        if not os.path.exists(self.watch_directory):
            return files
        
        try:
            for root, dirs, filenames in os.walk(self.watch_directory):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    try:
                        stat = os.stat(file_path)
                        files[file_path] = {
                            'size': stat.st_size,
                            'modified': stat.st_mtime
                        }
                    except OSError:
                        continue
        except OSError as e:
            print(f"Error scanning directory: {e}")
        
        return files
    
    def _detect_changes(self, current_files):
        """Detect changes between current and last scan."""
        changes = {
            'added': [],
            'modified': [],
            'deleted': []
        }
        
        # Find added and modified files
        for file_path, file_info in current_files.items():
            if file_path not in self.last_scan:
                changes['added'].append(file_path)
            elif self.last_scan[file_path]['modified'] != file_info['modified']:
                changes['modified'].append(file_path)
        
        # Find deleted files
        for file_path in self.last_scan:
            if file_path not in current_files:
                changes['deleted'].append(file_path)
        
        return changes if any(changes.values()) else None

def start_watching(directory, callback=None):
    """Convenience function to start watching a directory."""
    watcher = DirectoryWatcher(directory, callback)
    return watcher.start_watching()