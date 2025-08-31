"""
Markdown rendering utilities for the Markdown Viewer application.
"""

import logging
from pathlib import Path
from typing import Optional

import markdown
from markdown.extensions import codehilite, fenced_code, tables, toc
import bleach
from pygments.formatters import HtmlFormatter

from .text_cleaner import clean_text, clean_html

logger = logging.getLogger(__name__)


class MarkdownRenderer:
    """
    Handles Markdown to HTML conversion with syntax highlighting and sanitization.
    """
    
    def __init__(self) -> None:
        """Initialize the Markdown renderer."""
        self._markdown_processor = self._create_markdown_processor()
        self._style_css = self._load_style_css()
        self._pygments_css = self._load_pygments_css()
    
    def _create_markdown_processor(self) -> markdown.Markdown:
        """
        Create and configure the Markdown processor.
        
        Returns:
            Configured Markdown processor
        """
        extensions = [
            'fenced_code',
            'codehilite',
            'tables',
            'toc',
            'nl2br',
            'sane_lists'
        ]
        
        extension_configs = {
            'codehilite': {
                'css_class': 'codehilite',
                'use_pygments': True,
                'noclasses': False,
                'linenums': False
            },
            'toc': {
                'permalink': True,
                'permalink_title': 'Permalink to this headline',
                'toc_depth': 6
            }
        }
        
        return markdown.Markdown(
            extensions=extensions,
            extension_configs=extension_configs,
            output_format='html5'
        )
    
    def _load_style_css(self) -> str:
        """
        Load the main CSS styles.
        
        Returns:
            CSS content as string
        """
        try:
            css_path = Path(__file__).parent.parent / "resources" / "style.css"
            if css_path.exists():
                return css_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning("Could not load style.css: %s", e)
        
        return ""
    
    def _load_pygments_css(self) -> str:
        """
        Load the Pygments CSS styles.
        
        Returns:
            CSS content as string
        """
        try:
            css_path = Path(__file__).parent.parent / "resources" / "pygments.css"
            if css_path.exists():
                return css_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning("Could not load pygments.css: %s", e)
        
        return ""
    
    def render(self, markdown_text: str, sanitize: bool = False) -> str:
        """
        Render Markdown text to HTML.
        
        Args:
            markdown_text: The Markdown text to render
            sanitize: Whether to sanitize the HTML output
            
        Returns:
            Rendered HTML string
        """
        if not markdown_text.strip():
            return self._create_html_document("")
        
        try:
            # Reset the processor to clear any state
            self._markdown_processor.reset()
            
            # Clean the input text to remove any problematic characters
            cleaned_text = clean_text(markdown_text)
            
            # Convert Markdown to HTML
            html_content = self._markdown_processor.convert(cleaned_text)
            
            # Sanitize if requested
            if sanitize:
                html_content = self._sanitize_html(html_content)
            
            # Create complete HTML document
            return self._create_html_document(html_content)
            
        except Exception as e:
            logger.exception("Error rendering Markdown: %s", e)
            error_html = f"<p><strong>Error rendering Markdown:</strong> {str(e)}</p>"
            return self._create_html_document(error_html)
    

    
    def _sanitize_html(self, html: str) -> str:
        """
        Sanitize HTML content to remove potentially dangerous elements.
        
        Args:
            html: HTML content to sanitize
            
        Returns:
            Sanitized HTML content
        """
        # Allow common HTML tags and attributes
        allowed_tags = [
            'a', 'abbr', 'acronym', 'b', 'blockquote', 'br', 'code', 'dd', 'del',
            'div', 'dl', 'dt', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr',
            'i', 'img', 'ins', 'kbd', 'li', 'ol', 'p', 'pre', 'q', 's', 'samp',
            'span', 'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th',
            'thead', 'tr', 'tt', 'u', 'ul', 'var'
        ]
        
        allowed_attributes = {
            '*': ['class', 'id'],
            'a': ['href', 'title', 'name'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'table': ['border', 'cellpadding', 'cellspacing'],
            'td': ['colspan', 'rowspan'],
            'th': ['colspan', 'rowspan'],
        }
        
        return bleach.clean(
            html,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    
    def _create_html_document(self, body_content: str) -> str:
        """
        Create a complete HTML document with styles.
        
        Args:
            body_content: HTML content for the body
            
        Returns:
            Complete HTML document
        """
        # Clean the body content
        clean_body = clean_html(body_content)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown Preview</title>
    <style>
{self._style_css}

{self._pygments_css}
    </style>
</head>
<body>
{clean_body}
</body>
</html>"""
    
    def get_toc(self) -> Optional[str]:
        """
        Get the table of contents from the last rendered document.
        
        Returns:
            Table of contents HTML or None if not available
        """
        if hasattr(self._markdown_processor, 'toc') and self._markdown_processor.toc:
            return self._markdown_processor.toc
        return None
