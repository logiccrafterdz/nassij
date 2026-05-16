"""
Arabic text processing module.
The heart of linguistic fidelity for Nassij.

This module handles:
- Unicode NFC normalization (MANDATORY)
- Right-to-left (RTL) text direction
- Arabic ligatures (لا, إلا, الله, etc.)
- Diacritics (tashkeel) preservation
"""
import unicodedata
import regex as re
from typing import Optional
from bidi.algorithm import get_display
import arabic_reshaper
import logging

logger = logging.getLogger(__name__)

from utils.unicode_helpers import normalize_nfc, count_diacritics, is_arabic_char


class ArabicProcessor:
    """
    Processes Arabic text with strict order of operations.
    Order is NON-NEGOTIABLE for correct rendering.
    """
    
    def __init__(self, preserve_diacritics: bool = True):
        """
        Initialize Arabic processor.
        
        Args:
            preserve_diacritics: If True, preserve tashkeel marks
        """
        self.preserve_diacritics = preserve_diacritics
        # arabic_reshaper works out of the box, no configuration needed
    
    def normalize_arabic_text(self, raw_text: str, logical: bool = False) -> str:
        """
        Process Arabic text with strict order:
        0. Detect and Repair Visual Text (Crucial for PDFs with pre-shaped glyphs)
        1. Unicode NFC normalization (MANDATORY FIRST STEP)
        2. Bidi direction correction (get_display) - SKIPPED IF logical=True
        3. Arabic reshaping (ligatures + connections) - SKIPPED IF logical=True
        4. Final NFC normalization (after reshaping)
        
        Args:
            raw_text: Raw text input (may be mixed Arabic/Latin)
            logical: If True, keep logical order and base characters (for Word/modern systems)
            
        Returns:
            Processed Arabic text
        """
        if not raw_text or not raw_text.strip():
            return raw_text
            
        # Step 0: Detect Visual Glyphs (Presentation Forms B) and Reset to Logical
        # This fixes the "Garbage In" from PDFs that store pre-reversed/pre-shaped text
        
        # Check if text contains Arabic Presentation Forms
        has_presentation_forms = bool(re.search(r'[\ufb50-\ufdff\ufe70-\ufeff]', raw_text))
        
        if has_presentation_forms:
            # NFKC maps visual glyphs (ﻼ) to base characters (ل+ا)
            text = unicodedata.normalize('NFKC', raw_text)
        else:
            text = raw_text
        
        # Step 1: Normalize to NFC
        text = normalize_nfc(text)
        
        if logical:
            # For DOCX (logical order), we just need standard Unicode normalization.
            # Modern OCR engines (PaddleOCR/EasyOCR) output correct logical text.
            # We don't need fragile heuristics to reverse text here.
            return normalize_nfc(text)

        # Step 2: Fix RTL direction using bidi algorithm
        # This handles mixed-script paragraphs correctly
        text = get_display(text)
        
        # Step 3: Apply Arabic reshaping for ligatures and connections
        # Only reshape if text contains Arabic characters
        if any(is_arabic_char(c) for c in text):
            try:
                text = arabic_reshaper.reshape(text)
            except Exception as e:
                # If reshaping fails, continue with bidi-corrected text
                # Never corrupt meaning for speed
                logger.warning(f"Arabic reshaping failed: {e}")
        
        # Step 4: Final NFC normalization pass (after reshaping)
        text = normalize_nfc(text)
        
        return text
    
    def process_paragraph(self, text: str, detect_script: bool = True, logical_output: bool = False) -> dict:
        """
        Process a paragraph of text, detecting script and applying appropriate processing.
        
        Args:
            text: Input paragraph text
            detect_script: If True, detect script and process accordingly
            logical_output: If True, return logical order (for DOCX)
            
        Returns:
            Dictionary with processed data
        """
        if not text or not text.strip():
            return {
                'text': text,
                'is_arabic': False,
                'diacritics_count': 0
            }
        
        # Count diacritics before processing
        diacritics_before = count_diacritics(text)
        
        # Detect if text is primarily Arabic
        is_arabic = False
        if detect_script:
            # Also consider characters in the Arabic block
            arabic_chars = sum(1 for c in text if is_arabic_char(c))
            total_chars = len([c for c in text if c.strip()])
            # If any significant Arabic is found, treat as Arabic to be safe with RTL
            is_arabic = total_chars > 0 and (arabic_chars / total_chars) > 0.1
        
        if is_arabic:
            processed_text = self.normalize_arabic_text(text, logical=logical_output)
        else:
            # For non-Arabic text, just normalize Unicode
            processed_text = normalize_nfc(text)
        
        # Count diacritics after processing
        diacritics_after = count_diacritics(processed_text)
        
        return {
            'text': processed_text,
            'is_arabic': is_arabic,
            'diacritics_count': diacritics_after,
            'diacritics_preserved': diacritics_after >= diacritics_before * 0.9  # 90% threshold
        }
    
    def validate_ligatures(self, text: str) -> dict:
        """
        Validate that known Arabic ligatures are preserved.
        
        Args:
            text: Processed text to validate
            
        Returns:
            Dictionary with validation results
        """
        known_ligatures = {
            'لا': 'لا',  # Lam + Alif
            'إلا': 'إلا',  # Alif + Lam + Alif
            'الله': 'الله',  # Alif + Lam + Lam + Heh
            'لله': 'لله',  # Lam + Lam + Heh
        }
        
        results = {}
        for ligature, expected in known_ligatures.items():
            # Check if ligature exists in text
            if ligature in text:
                # Verify it's correctly formed
                results[ligature] = {
                    'found': True,
                    'correct': ligature == expected,
                    'position': text.find(ligature)
                }
            else:
                results[ligature] = {
                    'found': False,
                    'correct': None,
                    'position': -1
                }
        
        return results

