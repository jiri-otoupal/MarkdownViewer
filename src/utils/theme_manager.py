"""
Theme management for the Markdown Viewer application.
"""

import logging
from pathlib import Path
from typing import Optional
from enum import Enum

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPalette, QColor

logger = logging.getLogger(__name__)


class Theme(Enum):
    """Available themes."""
    LIGHT = "light"
    DARK = "dark"


class ThemeManager(QObject):
    """
    Manages application themes and styling.
    """
    
    # Signals
    theme_changed = Signal(Theme)
    
    def __init__(self) -> None:
        """Initialize the theme manager."""
        super().__init__()
        self._current_theme = Theme.DARK  # Default to dark theme
        self._dark_stylesheet = self._load_dark_stylesheet()
    
    def _load_dark_stylesheet(self) -> str:
        """
        Load the dark theme stylesheet.
        
        Returns:
            Dark theme stylesheet content
        """
        try:
            css_path = Path(__file__).parent.parent / "resources" / "dark_theme.qss"
            if css_path.exists():
                return css_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning("Could not load dark theme stylesheet: %s", e)
        
        return ""
    
    def get_current_theme(self) -> Theme:
        """
        Get the current theme.
        
        Returns:
            Current theme
        """
        return self._current_theme
    
    def set_theme(self, theme: Theme) -> None:
        """
        Set the application theme.
        
        Args:
            theme: Theme to apply
        """
        if theme == self._current_theme:
            return
        
        self._current_theme = theme
        self._apply_theme()
        self.theme_changed.emit(theme)
    
    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        new_theme = Theme.LIGHT if self._current_theme == Theme.DARK else Theme.DARK
        self.set_theme(new_theme)
    
    def _apply_theme(self) -> None:
        """Apply the current theme to the application."""
        app = QApplication.instance()
        if not app:
            return
        
        if self._current_theme == Theme.DARK:
            self._apply_dark_theme(app)
        else:
            self._apply_light_theme(app)
    
    def _apply_dark_theme(self, app: QApplication) -> None:
        """
        Apply dark theme to the application.
        
        Args:
            app: QApplication instance
        """
        # Set dark palette
        palette = QPalette()
        
        # Window colors
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        
        # Base colors (for input widgets)
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 48))
        
        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(212, 212, 212))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
        
        # Button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(62, 62, 66))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        
        # Highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 204))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        # Disabled colors
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(128, 128, 128))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(128, 128, 128))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(128, 128, 128))
        
        app.setPalette(palette)
        
        # Apply stylesheet
        if self._dark_stylesheet:
            app.setStyleSheet(self._dark_stylesheet)
        
        logger.info("Applied dark theme")
    
    def _apply_light_theme(self, app: QApplication) -> None:
        """
        Apply light theme to the application.
        
        Args:
            app: QApplication instance
        """
        # Reset to system palette and stylesheet
        app.setPalette(app.style().standardPalette())
        app.setStyleSheet("")
        
        logger.info("Applied light theme")
    
    def apply_initial_theme(self) -> None:
        """Apply the initial theme on application startup."""
        self._apply_theme()
    
    def is_dark_theme(self) -> bool:
        """
        Check if the current theme is dark.
        
        Returns:
            True if dark theme is active
        """
        return self._current_theme == Theme.DARK
    
    def get_editor_background_color(self) -> str:
        """
        Get the background color for the editor based on current theme.
        
        Returns:
            Hex color string
        """
        if self._current_theme == Theme.DARK:
            return "#1e1e1e"
        else:
            return "#ffffff"
    
    def get_editor_text_color(self) -> str:
        """
        Get the text color for the editor based on current theme.
        
        Returns:
            Hex color string
        """
        if self._current_theme == Theme.DARK:
            return "#d4d4d4"
        else:
            return "#000000"
    
    def get_line_number_background_color(self) -> str:
        """
        Get the line number area background color based on current theme.
        
        Returns:
            Hex color string
        """
        if self._current_theme == Theme.DARK:
            return "#252526"
        else:
            return "#f0f0f0"
    
    def get_line_number_text_color(self) -> str:
        """
        Get the line number text color based on current theme.
        
        Returns:
            Hex color string
        """
        if self._current_theme == Theme.DARK:
            return "#858585"
        else:
            return "#808080"
