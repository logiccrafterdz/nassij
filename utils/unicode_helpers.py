"""
Unicode normalization and diacritic handling utilities.
Critical for Arabic text processing fidelity.
"""
import unicodedata
import regex as re
from typing import Tuple


# Arabic diacritics range: U+064B to U+0652, plus U+0670 (dagger alif)
# NOTE: Tatweel (U+0640) is a visual extender, NOT a diacritic
DIACRITIC_RANGES = [
    (0x064B, 0x0652),  # Fatha, Damma, Kasra, etc.
    0x0670,            # Dagger alif
]


def normalize_nfc(text: str) -> str:
    """
    Normalize text to Unicode NFC (Canonical Composition).
    This is MANDATORY for Arabic text processing.
    
    Args:
        text: Input text string
        
    Returns:
        NFC-normalized text
    """
    if not text:
        return text
    return unicodedata.normalize('NFC', text)


def count_diacritics(text: str) -> int:
    """
    Count Arabic diacritics (tashkeel) in text.
    
    Args:
        text: Input text string
        
    Returns:
        Number of diacritic marks found
    """
    count = 0
    for char in text:
        code = ord(char)
        # Check main diacritic range
        if 0x064B <= code <= 0x0652:
            count += 1
        # Check specific diacritics
        elif code == 0x0670:
            count += 1
    return count


def extract_diacritics(text: str) -> str:
    """
    Extract only diacritic marks from text.
    
    Args:
        text: Input text string
        
    Returns:
        String containing only diacritic marks
    """
    diacritics = []
    for char in text:
        code = ord(char)
        if 0x064B <= code <= 0x0652 or code == 0x0670:
            diacritics.append(char)
    return ''.join(diacritics)


def remove_diacritics(text: str) -> str:
    """
    Remove all Arabic diacritics from text while preserving base characters.
    
    Args:
        text: Input text string
        
    Returns:
        Text with diacritics removed
    """
    result = []
    for char in text:
        code = ord(char)
        # Skip diacritic marks
        if not (0x064B <= code <= 0x0652 or code == 0x0670):
            result.append(char)
    return ''.join(result)


def is_arabic_char(char: str) -> bool:
    """
    Check if a character is Arabic (including extended Arabic blocks).
    
    Args:
        char: Single character string
        
    Returns:
        True if character is Arabic
    """
    if not char:
        return False
    code = ord(char)
    # Arabic block: U+0600-U+06FF
    # Extended-A: U+08A0-U+08FF
    # Extended-B: U+0870-U+089F
    # Presentation Forms A & B: U+FB50-U+FDFF, U+FE70-U+FEFF
    return (0x0600 <= code <= 0x06FF or 
            0x08A0 <= code <= 0x08FF or
            0x0870 <= code <= 0x089F or
            0xfb50 <= code <= 0xfdff or
            0xfe70 <= code <= 0xfeff)





def get_arabic_ratio(text: str) -> float:
    """
    Calculate the ratio of Arabic characters in text.
    
    Args:
        text: Input text string
        
    Returns:
        Ratio between 0.0 and 1.0
    """
    if not text:
        return 0.0
    
    arabic_count = sum(1 for char in text if is_arabic_char(char))
    total_chars = len([c for c in text if c.strip()])  # Exclude whitespace
    
    if total_chars == 0:
        return 0.0
    
    return arabic_count / total_chars


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace while preserving structure.
    
    Args:
        text: Input text string
        
    Returns:
        Text with normalized whitespace
    """
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    # Normalize line breaks
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\r', '\n', text)
    # Remove trailing whitespace from lines
    lines = [line.rstrip() for line in text.split('\n')]
    return '\n'.join(lines)

