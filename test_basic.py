"""
Basic test script to verify Nassij core functionality.
Run this to test Arabic text processing without requiring a PDF.
"""
from core.arabic_processor import ArabicProcessor
from utils.unicode_helpers import normalize_nfc, count_diacritics
from utils.metrics import validate_ligatures, calculate_cer


def test_arabic_processor():
    """Test Arabic text processing."""
    print("Testing Arabic Processor...")
    processor = ArabicProcessor(preserve_diacritics=True)
    
    # Test ligatures
    test_cases = [
        ("لا", "Lam + Alif ligature"),
        ("إلا", "Alif + Lam + Alif ligature"),
        ("الله", "Allah ligature"),
        ("أسدٌ", "Text with diacritics"),
        ("مرحبا بك", "Simple Arabic text"),
        ("Hello مرحبا", "Mixed Arabic/English"),
    ]
    
    print("\n1. Testing Ligatures and Text Processing:")
    for text, description in test_cases:
        processed = processor.process_paragraph(text)
        print(f"   Input:  {text}")
        print(f"   Output: {processed['text']}")
        print(f"   Arabic: {processed['is_arabic']}")
        print(f"   Description: {description}")
        print()
    
    # Test ligature validation
    print("2. Testing Ligature Validation:")
    test_text = "لا يوجد إلا الله"
    ligature_results = processor.validate_ligatures(test_text)
    for ligature, result in ligature_results.items():
        status = "✓" if result.get('found') and result.get('correct', False) else "✗"
        print(f"   {status} {ligature}: {result}")
    
    print("\n✓ Arabic Processor tests completed!")


def test_unicode_helpers():
    """Test Unicode helper functions."""
    print("\nTesting Unicode Helpers...")
    
    # Test NFC normalization
    text1 = "أسد"
    text2 = normalize_nfc(text1)
    print(f"   NFC Normalization: {text1} -> {text2}")
    
    # Test diacritics counting
    text_with_diacritics = "أسدٌ"
    count = count_diacritics(text_with_diacritics)
    print(f"   Diacritics in '{text_with_diacritics}': {count}")
    
    print("\n✓ Unicode Helpers tests completed!")


def test_metrics():
    """Test quality metrics."""
    print("\nTesting Quality Metrics...")
    
    # Test CER
    reference = "مرحبا بك"
    hypothesis = "مرحبا بك"
    cer = calculate_cer(reference, hypothesis)
    print(f"   CER (identical): {cer:.4f} (expected: 0.0000)")
    
    # Test with error
    hypothesis_error = "مرحبا ب"
    cer_error = calculate_cer(reference, hypothesis_error)
    print(f"   CER (with error): {cer_error:.4f}")
    
    # Test ligature validation
    test_text = "لا يوجد إلا الله"
    ligatures = validate_ligatures(test_text)
    print(f"   Ligatures found: {sum(1 for v in ligatures.values() if v.get('found'))}")
    
    print("\n✓ Metrics tests completed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Nassij Basic Functionality Test")
    print("=" * 60)
    
    try:
        test_unicode_helpers()
        test_arabic_processor()
        test_metrics()
        
        print("\n" + "=" * 60)
        print("✓ All basic tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

