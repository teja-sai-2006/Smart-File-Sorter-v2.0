import sys
import os
import shutil
import threading
from datetime import datetime, date
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QGroupBox, QCheckBox,
    QComboBox, QDateEdit, QListWidget, QTableWidget, QTableWidgetItem,
    QFileDialog, QTextEdit, QSpinBox, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt, QDate, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QPalette, QColor

# Assuming these modules exist in the same directory or are in your PYTHONPATH
from config_manager import load_config, save_config, export_config, import_config, export_report
from file_sorter import scan_files
from rule_loader import load_rules_from_json, save_rules_to_json, manage_rules_ui
from undo_manager import undo_last_sort, log_sort_operation # Directly import log_sort_operation here
from smart_sorting import smart_categorize
from directory_watcher import DirectoryWatcher

class WorkerSignals(QObject):
    finished = pyqtSignal(list)
    progress = pyqtSignal(str)
    error = pyqtSignal(str)

class SmartFileSorter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart File Sorter — NeoFutures v2.0")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("background-color: white; color: black;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Initialize data
        self.current_files = []
        self.rules = {}
        self.config = load_config()
        self.directory_watcher = None
        self.dark_mode = False

        self.create_theme_toggle()
        self.create_quick_start_panel()
        self.create_folder_setup_panel()
        self.create_sorting_options_panel()
        self.create_preview_area()
        self.create_advanced_settings_panel()
        self.create_scheduling_panel()
        self.create_console_area()
        self.create_footer()

        # Load initial rules
        self.load_initial_rules()
        
        self.show()

    def create_theme_toggle(self):
        toggle_button = QPushButton("🌙 Toggle Dark Mode")
        toggle_button.clicked.connect(self.toggle_theme)
        toggle_button.setMaximumWidth(150)
        self.layout.addWidget(toggle_button, alignment=Qt.AlignmentFlag.AlignRight)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #2b2b2b; color: white; }
                QGroupBox { border: 1px solid #555; padding-top: 10px; margin-top: 5px; }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }
                QPushButton { background-color: #404040; border: 1px solid #555; padding: 5px; }
                QPushButton:hover { background-color: #505050; }
                QLineEdit, QComboBox, QSpinBox { background-color: #404040; border: 1px solid #555; padding: 2px; }
                QTableWidget { background-color: #353535; alternate-background-color: #404040; }
                QTextEdit { background-color: #1e1e1e; color: #fff; border: 1px solid #555; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: white; color: black; }
                QGroupBox { border: 1px solid #ccc; padding-top: 10px; margin-top: 5px; }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }
                QPushButton { background-color: #f0f0f0; border: 1px solid #ccc; padding: 5px; }
                QPushButton:hover { background-color: #e0e0e0; }
                QLineEdit, QComboBox, QSpinBox { background-color: white; border: 1px solid #ccc; padding: 2px; }
                QTableWidget { background-color: white; alternate-background-color: #f5f5f5; }
                QTextEdit { background-color: white; color: black; border: 1px solid #ccc; }
            """)

    def create_quick_start_panel(self):
        panel = QGroupBox("🚀 Quick Start Panel")
        layout = QVBoxLayout(panel)
        
        welcome_label = QLabel("Welcome to Smart File Sorter - Organize your files intelligently!")
        welcome_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0066cc;")
        layout.addWidget(welcome_label)
        
        start_button = QPushButton("🎯 Start Sorting Now")
        start_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        start_button.clicked.connect(self.start_sorting)
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.layout.addWidget(panel)

    def create_folder_setup_panel(self):
        panel = QGroupBox("📁 Folder Setup")
        layout = QVBoxLayout(panel)

        # Source folder row
        source_row = QHBoxLayout()
        source_row.addWidget(QLabel("Source Folder:"))
        self.source_folder_input = QLineEdit()
        self.source_folder_input.setPlaceholderText("Select the folder to scan for files...")
        source_row.addWidget(self.source_folder_input)
        browse_source_button = QPushButton("📂 Browse")
        browse_source_button.clicked.connect(self.browse_source_folder)
        source_row.addWidget(browse_source_button)
        layout.addLayout(source_row)

        # Destination folder row
        dest_row = QHBoxLayout()
        dest_row.addWidget(QLabel("Destination Folder:"))
        self.destination_folder_input = QLineEdit()
        self.destination_folder_input.setPlaceholderText("Select where sorted files will be moved...")
        dest_row.addWidget(self.destination_folder_input)
        browse_dest_button = QPushButton("📂 Browse")
        browse_dest_button.clicked.connect(self.browse_destination_folder)
        dest_row.addWidget(browse_dest_button)
        layout.addLayout(dest_row)

        self.layout.addWidget(panel)

    def create_sorting_options_panel(self):
        panel = QGroupBox("⚙️ Sorting Options")
        layout = QVBoxLayout(panel)

        # Checkboxes row
        checkbox_row = QHBoxLayout()
        self.scan_subfolders_checkbox = QCheckBox("🔍 Scan subfolders recursively")
        self.scan_subfolders_checkbox.setChecked(True)
        checkbox_row.addWidget(self.scan_subfolders_checkbox)
        
        self.modified_filter_checkbox = QCheckBox("📅 Enable Modified Before Filter")
        self.modified_filter_checkbox.clicked.connect(self.toggle_date_picker)
        checkbox_row.addWidget(self.modified_filter_checkbox)
        layout.addLayout(checkbox_row)

        # Size filter row
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("File Size Filter:"))
        self.size_filter_combo = QComboBox()
        self.size_filter_combo.addItems(["Any Size", ">1MB", ">10MB", ">100MB", "Custom Size..."])
        self.size_filter_combo.currentTextChanged.connect(self.toggle_custom_size)
        size_row.addWidget(self.size_filter_combo)

        self.custom_size_input = QSpinBox()
        self.custom_size_input.setSuffix(" MB")
        self.custom_size_input.setMaximum(10240)
        self.custom_size_input.setValue(1)
        self.custom_size_input.setVisible(False)
        size_row.addWidget(self.custom_size_input)
        
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setEnabled(False)
        size_row.addWidget(QLabel("Modified Before:"))
        size_row.addWidget(self.date_picker)
        layout.addLayout(size_row)

        # Rules row
        rules_row = QHBoxLayout()
        self.load_rules_button = QPushButton("📄 Load Rules from JSON")
        self.load_rules_button.clicked.connect(self.load_rules_from_file)
        rules_row.addWidget(self.load_rules_button)

        self.manage_rules_button = QPushButton("⚙️ Manage Custom Rules")
        self.manage_rules_button.clicked.connect(self.manage_rules)
        rules_row.addWidget(self.manage_rules_button)
        layout.addLayout(rules_row)

        # Excluded extensions
        layout.addWidget(QLabel("🚫 Excluded Extensions:"))
        self.excluded_extensions_list = QListWidget()
        self.excluded_extensions_list.setMaximumHeight(80)
        self.update_excluded_extensions_list()
        layout.addWidget(self.excluded_extensions_list)

        self.layout.addWidget(panel)

    def toggle_custom_size(self, value):
        self.custom_size_input.setVisible(value == "Custom Size...")

    def toggle_date_picker(self, checked):
        self.date_picker.setEnabled(checked)


    def create_preview_area(self):
        panel = QGroupBox("👀 Preview Area")
        layout = QVBoxLayout(panel)

        self.preview_label = QLabel("📊 Files Ready to Sort: 0 files (0 MB)")
        self.preview_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        layout.addWidget(self.preview_label)

        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(6)
        self.preview_table.setHorizontalHeaderLabels(["File Name", "Type", "Size", "Category", "Modified", "Path"])
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setSortingEnabled(True)
        
        # Set column widths
        header = self.preview_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.preview_table)

        # Action buttons
        button_row = QHBoxLayout()
        
        sort_button = QPushButton("✅ Sort Files Now")
        sort_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        sort_button.clicked.connect(self.execute_sort)
        button_row.addWidget(sort_button)

        self.undo_button = QPushButton("↩️ Undo Last Sort")
        self.undo_button.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 8px;")
        self.undo_button.clicked.connect(self.undo_last_operation)
        button_row.addWidget(self.undo_button)

        refresh_button = QPushButton("🔄 Refresh Preview")
        refresh_button.clicked.connect(self.start_sorting)
        button_row.addWidget(refresh_button)

        layout.addLayout(button_row)
        self.layout.addWidget(panel)

    def create_advanced_settings_panel(self):
        panel = QGroupBox("🔧 Advanced Settings")
        layout = QVBoxLayout(panel)

        # Checkboxes
        checkbox_row = QHBoxLayout()
        self.auto_watch_checkbox = QCheckBox("👁️ Enable Auto-Watch Directory")
        self.auto_watch_checkbox.stateChanged.connect(self.toggle_auto_watch)
        checkbox_row.addWidget(self.auto_watch_checkbox)

        self.ai_sort_checkbox = QCheckBox("🤖 Use AI Smart Sorting")
        checkbox_row.addWidget(self.ai_sort_checkbox)
        layout.addLayout(checkbox_row)

        # Action buttons
        button_row = QHBoxLayout()
        
        self.export_report_button = QPushButton("📊 Export Report")
        self.export_report_button.clicked.connect(self.export_report)
        button_row.addWidget(self.export_report_button)

        self.export_config_button = QPushButton("💾 Export Config")
        self.export_config_button.clicked.connect(self.export_config)
        button_row.addWidget(self.export_config_button)

        self.import_config_button = QPushButton("📁 Import Config")
        self.import_config_button.clicked.connect(self.import_config)
        button_row.addWidget(self.import_config_button)

        layout.addLayout(button_row)
        self.layout.addWidget(panel)

    def create_scheduling_panel(self):
        panel = QGroupBox("⏰ Scheduling (Future Feature)")
        layout = QHBoxLayout(panel)

        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["Hourly", "Daily", "Weekly", "Monthly"])
        layout.addWidget(QLabel("Frequency:"))
        layout.addWidget(self.frequency_combo)

        self.time_picker = QDateEdit()
        self.time_picker.setCalendarPopup(True)
        self.time_picker.setDate(QDate.currentDate())
        layout.addWidget(QLabel("Next Run:"))
        layout.addWidget(self.time_picker)

        self.enable_scheduler_checkbox = QCheckBox("📅 Enable Scheduler")
        layout.addWidget(self.enable_scheduler_checkbox)

        self.layout.addWidget(panel)

    def create_console_area(self):
        panel = QGroupBox("💻 Console Output")
        layout = QVBoxLayout(panel)
        
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setMaximumHeight(150)
        self.console_output.setStyleSheet("font-family: 'Courier New', monospace; font-size: 10px;")
        layout.addWidget(self.console_output)
        
        # Add clear button
        clear_button = QPushButton("🗑️ Clear Console")
        clear_button.clicked.connect(self.console_output.clear)
        layout.addWidget(clear_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.layout.addWidget(panel)
        
        # Initial console message
        self.log_to_console("Smart File Sorter initialized successfully!", "SUCCESS")

    def create_footer(self):
        footer = QLabel("🚀 Smart File Sorter v2.0 | A project by Tejas Sai | 📧 tejasai13052006@gmail.com")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: gray; font-size: 10px; margin: 5px;")
        self.layout.addWidget(footer)

    def log_to_console(self, message, level="INFO"):
        """Log messages to the console with timestamps and colors."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        color_map = {
            "INFO": "#2196F3",
            "SUCCESS": "#4CAF50", 
            "WARNING": "#FF9800",
            "ERROR": "#f44336"
        }
        
        color = color_map.get(level, "#000000")
        formatted_message = f'<span style="color: {color};">[{timestamp}] {level}: {message}</span>'
        
        self.console_output.append(formatted_message)
        self.console_output.verticalScrollBar().setValue(
            self.console_output.verticalScrollBar().maximum()
        )

    def browse_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if folder:
            self.source_folder_input.setText(folder)
            self.log_to_console(f"Source folder set to: {folder}")

    def browse_destination_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if folder:
            self.destination_folder_input.setText(folder)
            self.log_to_console(f"Destination folder set to: {folder}")

    def load_initial_rules(self):
        """Load initial rules on startup."""
        try:
            self.rules = load_rules_from_json()
            self.log_to_console(f"Loaded {len(self.rules)} custom rules")
        except Exception as e:
            self.log_to_console(f"Failed to load rules: {e}", "ERROR")
            self.rules = {}

    def load_rules_from_file(self):
        """Load rules from a selected JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Rules File", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                self.rules = load_rules_from_json(file_path)
                self.log_to_console(f"Successfully loaded {len(self.rules)} rules from {file_path}", "SUCCESS")
                QMessageBox.information(self, "Success", f"Loaded {len(self.rules)} rules successfully!")
            except Exception as e:
                self.log_to_console(f"Failed to load rules: {e}", "ERROR")
                QMessageBox.warning(self, "Error", f"Failed to load rules: {e}")

    def manage_rules(self):
        """Open rules management dialog."""
        self.log_to_console("Opening rules management...")
        # For now, use console-based management
        # In a full implementation, this would open a GUI dialog
        try:
            self.rules = manage_rules_ui()
            self.log_to_console("Rules management completed", "SUCCESS")
        except Exception as e:
            self.log_to_console(f"Rules management failed: {e}", "ERROR")

    def update_excluded_extensions_list(self):
        """Update the excluded extensions list display."""
        self.excluded_extensions_list.clear()
        for ext in self.config.get('excluded_extensions', []):
            self.excluded_extensions_list.addItem(ext)

    def toggle_auto_watch(self, state):
        """Toggle directory auto-watching."""
        if state == Qt.CheckState.Checked:
            source_folder = self.source_folder_input.text()
            if source_folder and os.path.exists(source_folder):
                self.start_directory_watching(source_folder)
            else:
                self.auto_watch_checkbox.setChecked(False)
                QMessageBox.warning(self, "Warning", "Please select a valid source folder first!")
        else:
            self.stop_directory_watching()

    def start_directory_watching(self, directory):
        """Start watching directory for changes."""
        try:
            self.directory_watcher = DirectoryWatcher(directory, self.on_directory_change)
            if self.directory_watcher.start_watching():
                self.log_to_console(f"Started watching directory: {directory}", "SUCCESS")
            else:
                self.log_to_console("Failed to start directory watching", "ERROR")
        except Exception as e:
            self.log_to_console(f"Directory watching error: {e}", "ERROR")

    def stop_directory_watching(self):
        """Stop directory watching."""
        if self.directory_watcher:
            self.directory_watcher.stop_watching()
            self.log_to_console("Stopped directory watching", "INFO")

    def on_directory_change(self, changes):
        """Handle directory change events."""
        added_count = len(changes.get('added', []))
        modified_count = len(changes.get('modified', []))
        deleted_count = len(changes.get('deleted', []))
        
        if added_count > 0:
            self.log_to_console(f"Detected {added_count} new files", "INFO")
        if modified_count > 0:
            self.log_to_console(f"Detected {modified_count} modified files", "INFO")
        if deleted_count > 0:
            self.log_to_console(f"Detected {deleted_count} deleted files", "INFO")

    def get_size_filter(self):
        """Get the size filter in bytes."""
        size_option = self.size_filter_combo.currentText()
        size_map = {
            ">1MB": 1 * 1024 * 1024,
            ">10MB": 10 * 1024 * 1024,
            ">100MB": 100 * 1024 * 1024
        }
        
        if size_option == "Custom Size...":
            return self.custom_size_input.value() * 1024 * 1024
        else:
            return size_map.get(size_option, 0)

    def start_sorting(self):
        """Start the file sorting process."""
        source_folder = self.source_folder_input.text().strip()
        
        if not source_folder:
            self.log_to_console("Please select a source folder", "WARNING")
            QMessageBox.warning(self, "Warning", "Please select a source folder!")
            return
        
        if not os.path.exists(source_folder):
            self.log_to_console(f"Source folder does not exist: {source_folder}", "ERROR")
            QMessageBox.warning(self, "Error", "Source folder does not exist!")
            return

        self.log_to_console(f"Starting file scan in: {source_folder}")
        
        # Prepare filters
        filters = {
            'excluded_extensions': self.config.get('excluded_extensions', []),
            'min_size': self.get_size_filter(),
            'max_size': float('inf'),
            'cutoff_date': self.date_picker.date().toPyDate() if self.modified_filter_checkbox.isChecked() else None,
            'rules': self.rules
        }

        try:
            # Scan files
            found_files = scan_files(
                source_folder, 
                recursive=self.scan_subfolders_checkbox.isChecked(), 
                filters=filters
            )
            
            # Apply AI sorting if enabled
            if self.ai_sort_checkbox.isChecked():
                self.log_to_console("Applying AI smart categorization...")
                for file_data in found_files:
                    ai_category = smart_categorize(file_data['path'])
                    if ai_category != file_data['category']:
                        file_data['category'] = f"AI: {ai_category}"

            self.current_files = found_files
            self.update_preview_table(found_files)
            
            total_size = sum(f['size_bytes'] for f in found_files)
            size_str = self.format_file_size(total_size)
            
            self.preview_label.setText(f"📊 Files Ready to Sort: {len(found_files)} files ({size_str})")
            self.log_to_console(f"Scan completed: Found {len(found_files)} files ({size_str})", "SUCCESS")
            
        except Exception as e:
            self.log_to_console(f"Error during file scan: {e}", "ERROR")
            QMessageBox.critical(self, "Error", f"Error during file scan: {e}")

    def update_preview_table(self, files):
        """Update the preview table with file data."""
        self.preview_table.setRowCount(len(files))
        
        for row, file_data in enumerate(files):
            self.preview_table.setItem(row, 0, QTableWidgetItem(file_data['name']))
            self.preview_table.setItem(row, 1, QTableWidgetItem(file_data['type']))
            self.preview_table.setItem(row, 2, QTableWidgetItem(file_data['size']))
            self.preview_table.setItem(row, 3, QTableWidgetItem(file_data['category']))
            self.preview_table.setItem(row, 4, QTableWidgetItem(file_data['modified']))
            self.preview_table.setItem(row, 5, QTableWidgetItem(file_data['path']))

    def execute_sort(self):
        """Execute the actual file sorting."""
        if not self.current_files:
            QMessageBox.warning(self, "Warning", "No files to sort! Please run a scan first.")
            return

        destination_folder = self.destination_folder_input.text().strip()
        if not destination_folder:
            QMessageBox.warning(self, "Warning", "Please select a destination folder!")
            return

        # Confirm operation
        reply = QMessageBox.question(
            self, "Confirm Sort",
            f"Are you sure you want to sort {len(self.current_files)} files?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        self.log_to_console(f"Starting file sort operation for {len(self.current_files)} files...")

        moved_files = []
        for file_data in self.current_files:
            category_folder = os.path.join(destination_folder, file_data['category'])
            os.makedirs(category_folder, exist_ok=True)  # ✅ Ensure folder exists

            destination_path = os.path.join(category_folder, file_data['name'])

            try:
                shutil.move(file_data['path'], destination_path)  # ✅ Actually move the file
                moved_files.append({
                    'original_path': file_data['path'],
                    'new_path': destination_path,
                    'category': file_data['category']
                })
                self.log_to_console(f"✅ Moved: {file_data['name']} ➜ {file_data['category']}", "INFO")
            except Exception as e:
                self.log_to_console(f"❌ Failed to move {file_data['name']}: {e}", "ERROR")

        # After the for loop ends, log the operation and give feedback
        log_sort_operation(moved_files) # Corrected indentation and used imported function directly

        self.log_to_console(f"Sort operation completed for {len(moved_files)} files!", "SUCCESS")
        QMessageBox.information(self, "Success", f"Successfully sorted {len(moved_files)} files!")


    def undo_last_operation(self):
        """Undo the last sort operation."""
        success, message = undo_last_sort()
        
        if success:
            self.log_to_console(message, "SUCCESS")
            QMessageBox.information(self, "Success", message)
        else:
            self.log_to_console(message, "ERROR")
            QMessageBox.warning(self, "Error", message)

    def export_report(self):
        """Export current preview as a report."""
        if not self.current_files:
            QMessageBox.warning(self, "Warning", "No data to export! Please run a scan first.")
            return
        
        file_path, file_type = QFileDialog.getSaveFileName(
            self, "Export Report", f"sort_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}", 
            "CSV Files (*.csv);;JSON Files (*.json)"
        )
        
        if file_path:
            try:
                report_type = 'csv' if 'csv' in file_type.lower() else 'json'
                result_path = export_report(self.current_files, report_type, file_path)
                
                if result_path:
                    self.log_to_console(f"Report exported to: {result_path}", "SUCCESS")
                    QMessageBox.information(self, "Success", f"Report exported to:\n{result_path}")
                else:
                    self.log_to_console("Failed to export report", "ERROR")
                    
            except Exception as e:
                self.log_to_console(f"Export error: {e}", "ERROR")
                QMessageBox.critical(self, "Error", f"Export failed: {e}")

    def export_config(self):
        """Export current configuration."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Configuration", f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                result_path = export_config(file_path)
                if result_path:
                    self.log_to_console(f"Configuration exported to: {result_path}", "SUCCESS")
                    QMessageBox.information(self, "Success", f"Configuration exported to:\n{result_path}")
                else:
                    self.log_to_console("Failed to export configuration", "ERROR")
            except Exception as e:
                self.log_to_console(f"Export error: {e}", "ERROR")
                QMessageBox.critical(self, "Error", f"Export failed: {e}")

    def import_config(self):
        """Import configuration from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Configuration", "", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                new_config = import_config(file_path)
                if new_config:
                    self.config = new_config
                    self.update_ui_from_config()
                    self.log_to_console(f"Configuration imported from: {file_path}", "SUCCESS")
                    QMessageBox.information(self, "Success", "Configuration imported successfully!")
                else:
                    self.log_to_console("Failed to import configuration", "ERROR")
            except Exception as e:
                self.log_to_console(f"Import error: {e}", "ERROR")
                QMessageBox.critical(self, "Error", f"Import failed: {e}")

    def update_ui_from_config(self):
        """Update UI elements from loaded configuration."""
        self.auto_watch_checkbox.setChecked(self.config.get('auto_watch', False))
        self.ai_sort_checkbox.setChecked(self.config.get('ai_sorting', False))
        self.update_excluded_extensions_list()

    def format_file_size(self, size_bytes):
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"

    def closeEvent(self, event):
        """Handle application closing."""
        if self.directory_watcher:
            self.directory_watcher.stop_watching()
        
        # Save current configuration
        save_config(self.config)
        self.log_to_console("Application closing - configuration saved", "INFO")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better cross-platform appearance
    
    window = SmartFileSorter()
    sys.exit(app.exec())