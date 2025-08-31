#!/usr/bin/env python3
"""
Markdown Viewer - A PySide6 desktop application for viewing and editing Markdown files.

This is the main entry point for the application.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QDir
from PySide6.QtGui import QFont, QIcon

from src.main_window import MainWindow
from src.utils.logging_config import setup_logging


def setup_application() -> QApplication:
    """
    Set up the QApplication with proper attributes and settings.
    
    Returns:
        QApplication: Configured application instance
    """
    # Enable High DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    
    # Enable emoji rendering
    app.setAttribute(Qt.ApplicationAttribute.AA_UseDesktopOpenGL, True)
    
    # Set application properties
    app.setApplicationName("Markdown Viewer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("MarkdownViewer")
    app.setOrganizationDomain("markdownviewer.local")
    
    # Use system font
    system_font = QFont()
    system_font.setStyleHint(QFont.StyleHint.System)
    app.setFont(system_font)
    
    # Set application icon
    try:
        icon_path = Path("src/resources/icon.ico")
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
    except Exception as e:
        print(f"Could not load application icon: {e}")
    
    return app


def main() -> int:
    """
    Main application entry point.
    
    Returns:
        int: Application exit code
    """
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Create and configure application
        app = setup_application()
        
        # Create main window
        main_window = MainWindow()
        main_window.show()
        
        # Handle command line arguments
        if len(sys.argv) > 1:
            file_path = Path(sys.argv[1])
            if file_path.exists() and file_path.is_file():
                main_window.open_file(str(file_path))
        
        logger.info("Application started successfully")
        
        # Run application
        return app.exec()
        
    except Exception as e:
        logger.exception("Fatal error during application startup: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
