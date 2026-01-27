from typing import Dict, List, Tuple
import regex as re

class LigatureProcessor:
    """
    Handles detection and validation of Arabic ligatures.
    Crucial for checking if text extraction or OCR preserved complex glyphs properly.
    """
    
    # Common mandatory ligatures
    LIGATURES = {
        '\ufefb': 'لا', # LAM WITH ALEF ISOLATED FORM
        '\ufef7': 'لا', # LAM WITH ALEF FINAL FORM
        '\ufef5': 'لآ', # LAM WITH ALEF MADDA ABOVE ISOLATED
        '\ufef9': 'لأ', # LAM WITH ALEF HAMZA ABOVE ISOLATED
        '\ufdf2': 'الله', # ALLAH LIGATURE
    }
    
    def __init__(self):
        pass
        
    def check_ligatures(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for ligature presence and correctness.
        Note: Standard Unicode strings usually store 'لا' as 'L+A' (logical).
        Visual ligatures (U+FEFB) usually appear only in presentation forms or corrupted OCR/PDFs.
        
        This tool helps detect if we have *Visual* characters in the stream.
        """
        results = {
            'visual_ligatures_found': 0,
            'logical_ligatures_found': 0, # "Lam + Alif" seq
            'details': []
        }
        
        # Check for Visual Forms (Presentation Forms B)
        # Block U+FE70 to U+FEFF
        visual_matches = re.findall(r'[\ufe70-\ufeff]', text)
        results['visual_ligatures_found'] = len(visual_matches)
        
        # Check for Logical Sequences
        # Lam + Alif
        logical_matches = re.findall(r'\u0644\u0627', text)
        results['logical_ligatures_found'] = len(logical_matches)
        
        return results

    def fix_visual_ligatures(self, text: str) -> str:
        """
        Convert visual presentation forms back to logical characters.
        Useful if extraction yielded visual glyphs (like from our 'bad' PDF).
        """
        # Mapping from Presentation Form B to General Arabic
        # This is a partial map, usually unicodedata.normalize('NFKC') handles compatibility decomposition!
        import unicodedata
        
        # Normalize NFKC (Compatibility Decomposition)
        # This turns ﻼ (U+FEFB) into ل + ا (Logical)
        return unicodedata.normalize('NFKC', text)
