"""
Main window for the Markdown Viewer application.
"""

import logging
from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QMenuBar, QMenu, QToolBar, QPushButton, QFileDialog, QMessageBox,
    QLabel, QStatusBar, QApplication, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QSettings
from PySide6.QtGui import QAction, QKeySequence, QIcon, QFont, QPixmap

from .widgets.markdown_editor import MarkdownEditor
from .widgets.markdown_preview import MarkdownPreview
from .utils.settings import SettingsManager
from .utils.theme_manager import ThemeManager, Theme

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window with editor and preview panes.
    """
    
    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        
        # Initialize settings and theme
        self.settings_manager = SettingsManager()
        self.theme_manager = ThemeManager()
        
        # File handling
        self.current_file_path: Optional[str] = None
        self.is_modified = False
        
        # Recent files
        self.recent_files: List[str] = []
        
        # Setup UI
        self._setup_ui()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_status_bar()
        self._setup_connections()
        
        # Apply theme first
        self.theme_manager.apply_initial_theme()
        
        # Restore settings
        self._restore_settings()
        
        # Set window properties
        self.setWindowTitle("Markdown Viewer")
        self.setMinimumSize(800, 600)
        
        # Set window icon
        self._set_window_icon()
        
        # Update UI state
        self._update_ui_state()
    
    def _set_window_icon(self) -> None:
        """Set the window icon."""
        try:
            from pathlib import Path
            
            # Try to load ICO file first (best for Windows)
            icon_path = Path(__file__).parent / "resources" / "icon.ico"
            if icon_path.exists():
                icon = QIcon(str(icon_path))
                self.setWindowIcon(icon)
                logger.info("Loaded ICO icon: %s", icon_path)
                return
            
            # Fallback to PNG
            png_path = Path(__file__).parent / "resources" / "icon.png"
            if png_path.exists():
                icon = QIcon(str(png_path))
                self.setWindowIcon(icon)
                logger.info("Loaded PNG icon: %s", png_path)
                return
            
            logger.warning("No icon files found")
            
        except Exception as e:
            logger.warning("Could not load window icon: %s", e)
    
    def _setup_ui(self) -> None:
        """Set up the main UI layout."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)
        
        # Create editor
        self.editor = MarkdownEditor()
        
        # Create preview
        self.preview = MarkdownPreview()
        
        # Add widgets to splitter
        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.preview)
        
        # Set initial splitter sizes (50/50)
        self.splitter.setSizes([400, 400])
        
        # Hide editor by default
        self.editor.setVisible(False)
    
    def _setup_menus(self) -> None:
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # New file
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.setStatusTip("Create a new file")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        # Open file
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Open an existing file")
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)
        
        # Recent files submenu
        self.recent_menu = file_menu.addMenu("Open &Recent")
        self._update_recent_menu()
        
        file_menu.addSeparator()
        
        # Save file
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.setStatusTip("Save the current file")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        self.save_action = save_action
        
        # Save as
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.setStatusTip("Save the file with a new name")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        self.save_as_action = save_as_action
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Toggle editor
        toggle_editor_action = QAction("Toggle &Editor", self)
        toggle_editor_action.setShortcut(QKeySequence("F2"))
        toggle_editor_action.setStatusTip("Show/hide the editor panel")
        toggle_editor_action.setCheckable(True)
        toggle_editor_action.triggered.connect(self.toggle_editor)
        view_menu.addAction(toggle_editor_action)
        self.toggle_editor_action = toggle_editor_action
        
        view_menu.addSeparator()
        
        # Zoom controls
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.setStatusTip("Increase preview zoom")
        zoom_in_action.triggered.connect(self.preview.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.setStatusTip("Decrease preview zoom")
        zoom_out_action.triggered.connect(self.preview.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_reset_action = QAction("&Reset Zoom", self)
        zoom_reset_action.setShortcut(QKeySequence("Ctrl+0"))
        zoom_reset_action.setStatusTip("Reset preview zoom to 100%")
        zoom_reset_action.triggered.connect(self.preview.zoom_reset)
        view_menu.addAction(zoom_reset_action)
        
        view_menu.addSeparator()
        
        # Theme toggle
        toggle_theme_action = QAction("Toggle &Theme", self)
        toggle_theme_action.setShortcut(QKeySequence("Ctrl+T"))
        toggle_theme_action.setStatusTip("Toggle between light and dark theme")
        toggle_theme_action.triggered.connect(self.theme_manager.toggle_theme)
        view_menu.addAction(toggle_theme_action)
        
        view_menu.addSeparator()
        
        # Refresh preview
        refresh_action = QAction("&Refresh Preview", self)
        refresh_action.setShortcut(QKeySequence("Ctrl+R"))
        refresh_action.setStatusTip("Refresh the preview")
        refresh_action.triggered.connect(self.preview.refresh_content)
        view_menu.addAction(refresh_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        # Sanitize HTML toggle
        sanitize_action = QAction("&Sanitize HTML", self)
        sanitize_action.setStatusTip("Enable/disable HTML sanitization")
        sanitize_action.setCheckable(True)
        sanitize_action.triggered.connect(self._toggle_sanitize_html)
        tools_menu.addAction(sanitize_action)
        self.sanitize_action = sanitize_action
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # About
        about_action = QAction("&About", self)
        about_action.setStatusTip("About Markdown Viewer")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbar(self) -> None:
        """Set up the toolbar."""
        toolbar = self.addToolBar("Main")
        toolbar.setObjectName("main_toolbar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        
        # Toggle editor button
        self.toggle_editor_btn = QPushButton("📝 Edit")
        self.toggle_editor_btn.setCheckable(True)
        self.toggle_editor_btn.setStatusTip("Show/hide the editor panel")
        self.toggle_editor_btn.clicked.connect(self.toggle_editor)
        toolbar.addWidget(self.toggle_editor_btn)
        
        toolbar.addSeparator()
        
        # File operations
        new_btn = QPushButton("📄 New")
        new_btn.setStatusTip("Create a new file")
        new_btn.clicked.connect(self.new_file)
        toolbar.addWidget(new_btn)
        
        open_btn = QPushButton("📂 Open")
        open_btn.setStatusTip("Open an existing file")
        open_btn.clicked.connect(self.open_file_dialog)
        toolbar.addWidget(open_btn)
        
        save_btn = QPushButton("💾 Save")
        save_btn.setStatusTip("Save the current file")
        save_btn.clicked.connect(self.save_file)
        toolbar.addWidget(save_btn)
        self.save_btn = save_btn
        
        toolbar.addSeparator()
        
        # Zoom controls
        zoom_out_btn = QPushButton("−")
        zoom_out_btn.setObjectName("zoom_btn")
        zoom_out_btn.setStatusTip("Zoom out")
        zoom_out_btn.clicked.connect(self.preview.zoom_out)
        toolbar.addWidget(zoom_out_btn)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setObjectName("zoom_label")
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toolbar.addWidget(self.zoom_label)
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setObjectName("zoom_btn")
        zoom_in_btn.setStatusTip("Zoom in")
        zoom_in_btn.clicked.connect(self.preview.zoom_in)
        toolbar.addWidget(zoom_in_btn)
        
        zoom_reset_btn = QPushButton("🔄 Reset")
        zoom_reset_btn.setStatusTip("Reset zoom to 100%")
        zoom_reset_btn.clicked.connect(self.preview.zoom_reset)
        toolbar.addWidget(zoom_reset_btn)
        
        toolbar.addSeparator()
        
        # Theme toggle button
        theme_btn = QPushButton("🌙 Dark")
        theme_btn.setStatusTip("Toggle theme")
        theme_btn.clicked.connect(self._toggle_theme_with_button_update)
        toolbar.addWidget(theme_btn)
        self.theme_btn = theme_btn
    
    def _setup_status_bar(self) -> None:
        """Set up the status bar."""
        self.status_bar = self.statusBar()
        
        # File info label
        self.file_label = QLabel("No file")
        self.status_bar.addWidget(self.file_label)
        
        # Modified indicator
        self.modified_label = QLabel("")
        self.status_bar.addPermanentWidget(self.modified_label)
        
        # Zoom info
        self.zoom_info_label = QLabel("100%")
        self.status_bar.addPermanentWidget(self.zoom_info_label)
    
    def _setup_connections(self) -> None:
        """Set up signal connections."""
        # Editor text changes
        self.editor.text_changed_debounced.connect(self._on_editor_text_changed)
        self.editor.textChanged.connect(self._on_text_modified)
        
        # Preview zoom changes
        self.preview.zoom_changed.connect(self._on_zoom_changed)
        
        # Splitter changes
        self.splitter.splitterMoved.connect(self._on_splitter_moved)
    
    def _restore_settings(self) -> None:
        """Restore application settings."""
        # Window geometry
        self.settings_manager.restore_window_geometry(self)
        
        # Splitter state
        splitter_state = self.settings_manager.restore_splitter_state()
        if splitter_state:
            self.splitter.restoreState(splitter_state)
        
        # Editor visibility
        editor_visible = self.settings_manager.restore_editor_visible()
        self.editor.setVisible(editor_visible)
        self.toggle_editor_action.setChecked(editor_visible)
        self.toggle_editor_btn.setChecked(editor_visible)
        
        # Recent files
        self.recent_files = self.settings_manager.restore_recent_files()
        self._update_recent_menu()
        
        # HTML sanitization
        sanitize = self.settings_manager.restore_sanitize_html()
        self.preview.set_sanitize_html(sanitize)
        self.sanitize_action.setChecked(sanitize)
        
        # Preview zoom
        zoom_factor = self.settings_manager.restore_preview_zoom()
        self.preview.set_zoom_factor(zoom_factor)
        
        # Reopen last file if enabled
        if self.settings_manager.restore_reopen_last_file():
            last_file = self.settings_manager.restore_last_file()
            if last_file:
                self.open_file(last_file)
    
    def _save_settings(self) -> None:
        """Save application settings."""
        # Window geometry
        self.settings_manager.save_window_geometry(self)
        
        # Splitter state
        self.settings_manager.save_splitter_state(self.splitter.saveState())
        
        # Editor visibility
        self.settings_manager.save_editor_visible(self.editor.isVisible())
        
        # Recent files
        self.settings_manager.save_recent_files(self.recent_files)
        
        # HTML sanitization
        self.settings_manager.save_sanitize_html(self.preview.get_sanitize_html())
        
        # Preview zoom
        self.settings_manager.save_preview_zoom(self.preview.get_zoom_factor())
        
        # Last file
        if self.current_file_path:
            self.settings_manager.save_last_file(self.current_file_path)
    
    def _update_ui_state(self) -> None:
        """Update UI state based on current conditions."""
        has_file = self.current_file_path is not None
        
        # Update save actions
        self.save_action.setEnabled(has_file and self.is_modified)
        self.save_as_action.setEnabled(True)
        self.save_btn.setEnabled(has_file and self.is_modified)
        
        # Update window title
        title = "Markdown Viewer"
        if self.current_file_path:
            filename = Path(self.current_file_path).name
            title = f"{filename} - {title}"
            if self.is_modified:
                title = f"*{title}"
        
        self.setWindowTitle(title)
        
        # Update status bar
        if self.current_file_path:
            self.file_label.setText(str(Path(self.current_file_path).name))
        else:
            self.file_label.setText("No file")
        
        self.modified_label.setText("Modified" if self.is_modified else "")
    
    def _update_recent_menu(self) -> None:
        """Update the recent files menu."""
        self.recent_menu.clear()
        
        for file_path in self.recent_files:
            if Path(file_path).exists():
                action = QAction(str(Path(file_path).name), self)
                action.setStatusTip(file_path)
                action.triggered.connect(lambda checked, path=file_path: self.open_file(path))
                self.recent_menu.addAction(action)
        
        if not self.recent_files:
            action = QAction("No recent files", self)
            action.setEnabled(False)
            self.recent_menu.addAction(action)
    
    def _on_editor_text_changed(self, text: str) -> None:
        """Handle debounced editor text changes."""
        self.preview.set_markdown_content(text)
    
    def _on_text_modified(self) -> None:
        """Handle immediate text modifications."""
        if not self.is_modified:
            self.is_modified = True
            self._update_ui_state()
    
    def _on_zoom_changed(self, zoom_factor: float) -> None:
        """Handle zoom changes."""
        percentage = int(zoom_factor * 100)
        self.zoom_label.setText(f"{percentage}%")
        self.zoom_info_label.setText(f"{percentage}%")
    
    def _on_splitter_moved(self) -> None:
        """Handle splitter movements."""
        # Save splitter state
        self.settings_manager.save_splitter_state(self.splitter.saveState())
    
    def _toggle_sanitize_html(self, checked: bool) -> None:
        """Toggle HTML sanitization."""
        self.preview.set_sanitize_html(checked)
    
    def _toggle_theme_with_button_update(self) -> None:
        """Toggle theme and update button text."""
        self.theme_manager.toggle_theme()
        
        # Update button text based on current theme
        if self.theme_manager.is_dark_theme():
            self.theme_btn.setText("☀️ Light")
        else:
            self.theme_btn.setText("🌙 Dark")
    
    def toggle_editor(self) -> None:
        """Toggle editor visibility."""
        visible = not self.editor.isVisible()
        self.editor.setVisible(visible)
        self.toggle_editor_action.setChecked(visible)
        self.toggle_editor_btn.setChecked(visible)
        
        # Save setting
        self.settings_manager.save_editor_visible(visible)
    
    def new_file(self) -> None:
        """Create a new file."""
        if self.is_modified and not self._confirm_discard_changes():
            return
        
        self.current_file_path = None
        self.is_modified = False
        self.editor.clear()
        self.preview.clear_content()
        self._update_ui_state()
    
    def open_file_dialog(self) -> None:
        """Open file dialog and load selected file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            "",
            "Markdown Files (*.md *.markdown *.mdown *.txt);;All Files (*.*)"
        )
        
        if file_path:
            self.open_file(file_path)
    
    def open_file(self, file_path: str) -> bool:
        """
        Open a file.
        
        Args:
            file_path: Path to the file to open
            
        Returns:
            True if successful, False otherwise
        """
        if self.is_modified and not self._confirm_discard_changes():
            return False
        
        try:
            path = Path(file_path)
            if not path.exists():
                QMessageBox.warning(self, "File Not Found", f"File not found: {file_path}")
                return False
            
            # Read file content with proper encoding handling
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                # Try with different encodings if UTF-8 fails
                try:
                    content = path.read_text(encoding="utf-8-sig")  # UTF-8 with BOM
                except UnicodeDecodeError:
                    try:
                        content = path.read_text(encoding="cp1252")  # Windows encoding
                    except UnicodeDecodeError:
                        content = path.read_text(encoding="latin1", errors="replace")
            
            # Clean any problematic characters
            content = content.replace('¶', '').replace('\u00b6', '')
            
            # Update editor and preview
            self.editor.setPlainText(content)
            self.preview.set_markdown_content(content, immediate=True)
            
            # Update state
            self.current_file_path = file_path
            self.is_modified = False
            
            # Update recent files
            self.recent_files = self.settings_manager.add_recent_file(file_path)
            self._update_recent_menu()
            
            self._update_ui_state()
            
            logger.info("Opened file: %s", file_path)
            return True
            
        except Exception as e:
            logger.exception("Error opening file: %s", e)
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
            return False
    
    def save_file(self) -> bool:
        """
        Save the current file.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.current_file_path:
            return self.save_file_as()
        
        return self._save_to_file(self.current_file_path)
    
    def save_file_as(self) -> bool:
        """
        Save the file with a new name.
        
        Returns:
            True if successful, False otherwise
        """
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Markdown File",
            "",
            "Markdown Files (*.md);;All Files (*.*)"
        )
        
        if file_path:
            return self._save_to_file(file_path)
        
        return False
    
    def _save_to_file(self, file_path: str) -> bool:
        """
        Save content to a specific file.
        
        Args:
            file_path: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(file_path)
            content = self.editor.toPlainText()
            
            # Clean any pilcrow characters before saving
            cleaned_content = content.replace('¶', '').replace('\u00b6', '')
            
            # Write file (UTF-8, no BOM)
            path.write_text(cleaned_content, encoding="utf-8")
            
            # Update state
            self.current_file_path = file_path
            self.is_modified = False
            
            # Update recent files
            self.recent_files = self.settings_manager.add_recent_file(file_path)
            self._update_recent_menu()
            
            self._update_ui_state()
            
            logger.info("Saved file: %s", file_path)
            return True
            
        except Exception as e:
            logger.exception("Error saving file: %s", e)
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
            return False
    
    def _confirm_discard_changes(self) -> bool:
        """
        Confirm discarding unsaved changes.
        
        Returns:
            True if user confirms, False otherwise
        """
        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            "You have unsaved changes. Do you want to discard them?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        return reply == QMessageBox.StandardButton.Yes
    
    def show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Markdown Viewer",
            "<h2>Markdown Viewer</h2>"
            "<p>A modern Markdown editor and viewer built with PySide6.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Live preview with syntax highlighting</li>"
            "<li>Zoom controls</li>"
            "<li>HTML sanitization</li>"
            "<li>Recent files</li>"
            "<li>Customizable interface</li>"
            "</ul>"
            "<p>Version 1.0.0</p>"
        )
    
    def closeEvent(self, event) -> None:
        """Handle close event."""
        if self.is_modified and not self._confirm_discard_changes():
            event.ignore()
            return
        
        # Save settings
        self._save_settings()
        
        event.accept()
        logger.info("Application closed")
