import os
import time
from pathlib import Path

def scan_files(source_path, recursive, filters):
    """Scan the source folder and apply filters, returning structured data.

    Args:
        source_path (str): Path to the source folder.
        recursive (bool): Whether to scan subfolders.
        filters (dict): Filters for date, size, and excluded extensions.

    Returns:
        list: List of dictionaries with file information (name, type, size, category, path).
    """
    valid_files = []
    excluded_extensions = filters.get('excluded_extensions', [])
    min_size = filters.get('min_size', 0)
    max_size = filters.get('max_size', float('inf'))
    cutoff_date = filters.get('cutoff_date', None)
    rules = filters.get('rules', {})

    for dirpath, dirnames, filenames in os.walk(source_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                file_size = os.path.getsize(file_path)
                file_mtime = os.path.getmtime(file_path)
                file_ext = Path(filename).suffix.lower()

                # Apply exclusion filter
                if any(filename.lower().endswith(ext.lower()) for ext in excluded_extensions):
                    continue

                # Apply size filter
                if not (min_size <= file_size <= max_size):
                    continue

                # Apply date filter (only if cutoff_date is provided)
                if cutoff_date and file_mtime > time.mktime(cutoff_date.timetuple()):
                    continue

                # Categorize file
                category = categorize_file(filename, file_ext, rules)

                # Create structured file data
                file_data = {
                    'name': filename,
                    'type': file_ext or 'No Extension',
                    'size': format_file_size(file_size),
                    'size_bytes': file_size,
                    'category': category,
                    'path': file_path,
                    'modified': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_mtime))
                }

                valid_files.append(file_data)

            except (OSError, IOError) as e:
                print(f"Error processing {file_path}: {e}")
                continue

        if not recursive:
            break

    return valid_files

def categorize_file(filename, file_ext, rules):
    """Categorize a file based on extension and custom rules."""
    # Check custom rules first
    for pattern, category in rules.items():
        if filename.lower().endswith(pattern.lower()) or file_ext.lower() == pattern.lower():
            return category
    
    # Default categorization
    image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp']
    video_exts = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v']
    audio_exts = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a']
    document_exts = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx']
    archive_exts = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']
    code_exts = ['.py', '.js', '.html', '.css', '.cpp', '.java', '.c', '.h']
    
    if file_ext.lower() in image_exts:
        return 'Images'
    elif file_ext.lower() in video_exts:
        return 'Videos'
    elif file_ext.lower() in audio_exts:
        return 'Audio'
    elif file_ext.lower() in document_exts:
        return 'Documents'
    elif file_ext.lower() in archive_exts:
        return 'Archives'
    elif file_ext.lower() in code_exts:
        return 'Code Files'
    else:
        return 'Other'

def format_file_size(size_bytes):
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"