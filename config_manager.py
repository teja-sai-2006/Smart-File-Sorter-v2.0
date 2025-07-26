import json
import os
import csv
from datetime import datetime

# Default configuration settings
DEFAULT_CONFIG = {
    "categories": ["Images", "Videos", "Documents", "Audio", "Archives", "Code Files", "Other"],
    "default_destination": os.path.expanduser("~/Documents/Sorted_Files"),
    "custom_rules": {},
    "excluded_extensions": [".tmp", ".log", ".cache"],
    "auto_watch": False,
    "ai_sorting": False,
    "theme": "light"
}

CONFIG_FILE = "file_sorter_config.json"

def load_config():
    """Load configuration from file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as file:
                config = json.load(file)
                # Merge with defaults to ensure all keys exist
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG.copy()
    else:
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file, indent=4)
        return True
    except IOError as e:
        print(f"Error saving config: {e}")
        return False

def export_config(export_path=None):
    """Export current configuration to a file."""
    if export_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = f"config_backup_{timestamp}.json"
    
    config = load_config()
    try:
        with open(export_path, 'w') as file:
            json.dump(config, file, indent=4)
        return export_path
    except IOError as e:
        print(f"Error exporting config: {e}")
        return None

def import_config(import_path):
    """Import configuration from a file."""
    try:
        with open(import_path, 'r') as file:
            imported_config = json.load(file)
        
        # Validate imported config
        config = DEFAULT_CONFIG.copy()
        for key, value in imported_config.items():
            if key in DEFAULT_CONFIG:
                config[key] = value
        
        save_config(config)
        return config
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error importing config: {e}")
        return None

def export_report(preview_data, report_type='json', export_path=None):
    """Export sorting report in various formats."""
    if export_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = f"sort_report_{timestamp}.{report_type}"
    
    try:
        os.makedirs(os.path.dirname(export_path) if os.path.dirname(export_path) else '.', exist_ok=True)
        
        if report_type == 'json':
            with open(export_path, 'w') as file:
                json.dump(preview_data, file, indent=4)
        
        elif report_type == 'csv':
            with open(export_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['File Name', 'Type', 'Size', 'Category', 'Path', 'Modified'])
                
                for file_data in preview_data:
                    writer.writerow([
                        file_data.get('name', ''),
                        file_data.get('type', ''),
                        file_data.get('size', ''),
                        file_data.get('category', ''),
                        file_data.get('path', ''),
                        file_data.get('modified', '')
                    ])
        
        return export_path
    except IOError as e:
        print(f"Error exporting report: {e}")
        return None