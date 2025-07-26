import json
import os

def load_rules_from_json(rules_file=None):
    """Load custom rules from a JSON file."""
    if rules_file is None:
        rules_file = 'custom_rules.json'
    
    if not os.path.exists(rules_file):
        # Create default rules file
        default_rules = {
            ".pdf": "Documents",
            ".jpg": "Images",
            ".mp4": "Videos",
            ".mp3": "Audio",
            ".zip": "Archives",
            ".py": "Code Files"
        }
        save_rules_to_json(default_rules, rules_file)
        return default_rules
    
    try:
        with open(rules_file, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading rules: {e}")
        return {}

def save_rules_to_json(rules, rules_file='custom_rules.json'):
    """Save rules to a JSON file."""
    try:
        with open(rules_file, 'w') as file:
            json.dump(rules, file, indent=4)
        return True
    except IOError as e:
        print(f"Error saving rules: {e}")
        return False

def load_rules(rules_file):
    """Legacy function for compatibility."""
    return load_rules_from_json(rules_file)

def categorize_file(file_name, rules):
    """Categorize a file based on rules."""
    file_ext = os.path.splitext(file_name)[1].lower()
    
    # Check by extension first
    if file_ext in rules:
        return rules[file_ext]
    
    # Check by filename patterns
    for pattern, category in rules.items():
        if pattern.startswith('*') and file_name.lower().endswith(pattern[1:].lower()):
            return category
        elif file_name.lower().startswith(pattern.lower()):
            return category
    
    return "Uncategorized"

def manage_rules_ui():
    """Simple console-based rules management (can be expanded to GUI)."""
    print("=== Rules Management ===")
    rules = load_rules_from_json()
    
    print("Current Rules:")
    for pattern, category in rules.items():
        print(f"  {pattern} -> {category}")
    
    print("\nOptions:")
    print("1. Add new rule")
    print("2. Remove rule")
    print("3. Save and exit")
    
    choice = input("Enter choice (1-3): ")
    
    if choice == '1':
        pattern = input("Enter file pattern (e.g., .txt or filename*): ")
        category = input("Enter category: ")
        rules[pattern] = category
        save_rules_to_json(rules)
        print(f"Added rule: {pattern} -> {category}")
    
    elif choice == '2':
        pattern = input("Enter pattern to remove: ")
        if pattern in rules:
            del rules[pattern]
            save_rules_to_json(rules)
            print(f"Removed rule for {pattern}")
        else:
            print("Pattern not found")
    
    return rules