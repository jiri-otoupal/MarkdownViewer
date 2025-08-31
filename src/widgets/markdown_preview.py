"""
Markdown preview widget using QTextBrowser with zoom controls.
"""

import logging
from typing import Optional

from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QFont, QTextOption
from PySide6.QtWidgets import QTextEdit, QWidget

from ..utils.markdown_renderer import MarkdownRenderer
from ..utils.text_cleaner import clean_html

logger = logging.getLogger(__name__)


class MarkdownPreview(QTextEdit):
    """
    A Markdown preview widget with zoom controls and HTML rendering.
    """
    
    # Signals
    zoom_changed = Signal(float)  # Emitted when zoom level changes
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the Markdown preview widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize renderer
        self.renderer = MarkdownRenderer()
        
        # Zoom settings
        self._zoom_factor = 1.0
        self._min_zoom = 0.25
        self._max_zoom = 5.0
        self._zoom_step = 0.1
        self._base_font_size = 11
        
        # Setup the widget
        self._setup_preview()
        
        # Update timer for debounced updates
        self._update_timer = QTimer()
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._perform_update)
        
        # Current content
        self._current_markdown = ""
        self._sanitize_html = False
    
    def _setup_preview(self) -> None:
        """Set up the preview widget properties."""
        # Enable HTML rendering
        self.setReadOnly(True)

        # Set document stylesheet to override defaults for code blocks only
        self.document().setDefaultStyleSheet("""
            pre, .codehilite {
                background-color: #161b22 !important;
                background-image: none !important;
                line-height: 0.9 !important;
                white-space: pre !important;
                display: block !important;
                margin: 16px 0 !important;
                padding: 16px !important;
            }
            pre *, .codehilite * {
                background-color: transparent !important;
                background-image: none !important;
                margin: 0 !important;
                padding: 0 !important;
                line-height: inherit !important;
                display: inline !important;
            }
        """)
        
        # Set text options to not show whitespace
        option = QTextOption()
        option.setFlags(QTextOption.Flag.ShowTabsAndSpaces | QTextOption.Flag.ShowLineAndParagraphSeparators)
        # Actually, we want to DISABLE these flags, so we set empty flags
        option.setFlags(QTextOption.Flag(0))
        self.document().setDefaultTextOption(option)

        # Disable QTextBrowser's default alternating background and selection
        self.setStyleSheet("""
            QTextBrowser {
                alternate-background-color: transparent;
                background-color: #1e1e1e;
                selection-background-color: #264f78;
                selection-color: #ffffff;
            }
            QTextBrowser::item {
                background-color: transparent;
            }
            QTextBrowser::item:alternate {
                background-color: transparent;
            }
        """)

        # QTextEdit doesn't have anchorClicked signal, so we'll handle links differently
        # Links will still be clickable through the HTML rendering
        
        # Set initial content (simple ASCII to avoid encoding issues)
        initial_content = "# Welcome to Markdown Viewer\n\nStart editing to see the preview here."
        initial_html = self.renderer.render(initial_content)
        self.setHtml(initial_html)
        
        # Set font with emoji support
        font = QFont()
        font.setStyleHint(QFont.StyleHint.System)
        font.setPointSize(self._base_font_size)
        
        # Try to set a font that supports emojis
        emoji_fonts = [
            "Segoe UI Emoji",  # Windows 10/11 emoji font
            "Apple Color Emoji",  # macOS
            "Noto Color Emoji",  # Linux
            "Segoe UI",  # Windows fallback
            "Arial",  # Universal fallback
        ]
        
        for font_name in emoji_fonts:
            font.setFamily(font_name)
            if font.exactMatch():
                break
        
        self.setFont(font)

    def set_markdown_content(self, markdown_text: str, immediate: bool = False) -> None:
        """
        Set the Markdown content to be rendered.
        
        Args:
            markdown_text: The Markdown text to render
            immediate: If True, update immediately without debouncing
        """
        self._current_markdown = markdown_text
        
        if immediate:
            self._perform_update()
        else:
            # Debounce updates to avoid excessive rendering
            self._update_timer.stop()
            self._update_timer.start(100)  # 100ms delay
    
    def _perform_update(self) -> None:
        """Perform the actual content update."""
        try:
            html_content = self.renderer.render(self._current_markdown, self._sanitize_html)
            
            # Clean HTML content to remove any problematic characters
            cleaned_html = clean_html(html_content)
            
            # Save current scroll position
            scroll_bar = self.verticalScrollBar()
            scroll_position = scroll_bar.value()
            
            # Update content
            self.setHtml(cleaned_html)
            
            # Apply zoom
            self._apply_zoom()
            
            # Restore scroll position
            scroll_bar.setValue(scroll_position)
            
        except Exception as e:
            logger.exception("Error updating preview: %s", e)
            error_html = f"<h1>Preview Error</h1><p>Could not render Markdown: {str(e)}</p>"
            self.setHtml(error_html)
    

    
    def set_sanitize_html(self, sanitize: bool) -> None:
        """
        Set whether to sanitize HTML in the rendered output.
        
        Args:
            sanitize: Whether to sanitize HTML
        """
        if self._sanitize_html != sanitize:
            self._sanitize_html = sanitize
            # Re-render with new sanitization setting
            if self._current_markdown:
                self._perform_update()
    
    def get_sanitize_html(self) -> bool:
        """
        Get the current HTML sanitization setting.
        
        Returns:
            Whether HTML sanitization is enabled
        """
        return self._sanitize_html
    
    def zoom_in(self) -> None:
        """Increase the zoom level."""
        new_zoom = min(self._zoom_factor + self._zoom_step, self._max_zoom)
        self.set_zoom_factor(new_zoom)
    
    def zoom_out(self) -> None:
        """Decrease the zoom level."""
        new_zoom = max(self._zoom_factor - self._zoom_step, self._min_zoom)
        self.set_zoom_factor(new_zoom)
    
    def zoom_reset(self) -> None:
        """Reset zoom to 100%."""
        self.set_zoom_factor(1.0)
    
    def set_zoom_factor(self, factor: float) -> None:
        """
        Set the zoom factor.
        
        Args:
            factor: Zoom factor (1.0 = 100%)
        """
        factor = max(self._min_zoom, min(factor, self._max_zoom))
        
        if abs(self._zoom_factor - factor) > 0.001:  # Avoid unnecessary updates
            self._zoom_factor = factor
            self._apply_zoom()
            self.zoom_changed.emit(self._zoom_factor)
    
    def get_zoom_factor(self) -> float:
        """
        Get the current zoom factor.
        
        Returns:
            Current zoom factor
        """
        return self._zoom_factor
    
    def _apply_zoom(self) -> None:
        """Apply the current zoom factor to the widget."""
        # Use QTextBrowser's font-based zoom
        current_font = self.font()
        new_size = int(self._base_font_size * self._zoom_factor)
        
        # Clamp font size between reasonable limits
        new_size = max(6, min(72, new_size))
        
        current_font.setPointSize(new_size)
        self.setFont(current_font)
    
    def get_zoom_percentage(self) -> int:
        """
        Get the current zoom as a percentage.
        
        Returns:
            Zoom percentage (100 = 100%)
        """
        return int(self._zoom_factor * 100)
    
    def wheelEvent(self, event) -> None:
        """
        Handle mouse wheel events for zooming with Ctrl key.
        
        Args:
            event: The wheel event
        """
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom with Ctrl+Wheel
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            # Normal scrolling
            super().wheelEvent(event)
    
    def keyPressEvent(self, event) -> None:
        """
        Handle key press events for zoom shortcuts.
        
        Args:
            event: The key event
        """
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
                self.zoom_in()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Minus:
                self.zoom_out()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_0:
                self.zoom_reset()
                event.accept()
                return
        
        super().keyPressEvent(event)
    
    def refresh_content(self) -> None:
        """Force refresh the current content."""
        self._perform_update()
    
    def get_toc(self) -> Optional[str]:
        """
        Get the table of contents from the rendered content.
        
        Returns:
            Table of contents HTML or None
        """
        return self.renderer.get_toc()
    
    def clear_content(self) -> None:
        """Clear the preview content."""
        self._current_markdown = ""
        self.setHtml(self.renderer.render(""))
    
    def export_html(self) -> str:
        """
        Export the current content as HTML.
        
        Returns:
            Complete HTML document
        """
        return self.renderer.render(self._current_markdown, self._sanitize_html)
