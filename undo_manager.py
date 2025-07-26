import json
import os
import shutil
from datetime import datetime

UNDO_LOG_FILE = "undo_log.json"
MAX_UNDO_HISTORY = 5  # Keep track of the last 5 sort operations

def _load_undo_log():
    """Loads the undo history from the log file."""
    if os.path.exists(UNDO_LOG_FILE):
        with open(UNDO_LOG_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def _save_undo_log(log_entries):
    """Saves the undo history to the log file."""
    with open(UNDO_LOG_FILE, 'w') as f:
        json.dump(log_entries, f, indent=4)

def log_sort_operation(moved_files):
    """
    Logs a completed sort operation for potential undo.

    Args:
        moved_files (list): A list of dictionaries, where each dictionary
                            represents a moved file and contains:
                            - 'original_path': The file's path before moving.
                            - 'new_path': The file's path after moving.
                            - 'category': The category it was moved into (for context/deletion of empty dirs).
    """
    if not moved_files:
        return

    undo_log = _load_undo_log()

    # Add a timestamp to the operation
    operation_record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": moved_files
    }
    undo_log.append(operation_record)

    # Keep only the latest MAX_UNDO_HISTORY operations
    if len(undo_log) > MAX_UNDO_HISTORY:
        undo_log = undo_log[-MAX_UNDO_HISTORY:]

    _save_undo_log(undo_log)
    print(f"Logged sort operation with {len(moved_files)} files for undo.")

def undo_last_sort():
    """
    Undoes the last logged file sorting operation.

    Returns:
        tuple: (success, message) where success is a boolean and message is a string.
    """
    undo_log = _load_undo_log()

    if not undo_log:
        return False, "No previous sort operations to undo."

    last_operation = undo_log.pop()  # Get the last operation and remove it from history
    _save_undo_log(undo_log) # Save the updated log

    files_to_undo = last_operation.get("files", [])
    if not files_to_undo:
        return False, "The last operation record was empty."

    successful_undos = 0
    failed_undos = []

    for file_data in reversed(files_to_undo): # Undo in reverse order of moving
        original_path = file_data.get('original_path')
        new_path = file_data.get('new_path')

        if not original_path or not new_path:
            failed_undos.append(f"Invalid record for {file_data.get('new_path', 'unknown file')}")
            continue

        if not os.path.exists(new_path):
            failed_undos.append(f"File not found at new path: {new_path}")
            continue

        try:
            shutil.move(new_path, original_path)
            successful_undos += 1

            # Attempt to remove the now empty directory if it was created for the category
            # This is a bit more complex as the original category folder might contain other files
            # A safer approach is to only remove if it's truly empty AND was created by this sort.
            # For simplicity, we'll try to remove if it's empty after the move.
            category_folder = os.path.dirname(new_path)
            if os.path.exists(category_folder) and not os.listdir(category_folder):
                try:
                    os.rmdir(category_folder)
                    print(f"Removed empty category folder: {category_folder}")
                except OSError as e:
                    print(f"Could not remove empty directory {category_folder}: {e}")

        except Exception as e:
            failed_undos.append(f"Failed to move '{new_path}' back to '{original_path}': {e}")

    message = f"Successfully undid {successful_undos} file(s)."
    if failed_undos:
        message += "\nFailures:\n" + "\n".join(failed_undos)
        return False, message
    
    return True, message

# Example usage (for testing undo_manager.py independently)
if __name__ == "__main__":
    # Create some dummy files and folders for testing
    test_source_dir = "test_source"
    test_dest_dir = "test_destination"
    test_category_dir = os.path.join(test_dest_dir, "Images")

    os.makedirs(test_source_dir, exist_ok=True)
    os.makedirs(test_category_dir, exist_ok=True)

    with open(os.path.join(test_source_dir, "image1.jpg"), "w") as f:
        f.write("dummy image content")
    with open(os.path.join(test_source_dir, "doc1.pdf"), "w") as f:
        f.write("dummy doc content")

    print("--- Simulating a Sort Operation ---")
    simulated_moved_files = []
    
    # Simulate moving image1.jpg
    original_path_img1 = os.path.join(test_source_dir, "image1.jpg")
    new_path_img1 = os.path.join(test_category_dir, "image1.jpg")
    if os.path.exists(original_path_img1):
        shutil.move(original_path_img1, new_path_img1)
        simulated_moved_files.append({
            "original_path": original_path_img1,
            "new_path": new_path_img1,
            "category": "Images"
        })
        print(f"Simulated move: {original_path_img1} -> {new_path_img1}")

    # Simulate moving doc1.pdf to another category (create if needed)
    test_category_dir_docs = os.path.join(test_dest_dir, "Documents")
    os.makedirs(test_category_dir_docs, exist_ok=True)
    original_path_doc1 = os.path.join(test_source_dir, "doc1.pdf")
    new_path_doc1 = os.path.join(test_category_dir_docs, "doc1.pdf")
    if os.path.exists(original_path_doc1):
        shutil.move(original_path_doc1, new_path_doc1)
        simulated_moved_files.append({
            "original_path": original_path_doc1,
            "new_path": new_path_doc1,
            "category": "Documents"
        })
        print(f"Simulated move: {original_path_doc1} -> {new_path_doc1}")

    log_sort_operation(simulated_moved_files)

    print("\n--- Attempting Undo ---")
    success, msg = undo_last_sort()
    print(f"Undo Result: {msg}")

    print("\n--- Checking files after undo ---")
    if os.path.exists(os.path.join(test_source_dir, "image1.jpg")):
        print("image1.jpg is back in source folder.")
    if os.path.exists(os.path.join(test_source_dir, "doc1.pdf")):
        print("doc1.pdf is back in source folder.")

    # Clean up test directories
    print("\n--- Cleaning up test directories ---")
    if os.path.exists(test_source_dir):
        shutil.rmtree(test_source_dir)
    if os.path.exists(test_dest_dir):
        shutil.rmtree(test_dest_dir)
    if os.path.exists(UNDO_LOG_FILE):
        os.remove(UNDO_LOG_FILE)
    print("Cleanup complete.")