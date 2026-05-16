import pytest
from core.arabic_processor import ArabicProcessor
from core.ligature_processor import LigatureProcessor

def test_arabic_processor_initialization():
    processor = ArabicProcessor()
    assert processor is not None

def test_arabic_script_detection():
    processor = ArabicProcessor()
    assert processor.is_arabic_text("مرحبا بك") == True
    assert processor.is_arabic_text("Hello World") == False
    assert processor.is_arabic_text("مرحبا Hello") == True  # Mixed, but has Arabic
    assert processor.is_arabic_text("12345") == False

def test_process_paragraph_logical_output():
    processor = ArabicProcessor()
    text = "مرحبا بك في Nassij"
    result = processor.process_paragraph(text, logical_output=True)
    
    assert result['is_arabic'] == True
    assert "مرحبا" in result['text']
    assert "Nassij" in result['text']

def test_process_paragraph_visual_output():
    processor = ArabicProcessor()
    text = "مرحبا"
    result = processor.process_paragraph(text, logical_output=False)
    
    # Should be reshaped and bidi-processed
    assert result['is_arabic'] == True
    # The first character in visual string should be the last character in logical string (Alef)
    # Actually, bidi algorithm handles this.
    assert len(result['text']) == len(text)

def test_diacritics_preservation():
    processor = ArabicProcessor(preserve_diacritics=True)
    text = "مَرْحَباً"
    result = processor.process_paragraph(text, logical_output=True)
    assert "َ" in result['text']  # Fatha should be preserved

def test_diacritics_removal():
    processor = ArabicProcessor(preserve_diacritics=False)
    text = "مَرْحَباً"
    result = processor.process_paragraph(text, logical_output=True)
    assert "َ" not in result['text']  # Fatha should be removed

def test_ligature_validation():
    processor = LigatureProcessor()
    text = "سلام الله عليكم لا إله إلا الله"
    result = processor.check_ligatures(text)
    
    assert result['has_ligatures'] == False # In plain string, these are usually logical.
    
    # Let's test with actual visual ligatures
    visual_text = "\ufefb" # LAM WITH ALEF ISOLATED
    result_visual = processor.check_ligatures(visual_text)
    assert result_visual['has_ligatures'] == True
    assert "لا" in result_visual['ligatures_found']
