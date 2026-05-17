import pytest
from core.arabic_processor import ArabicProcessor

class TestStage2Processing:
    """
    Stage 2 Tests: Verify that ArabicProcessor preserves valid logical text,
    fixes visual presentation forms, and doesn't corrupt diacritics.
    """
    
    def test_logical_text_unchanged(self):
        """Test B4: Logical Arabic text should not be modified into something else."""
        processor = ArabicProcessor()
        text = "مرحبا بالعالم"
        result = processor.process_paragraph(text, logical_output=True)
        assert result['text'] == text

    def test_visual_text_fixed(self):
        """Test B4: Visual presentation forms should be normalized back to logical characters."""
        processor = ArabicProcessor()
        # \ufefb is the isolated visual ligature for Lam-Alif (لا)
        # It should be converted back to logical Lam (ل) + Alif (ا)
        visual_text = "سلام \ufefb"
        result = processor.process_paragraph(visual_text, logical_output=True)
        
        # In logical DOCX output, it must be the 2 distinct logical chars
        assert "\ufefb" not in result['text']
        assert "لا" in result['text']

    def test_nfkc_preserves_diacritics(self):
        """Ensure normalization doesn't strip diacritics when preserving them."""
        processor = ArabicProcessor(preserve_diacritics=True)
        text = "بِسْمِ اللَّهِ"
        result = processor.process_paragraph(text, logical_output=True)
        
        # Diacritics should still be there
        assert "\u0650" in result['text'] # Kasra
        assert "\u0651" in result['text'] # Shadda
        assert "\u064e" in result['text'] # Fatha
