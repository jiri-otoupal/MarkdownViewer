"""
Text cleaning utilities to remove problematic Unicode characters.
"""

import re
import unicodedata


def clean_text(text: str) -> str:
    """
    Clean text by removing or replacing problematic Unicode characters.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return text
    
    # Remove pilcrow and paragraph markers
    cleaned = text.replace('¶', '')
    cleaned = cleaned.replace('\u00b6', '')  # Pilcrow sign
    
    # Remove replacement characters (question marks in boxes)
    cleaned = cleaned.replace('\ufffd', '')  # Replacement character
    
    # Replace paragraph and line separators with regular newlines
    cleaned = cleaned.replace('\u2029', '\n')  # Paragraph separator
    cleaned = cleaned.replace('\u2028', '\n')  # Line separator
    
    # Replace non-breaking spaces with regular spaces
    cleaned = cleaned.replace('\u00a0', ' ')   # Non-breaking space
    cleaned = cleaned.replace('\u202f', ' ')   # Narrow non-breaking space
    cleaned = cleaned.replace('\u2007', ' ')   # Figure space
    cleaned = cleaned.replace('\u2060', '')    # Word joiner
    
    # Remove zero-width characters (but keep zero-width joiner for emojis)
    cleaned = cleaned.replace('\u200b', '')    # Zero-width space
    cleaned = cleaned.replace('\u200c', '')    # Zero-width non-joiner
    # Keep \u200d (zero-width joiner) for emoji sequences
    cleaned = cleaned.replace('\ufeff', '')    # Zero-width no-break space (BOM)
    
    # Remove other problematic control characters (but preserve emojis)
    cleaned = re.sub(r'[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f-\u009f]', '', cleaned)
    
    # Normalize Unicode (decomposed to composed)
    cleaned = unicodedata.normalize('NFC', cleaned)
    
    # Normalize line endings
    cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
    
    return cleaned


def clean_html(html: str) -> str:
    """
    Clean HTML content by removing problematic characters.
    
    Args:
        html: HTML content to clean
        
    Returns:
        Cleaned HTML content
    """
    if not html:
        return html
    
    # First clean as regular text
    cleaned = clean_text(html)
    
    # Additional HTML-specific cleaning
    # Remove any remaining problematic entities
    cleaned = cleaned.replace('&para;', '')     # HTML pilcrow entity
    cleaned = cleaned.replace('&#182;', '')     # Numeric pilcrow entity
    cleaned = cleaned.replace('&#x00B6;', '')   # Hex pilcrow entity
    
    return cleaned


def is_problematic_char(char: str) -> bool:
    """
    Check if a character is problematic for display.
    
    Args:
        char: Single character to check
        
    Returns:
        True if the character is problematic
    """
    if not char or len(char) != 1:
        return False
    
    code = ord(char)
    
    # Pilcrow and related
    if code == 0x00b6:  # ¶
        return True
    
    # Replacement character
    if code == 0xfffd:  # �
        return True
    
    # Control characters (except tab, newline, carriage return)
    if code < 32 and code not in (9, 10, 13):
        return True
    
    # DEL and C1 control characters
    if 127 <= code <= 159:
        return True
    
    # Zero-width characters (but allow zero-width joiner for emojis)
    if code in (0x200b, 0x200c, 0x2060, 0xfeff):
        return True
    
    # Line/paragraph separators
    if code in (0x2028, 0x2029):
        return True
    
    return False
