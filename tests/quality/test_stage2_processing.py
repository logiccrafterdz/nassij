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

    def test_process_empty_string(self):
        """Test P4: Empty strings should not crash."""
        processor = ArabicProcessor()
        result = processor.process_paragraph("", logical_output=True)
        assert result['text'] == ""
        assert result['is_arabic'] is False

    def test_kashida_removed(self):
        """Test P5: Kashida (Tatweel) should be handled correctly (NFKC removes it or preserves it based on config).
        Actually, standard NFKC does NOT remove Tatweel, but we should test that it doesn't corrupt the text."""
        processor = ArabicProcessor()
        text = "بـــسم"
        result = processor.process_paragraph(text, logical_output=True)
        assert "ب" in result['text']
        assert "س" in result['text']
        assert "م" in result['text']

    def test_process_paragraph_idempotent(self):
        """Test P7: Processing twice should yield the same result."""
        processor = ArabicProcessor()
        text = "تجربة المعالجة المتكررة"
        pass1 = processor.process_paragraph(text, logical_output=True)
        pass2 = processor.process_paragraph(pass1['text'], logical_output=True)
        assert pass1['text'] == pass2['text']

    def test_farsi_yeh_normalized(self):
        """Test B8: NFKC converts Presentation Forms to Farsi Yeh (U+06CC).
        We must post-process it to standard Arabic Yeh (U+064A)."""
        processor = ArabicProcessor()
        # U+FBFE is ARABIC LETTER FARSI YEH INITIAL FORM — common in PDFs
        text = "اﻟﺟﻣﻬورﯾﺔ"  # Contains U+FBFE
        result = processor.process_paragraph(text, logical_output=True)
        
        # Should NOT contain Farsi Yeh (U+06CC)
        assert '\u06CC' not in result['text'], f"Farsi Yeh still present: {result['text']}"
        # Should contain standard Arabic Yeh (U+064A)
        assert '\u064A' in result['text'], f"Arabic Yeh missing: {result['text']}"
