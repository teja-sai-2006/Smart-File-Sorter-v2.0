# Smart File Sorter v2.0

A powerful and easy-to-use file organizer made using PyQt6. It helps you sort and manage files automatically with smart filters, custom rules, and pattern-based categorization.

## 🚀 Features

### Main Features

* **Smart Scanning**: Scans folders with filters and options
* **Auto Categorization**: Sorts files by type, name, content, and rules
* **Preview Before Sorting**: Shows what will happen before sorting
* **Undo Sort**: Undo the last 10 sorts anytime
* **Custom Rules**: Add your own sorting rules using JSON

### Extra Features

* **Smart Sorting**: Detects file types using name patterns and structure
* **Auto-Watch Folders**: Keeps watching folders for new files
* **Filter by Size & Date**: Sort only specific file sizes or dates
* **Reports**: Export results as CSV or JSON
* **Save Settings**: Import and export all your settings
* **Themes**: Switch between light and dark mode

### User Interface

* **Modern Design**: Clean and easy layout
* **Live Console**: Shows all actions with colors
* **Sortable Table**: Preview with file info and sorting
* **Progress Bar**: Shows operation status

## 📋 Requirements

* Python 3.8 or above
* PyQt6 (>= 6.4.0)
* watchdog (>= 2.1.9)

## 🛠️ Installation

1. Download or clone the folder
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python main.py
```

## 💡 How to Use

### Basic Steps

1. Choose a **source folder** (files to be sorted)
2. Choose a **destination folder**
3. Set your filters and options
4. Click **"Start Sorting Now"** to preview
5. Click **"Sort Files Now"** to sort
6. Use **"Undo Last Sort"** to undo

### Custom Rules

Create a `.json` file like this:

```json
{
  ".pdf": "Documents",
  ".jpg": "Images",
  "screenshot": "Screenshots",
  "*_backup": "Backups"
}
```

Then load it using **"Load Rules from JSON"**

### Filters

* **Size Filter**: 1MB, 10MB, 100MB, or custom
* **Date Filter**: Before a selected date
* **Exclude Extensions**: Skip certain file types
* **Recursive**: Choose whether to include subfolders

### Smart Sorting

Sorts based on:

* File name patterns
* File content structure
* Media file sizes
* File dates

### Directory Monitoring

* Enable **Auto-Watch**
* Detects changes in folders
* Logs actions in real-time

## 📁 Folder Structure

```
smart-file-sorter/
├── main.py
├── file_sorter.py
├── rule_loader.py
├── config_manager.py
├── undo_manager.py
├── smart_sorting.py
├── directory_watcher.py
├── requirements.txt
└── README.md
```

## 🔧 Configuration Files

* `file_sorter_config.json`: App settings
* `custom_rules.json`: Your custom rules
* `undo_log.json`: Stores last operations

## 🚨 Safety

* **Preview First**: No changes happen without preview
* **Undo Support**: Can undo last 10 sorts
* **Logs Everything**: Keeps full history
* **Auto Rename**: Avoids name conflicts
* **Error Handling**: Shows all errors clearly

## 🎨 Customization

### Themes

Click the theme button to switch light/dark mode

### Categories

Default types include:

* Images, Videos, Audio, Documents
* Archives, Code Files, Screenshots
* Downloads, Personal, Projects

### Excluded Files

Add extensions you want to skip in settings

## 🐛 Common Issues

1. **Permission Denied**: Make sure the destination folder is writable
2. **File in Use**: Close the file if it’s open
3. **Long Path**: Use shorter folder names (especially on Windows)
4. **Memory**: Use filters for huge folders

### Debugging

* Enable console logging
* Check for messages in the console
* Export a report to review results

## 📈 Performance

* Supports large folders (10,000+ files)
* Real-time watching
* Uses memory efficiently
* Future plan: Multi-threading

## 🤝 Contribute

Ideas you can work on:

* Better categorization logic
* Cloud support
* Batch sorting
* More filters
* Language support

## 📞 Contact

Made by Tejas Sai  
📧 [tejasai13052006@gmail.com](mailto:tejasai13052006@gmail.com)

---

**Smart File Sorter v2.0** – Sort files the smart way!
