import pytest
from integrity.canonical_hash import canonical_arabic_hash
from integrity.diacritics_splitter import split_diacritics
from integrity.merkle_tree import MerkleTree

def test_canonical_hash_equivalence():
    # 1. Base text
    text1 = "بسم الله"
    
    # 2. Text with Kashida/Tatweel
    text2 = "بـســم اللــــه"
    
    # 3. Text with Zero-Width Joiner
    text3 = "بسم\u200d الله"
    
    # 4. Text using Presentation Forms (e.g., ﷲ for Allah, ﺑ for Ba)
    # ﷲ = U+FDF2
    text4 = "بسم ﷲ"
    
    hash1 = canonical_arabic_hash(text1)
    hash2 = canonical_arabic_hash(text2)
    hash3 = canonical_arabic_hash(text3)
    hash4 = canonical_arabic_hash(text4)
    
    assert hash1 == hash2, "Kashida should be ignored"
    assert hash1 == hash3, "Zero-width joiners should be ignored"
    assert hash1 == hash4, "Presentation forms should be normalized"

def test_diacritics_splitter():
    # النص بتشكيل (Bismillahi)
    text = "بِسْمِ اللَّهِ"
    
    # النص بدون تشكيل (Base text)
    base_text_expected = "بسم الله"
    
    result = split_diacritics(text)
    
    assert result["base_text"] == base_text_expected
    # The canonical hash of the base text should match the hash of "بسم الله"
    assert result["base_hash"] == canonical_arabic_hash(base_text_expected)
    
    # Diacritics should be captured separately
    assert len(result["diacritics_only"]) > 0
    assert result["compound_hash"] != result["base_hash"]

def test_merkle_tree():
    tree = MerkleTree()
    tree.add_leaf("hash1")
    tree.add_leaf("hash2")
    tree.add_leaf("hash3")
    
    root = tree.build()
    assert root is not None
    assert len(root) == 64 # SHA-256 hex length
