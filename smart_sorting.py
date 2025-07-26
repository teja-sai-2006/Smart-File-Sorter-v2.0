import os
import re
from pathlib import Path

def smart_categorize(file_path):
    """Smart categorization using file content analysis and naming patterns."""
    filename = os.path.basename(file_path)
    file_ext = Path(filename).suffix.lower()
    
    # Analyze filename patterns
    filename_lower = filename.lower()
    
    # Project files
    if any(pattern in filename_lower for pattern in ['project', 'assignment', 'homework', 'thesis']):
        return "Projects"
    
    # Screenshots
    if any(pattern in filename_lower for pattern in ['screenshot', 'screen shot', 'capture']):
        return "Screenshots"
    
    # Downloads
    if any(pattern in filename_lower for pattern in ['download', 'temp', 'tmp']):
        return "Downloads"
    
    # Work documents
    if any(pattern in filename_lower for pattern in ['resume', 'cv', 'invoice', 'contract', 'report']):
        return "Work Documents"
    
    # Personal
    if any(pattern in filename_lower for pattern in ['personal', 'family', 'vacation', 'trip']):
        return "Personal"
    
    # Date-based categorization
    date_pattern = r'\d{4}[-_]\d{2}[-_]\d{2}'
    if re.search(date_pattern, filename):
        return "Dated Files"
    
    # Size-based categorization for media
    try:
        file_size = os.path.getsize(file_path)
        if file_ext in ['.jpg', '.png', '.gif'] and file_size > 5 * 1024 * 1024:  # > 5MB
            return "High Quality Images"
        elif file_ext in ['.mp4', '.avi', '.mkv'] and file_size > 100 * 1024 * 1024:  # > 100MB
            return "HD Videos"
    except OSError:
        pass
    
    # Default to basic categorization
    return categorize_by_extension(file_ext)

def categorize_by_extension(file_ext):
    """Basic categorization by file extension."""
    categories = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp'],
        'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        'code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.c', '.h', '.json', '.xml']
    }
    
    for category, extensions in categories.items():
        if file_ext in extensions:
            return category.title()
    
    return "Other"

def analyze_file_content(file_path):
    """Analyze file content for better categorization (placeholder for future ML integration)."""
    # This could be expanded to use machine learning models
    # to analyze file content, image recognition, document classification, etc.
    return None