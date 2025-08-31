"""
Logging configuration for the Markdown Viewer application.
"""

import logging
import logging.handlers
from typing import Optional


def setup_logging(
        log_level: int = logging.CRITICAL,
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Set up logging configuration - disabled by default.
    
    Args:
        log_level: Logging level (default: CRITICAL - effectively disabled)
        log_file: Path to log file (ignored)
        max_bytes: Maximum size of log file before rotation (ignored)
        backup_count: Number of backup log files to keep (ignored)
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.CRITICAL)  # Only show critical errors
    
    # Clear any existing handlers
    root_logger.handlers.clear()

    # Disable all logging by setting to CRITICAL level
    logging.getLogger("PySide6").setLevel(logging.CRITICAL)
    logging.getLogger("markdown").setLevel(logging.CRITICAL)
