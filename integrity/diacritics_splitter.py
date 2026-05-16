import regex as re
import hashlib
from .canonical_hash import canonical_arabic_hash

def split_diacritics(text: str, block_index: int = -1) -> dict:
    """
    يفصل التشكيل عن النص الأساسي ويحسب الهاش لكل منهما
    Splits diacritics from base text and calculates hashes independently.
    If block_index is provided, it's used to bind the hash to its position.
    """
    if not text:
        empty_hash = hashlib.sha256(b"").hexdigest()
        compound_input = f"{block_index}:{empty_hash}:{empty_hash}" if block_index >= 0 else empty_hash + empty_hash
        return {
            "base_text": "",
            "diacritics_only": "",
            "base_hash": empty_hash,
            "diacritics_hash": empty_hash,
            "compound_hash": hashlib.sha256(compound_input.encode('utf-8')).hexdigest()
        }

    # نطاق التشكيل العربي (Arabic Diacritics Range)
    # \u064b to \u065f covers Fathatan to Wavy Hamza Below
    # \u0670 is Superscript Alif (Maddah)
    diacritics_pattern = r'[\u064b-\u065f\u0670]'
    
    # النص الأساسي (بدون تشكيل)
    base_text = re.sub(diacritics_pattern, '', text)
    
    # التشكيل فقط
    diacritics_only = "".join(re.findall(diacritics_pattern, text))
    
    base_hash = canonical_arabic_hash(base_text)
    diacritics_hash = hashlib.sha256(diacritics_only.encode('utf-8')).hexdigest()
    
    # الهاش المركب (Compound Hash)
    combined = f"{block_index}:{base_hash}:{diacritics_hash}" if block_index >= 0 else base_hash + diacritics_hash
    compound_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
    
    return {
        "base_text": base_text,
        "diacritics_only": diacritics_only,
        "base_hash": base_hash,
        "diacritics_hash": diacritics_hash,
        "compound_hash": compound_hash
    }
