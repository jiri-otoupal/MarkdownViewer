"""
Markdown editor widget with syntax highlighting and basic editing features.
"""

import logging
from typing import Optional

from PySide6.QtWidgets import (
    QPlainTextEdit, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Signal, Qt, QTimer, QRegularExpression
from PySide6.QtGui import (
    QFont, QFontMetrics, QPainter, QColor, QTextCursor, 
    QKeySequence, QAction, QTextCharFormat, QSyntaxHighlighter,
    QTextDocument, QTextOption
)

logger = logging.getLogger(__name__)


class MarkdownHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter for Markdown text.
    """
    
    def __init__(self, document: QTextDocument) -> None:
        """
        Initialize the Markdown syntax highlighter.
        
        Args:
            document: The text document to highlight
        """
        super().__init__(document)
        self._setup_formats()
    
    def _setup_formats(self) -> None:
        """Set up text formats for different Markdown elements."""
        # Use theme-aware colors
        from ..utils.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        is_dark = theme_manager.is_dark_theme()
        
        # Header formats
        self.header_format = QTextCharFormat()
        self.header_format.setForeground(QColor(86, 156, 214) if is_dark else QColor(0, 100, 200))
        self.header_format.setFontWeight(QFont.Weight.Bold)
        
        # Bold format
        self.bold_format = QTextCharFormat()
        self.bold_format.setFontWeight(QFont.Weight.Bold)
        self.bold_format.setForeground(QColor(220, 220, 220) if is_dark else QColor(0, 0, 0))
        
        # Italic format
        self.italic_format = QTextCharFormat()
        self.italic_format.setFontItalic(True)
        self.italic_format.setForeground(QColor(206, 145, 120) if is_dark else QColor(100, 50, 0))
        
        # Code format
        self.code_format = QTextCharFormat()
        self.code_format.setForeground(QColor(206, 145, 120) if is_dark else QColor(200, 0, 0))
        self.code_format.setFontFamily("Consolas, Monaco, Courier New, monospace")
        self.code_format.setBackground(QColor(45, 45, 48) if is_dark else QColor(245, 245, 245))
        
        # Link format
        self.link_format = QTextCharFormat()
        self.link_format.setForeground(QColor(86, 156, 214) if is_dark else QColor(0, 150, 200))
        self.link_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline)
        
        # List format
        self.list_format = QTextCharFormat()
        self.list_format.setForeground(QColor(156, 220, 254) if is_dark else QColor(100, 100, 100))
        
        # Blockquote format
        self.blockquote_format = QTextCharFormat()
        self.blockquote_format.setForeground(QColor(106, 153, 85) if is_dark else QColor(100, 100, 100))
        self.blockquote_format.setFontItalic(True)
    
    def highlightBlock(self, text: str) -> None:
        """
        Highlight a block of text.
        
        Args:
            text: The text block to highlight
        """
        # Headers
        header_pattern = QRegularExpression(r'^#{1,6}\s+.*$')
        match = header_pattern.match(text)
        if match.hasMatch():
            self.setFormat(0, len(text), self.header_format)
            return
        
        # Blockquotes
        if text.startswith('>'):
            self.setFormat(0, len(text), self.blockquote_format)
            return
        
        # Lists
        list_pattern = QRegularExpression(r'^\s*[-*+]\s+')
        match = list_pattern.match(text)
        if match.hasMatch():
            self.setFormat(0, match.capturedLength(), self.list_format)
        
        # Numbered lists
        numbered_list_pattern = QRegularExpression(r'^\s*\d+\.\s+')
        match = numbered_list_pattern.match(text)
        if match.hasMatch():
            self.setFormat(0, match.capturedLength(), self.list_format)
        
        # Inline code
        code_pattern = QRegularExpression(r'`([^`]+)`')
        iterator = code_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.code_format)
        
        # Bold text
        bold_pattern = QRegularExpression(r'\*\*([^*]+)\*\*')
        iterator = bold_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.bold_format)
        
        # Italic text
        italic_pattern = QRegularExpression(r'\*([^*]+)\*')
        iterator = italic_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.italic_format)
        
        # Links
        link_pattern = QRegularExpression(r'\[([^\]]+)\]\([^)]+\)')
        iterator = link_pattern.globalMatch(text)
        while iterator.hasNext():
            match = iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), self.link_format)


class LineNumberArea(QWidget):
    """
    Widget for displaying line numbers in the editor.
    """
    
    def __init__(self, editor: 'MarkdownEditor') -> None:
        """
        Initialize the line number area.
        
        Args:
            editor: The parent editor widget
        """
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self) -> None:
        """Return the size hint for the line number area."""
        return self.editor.line_number_area_width()
    
    def paintEvent(self, event) -> None:
        """Paint the line numbers."""
        self.editor.line_number_area_paint_event(event)


class MarkdownEditor(QPlainTextEdit):
    """
    A Markdown editor with syntax highlighting and line numbers.
    """
    
    # Signals
    text_changed_debounced = Signal(str)  # Emitted after debounce delay
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
        Initialize the Markdown editor.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Set up the editor
        self._setup_editor()
        self._setup_line_numbers()
        self._setup_syntax_highlighting()
        self._setup_debounce_timer()
        
        # Connect signals
        self.textChanged.connect(self._on_text_changed)
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
    
    def _setup_editor(self) -> None:
        """Set up the editor properties."""
        # Set font with emoji support
        font = QFont()
        
        # Try monospace fonts that support emojis
        monospace_fonts = [
            "Cascadia Code",      # Windows Terminal font with emoji
            "JetBrains Mono",     # Popular coding font
            "Fira Code",          # Another popular coding font
            "Consolas",           # Windows monospace
            "Monaco",             # macOS monospace
            "Courier New",        # Universal fallback
        ]
        
        for font_name in monospace_fonts:
            font.setFamily(font_name)
            if font.exactMatch():
                break
        
        font.setPointSize(11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # Set tab width
        font_metrics = QFontMetrics(font)
        tab_width = font_metrics.horizontalAdvance(' ') * 4
        self.setTabStopDistance(tab_width)
        
        # Enable word wrap
        self.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        
        # Set placeholder text
        self.setPlaceholderText("Start typing your Markdown content here...")
    
    def _setup_line_numbers(self) -> None:
        """Set up line number display."""
        self.line_number_area = LineNumberArea(self)
        self.line_number_area.setObjectName("line_number_area")
        self._update_line_number_area_width()
    
    def _setup_syntax_highlighting(self) -> None:
        """Set up Markdown syntax highlighting."""
        self.highlighter = MarkdownHighlighter(self.document())
    
    def _setup_debounce_timer(self) -> None:
        """Set up the debounce timer for text changes."""
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self._emit_text_changed_debounced)
        self.debounce_delay = 300  # 300ms delay
    
    def _on_text_changed(self) -> None:
        """Handle text changes with debouncing."""
        self.debounce_timer.stop()
        self.debounce_timer.start(self.debounce_delay)
    
    def _emit_text_changed_debounced(self) -> None:
        """Emit the debounced text changed signal."""
        # Get text and clean any pilcrow characters that might have been introduced
        text = self.toPlainText()
        cleaned_text = text.replace('¶', '').replace('\u00b6', '')
        self.text_changed_debounced.emit(cleaned_text)
    
    def line_number_area_width(self) -> int:
        """
        Calculate the width needed for the line number area.
        
        Returns:
            Width in pixels
        """
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def _update_line_number_area_width(self) -> None:
        """Update the line number area width."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def _update_line_number_area(self, rect, dy: int) -> None:
        """
        Update the line number area when the editor is scrolled.
        
        Args:
            rect: The update rectangle
            dy: Vertical scroll delta
        """
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), 
                                       self.line_number_area.width(), 
                                       rect.height())
        
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width()
    
    def resizeEvent(self, event) -> None:
        """Handle resize events."""
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            cr.left(), cr.top(), 
            self.line_number_area_width(), 
            cr.height()
        )
    
    def line_number_area_paint_event(self, event) -> None:
        """
        Paint the line numbers.
        
        Args:
            event: The paint event
        """
        painter = QPainter(self.line_number_area)
        
        # Use theme-aware colors
        from ..utils.theme_manager import ThemeManager
        theme_manager = ThemeManager()
        bg_color = QColor(theme_manager.get_line_number_background_color())
        text_color = QColor(theme_manager.get_line_number_text_color())
        
        painter.fillRect(event.rect(), bg_color)
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(text_color)
                painter.drawText(
                    0, int(top), 
                    self.line_number_area.width() - 3, 
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, 
                    number
                )
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
    
    def set_debounce_delay(self, delay_ms: int) -> None:
        """
        Set the debounce delay for text changes.
        
        Args:
            delay_ms: Delay in milliseconds
        """
        self.debounce_delay = delay_ms
    
    def insert_markdown_syntax(self, syntax_type: str) -> None:
        """
        Insert Markdown syntax at the cursor position.
        
        Args:
            syntax_type: Type of syntax to insert ('bold', 'italic', 'code', etc.)
        """
        cursor = self.textCursor()
        
        if syntax_type == 'bold':
            if cursor.hasSelection():
                text = cursor.selectedText()
                cursor.insertText(f"**{text}**")
            else:
                cursor.insertText("****")
                cursor.movePosition(QTextCursor.MoveOperation.Left, 
                                  QTextCursor.MoveMode.MoveAnchor, 2)
        
        elif syntax_type == 'italic':
            if cursor.hasSelection():
                text = cursor.selectedText()
                cursor.insertText(f"*{text}*")
            else:
                cursor.insertText("**")
                cursor.movePosition(QTextCursor.MoveOperation.Left, 
                                  QTextCursor.MoveMode.MoveAnchor, 1)
        
        elif syntax_type == 'code':
            if cursor.hasSelection():
                text = cursor.selectedText()
                cursor.insertText(f"`{text}`")
            else:
                cursor.insertText("``")
                cursor.movePosition(QTextCursor.MoveOperation.Left, 
                                  QTextCursor.MoveMode.MoveAnchor, 1)
        
        elif syntax_type == 'link':
            if cursor.hasSelection():
                text = cursor.selectedText()
                cursor.insertText(f"[{text}]()")
                cursor.movePosition(QTextCursor.MoveOperation.Left, 
                                  QTextCursor.MoveMode.MoveAnchor, 1)
            else:
                cursor.insertText("[]()")
                cursor.movePosition(QTextCursor.MoveOperation.Left, 
                                  QTextCursor.MoveMode.MoveAnchor, 3)
        
        self.setTextCursor(cursor)
