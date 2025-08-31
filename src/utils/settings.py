"""
Settings management for the Markdown Viewer application.
"""

from typing import Any, Optional, List
from pathlib import Path

from PySide6.QtCore import QSettings, QByteArray, QSize, QPoint
from PySide6.QtWidgets import QWidget


class SettingsManager:
    """
    Manages application settings using QSettings.
    """
    
    def __init__(self) -> None:
        """Initialize the settings manager."""
        self.settings = QSettings()
    
    # Window geometry and state
    def save_window_geometry(self, widget: QWidget) -> None:
        """Save window geometry and state."""
        self.settings.setValue("window/geometry", widget.saveGeometry())
        self.settings.setValue("window/state", widget.saveState())
    
    def restore_window_geometry(self, widget: QWidget) -> None:
        """Restore window geometry and state."""
        geometry = self.settings.value("window/geometry")
        if geometry:
            widget.restoreGeometry(geometry)
        
        state = self.settings.value("window/state")
        if state:
            widget.restoreState(state)
    
    # Splitter state
    def save_splitter_state(self, splitter_state: QByteArray) -> None:
        """Save splitter state."""
        self.settings.setValue("splitter/state", splitter_state)
    
    def restore_splitter_state(self) -> Optional[QByteArray]:
        """Restore splitter state."""
        return self.settings.value("splitter/state")
    
    # Editor visibility
    def save_editor_visible(self, visible: bool) -> None:
        """Save editor visibility state."""
        self.settings.setValue("editor/visible", visible)
    
    def restore_editor_visible(self) -> bool:
        """Restore editor visibility state."""
        return self.settings.value("editor/visible", False, type=bool)
    
    # Recent files
    def save_recent_files(self, files: List[str]) -> None:
        """Save recent files list."""
        # Keep only the last 5 files
        recent_files = files[-5:] if len(files) > 5 else files
        self.settings.setValue("recent_files", recent_files)
    
    def restore_recent_files(self) -> List[str]:
        """Restore recent files list."""
        files = self.settings.value("recent_files", [], type=list)
        # Filter out files that no longer exist
        return [f for f in files if Path(f).exists()]
    
    def add_recent_file(self, file_path: str) -> List[str]:
        """
        Add a file to recent files list.
        
        Args:
            file_path: Path to the file to add
            
        Returns:
            Updated list of recent files
        """
        recent_files = self.restore_recent_files()
        
        # Remove if already in list
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to beginning
        recent_files.insert(0, file_path)
        
        # Keep only last 5
        recent_files = recent_files[:5]
        
        self.save_recent_files(recent_files)
        return recent_files
    
    # Last opened file
    def save_last_file(self, file_path: str) -> None:
        """Save the last opened file."""
        self.settings.setValue("last_file", file_path)
    
    def restore_last_file(self) -> Optional[str]:
        """Restore the last opened file."""
        file_path = self.settings.value("last_file")
        if file_path and Path(file_path).exists():
            return file_path
        return None
    
    # Reopen last file setting
    def save_reopen_last_file(self, reopen: bool) -> None:
        """Save whether to reopen last file on startup."""
        self.settings.setValue("startup/reopen_last_file", reopen)
    
    def restore_reopen_last_file(self) -> bool:
        """Restore whether to reopen last file on startup."""
        return self.settings.value("startup/reopen_last_file", True, type=bool)
    
    # HTML sanitization
    def save_sanitize_html(self, sanitize: bool) -> None:
        """Save HTML sanitization setting."""
        self.settings.setValue("preview/sanitize_html", sanitize)
    
    def restore_sanitize_html(self) -> bool:
        """Restore HTML sanitization setting."""
        return self.settings.value("preview/sanitize_html", False, type=bool)
    
    # Preview zoom
    def save_preview_zoom(self, zoom_factor: float) -> None:
        """Save preview zoom factor."""
        self.settings.setValue("preview/zoom_factor", zoom_factor)
    
    def restore_preview_zoom(self) -> float:
        """Restore preview zoom factor."""
        return self.settings.value("preview/zoom_factor", 1.0, type=float)
    
    # Font settings
    def save_editor_font(self, font_family: str, font_size: int) -> None:
        """Save editor font settings."""
        self.settings.setValue("editor/font_family", font_family)
        self.settings.setValue("editor/font_size", font_size)
    
    def restore_editor_font(self) -> tuple[str, int]:
        """Restore editor font settings."""
        family = self.settings.value("editor/font_family", "Consolas", type=str)
        size = self.settings.value("editor/font_size", 11, type=int)
        return family, size
