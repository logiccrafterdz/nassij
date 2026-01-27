"""
Unicode normalization and diacritic handling utilities.
Critical for Arabic text processing fidelity.
"""
import unicodedata
import regex as re
from typing import Tuple


# Arabic diacritics range: U+064B to U+0652, plus U+0670 (dagger alif)
DIACRITIC_RANGES = [
    (0x064B, 0x0652),  # Fatha, Damma, Kasra, etc.
    0x0670,            # Dagger alif
    0x0640,            # Tatweel (kashida)
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
        elif code in (0x0670, 0x0640):
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
        if 0x064B <= code <= 0x0652 or code in (0x0670, 0x0640):
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
        if not (0x064B <= code <= 0x0652 or code in (0x0670, 0x0640)):
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


def is_likely_reversed_arabic(text: str) -> bool:
    """
    Heuristic to detect if Arabic text is in visual order (reversed).
    Checks for characters that usually end words/sentences appearing at the start.
    
    Args:
        text: Input text string
        
    Returns:
        True if text is likely in visual order
    """
    if not text:
        return False
        
    # Remove whitespace and numbers for analysis
    clean_text = re.sub(r'[\s\d\p{P}]', '', text)
    if not clean_text or len(clean_text) < 3:
        return False
        
    # Heuristic 1: Ta Marbuta (ة) or Final Yaa (ى) at the beginning of words
    # Words in the string
    words = text.split()
    arabic_words = [w for w in words if any(is_arabic_char(c) for c in w)]
    
    if not arabic_words:
        return False
        
    # Ta Marbuta (ة) index: \u0629
    # Final Yaa (ى) index: \u0649
    # These characters almost EXCLUSIVELY appear at the end of Arabic words.
    reversed_indicators = 0
    total_checks = 0
    
    for word in arabic_words:
        # Strip non-arabic from word edges
        w = re.sub(r'^[^\u0600-\u06FF]+|[^\u0600-\u06FF]+$', '', word)
        if len(w) < 2:
            continue
            
        total_checks += 1
        # If word starts with ة or ى, it's a very strong indicator of reversal
        if w[0] in ('ة', 'ى'):
            reversed_indicators += 1
        # If word ends with common initial-only prefixes like ال (reversed as لا)
        # Note: ال is \u0627\u0644. Reversed is \u0644\u0627 (Lam-Alif ligature)
        if w.endswith('لا') and not w.startswith('ال'):
            reversed_indicators += 0.5
            
    if total_checks > 0 and (reversed_indicators / total_checks) > 0.3:
        return True
        
    return False


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

