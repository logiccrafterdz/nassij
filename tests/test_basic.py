"""
Proper pytest test suite for Nassij core functionality.
Replaces the old print-based test_basic.py with real assertions.
"""
import pytest
from core.arabic_processor import ArabicProcessor
from utils.unicode_helpers import normalize_nfc, count_diacritics, is_arabic_char
from utils.metrics import validate_ligatures, calculate_cer


class TestArabicProcessor:
    """Tests for the Arabic text processing pipeline."""

    def setup_method(self):
        self.processor = ArabicProcessor(preserve_diacritics=True)

    def test_simple_arabic_detected(self):
        result = self.processor.process_paragraph("مرحبا بك")
        assert result["is_arabic"] is True

    def test_english_not_arabic(self):
        result = self.processor.process_paragraph("Hello world")
        assert result["is_arabic"] is False

    def test_mixed_text_detected_as_arabic(self):
        result = self.processor.process_paragraph("Hello مرحبا بك في النظام")
        assert result["is_arabic"] is True

    def test_diacritics_preserved(self):
        # Use explicit Unicode: ba + kasra + sin + sukun + mim + kasra
        text = "\u0628\u0650\u0633\u0652\u0645\u0650"
        # Test the DOCX output path (logical order) which is where diacritics matter
        result = self.processor.process_paragraph(text, logical_output=True)
        assert result["diacritics_count"] > 0, "Diacritics should be preserved in logical output mode"

    def test_lam_alif_ligature_preserved(self):
        result = self.processor.process_paragraph("لا يوجد", logical_output=True)
        assert "لا" in result["text"]

    def test_allah_ligature_preserved(self):
        result = self.processor.process_paragraph("الله أكبر", logical_output=True)
        assert "الله" in result["text"]

    def test_empty_input(self):
        result = self.processor.process_paragraph("")
        assert result["text"] == ""
        assert result["is_arabic"] is False

    def test_whitespace_only(self):
        result = self.processor.process_paragraph("   ")
        assert result["is_arabic"] is False

    def test_logical_output_mode(self):
        text = "بسم الله الرحمن الرحيم"
        result = self.processor.process_paragraph(text, logical_output=True)
        assert result["text"] is not None
        assert len(result["text"]) > 0


class TestUnicodeHelpers:
    """Tests for Unicode utility functions."""

    def test_nfc_normalization(self):
        text = "أسد"
        normalized = normalize_nfc(text)
        assert normalized is not None
        assert len(normalized) > 0

    def test_diacritics_counting(self):
        assert count_diacritics("أسدٌ") >= 1
        assert count_diacritics("أسد") == 0

    def test_arabic_char_detection(self):
        assert is_arabic_char("ب") is True
        assert is_arabic_char("A") is False
        assert is_arabic_char("5") is False


class TestMetrics:
    """Tests for quality metrics."""

    def test_cer_identical(self):
        cer = calculate_cer("مرحبا بك", "مرحبا بك")
        assert cer == 0.0

    def test_cer_with_error(self):
        cer = calculate_cer("مرحبا بك", "مرحبا ب")
        assert cer > 0.0

    def test_cer_empty_reference(self):
        cer = calculate_cer("", "")
        assert cer == 0.0

    def test_ligature_validation(self):
        ligatures = validate_ligatures("لا يوجد إلا الله")
        assert ligatures["لا"]["found"] is True
        assert ligatures["الله"]["found"] is True
