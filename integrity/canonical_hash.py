import unicodedata
import hashlib
import regex as re

def canonical_arabic_hash(text: str) -> str:
    """
    يُنتج نفس الهاش لكل التمثيلات الإملائية المتكافئة
    Produces the same hash for all equivalent orthographic representations of Arabic text.
    """
    if not text:
        return hashlib.sha256(b"").hexdigest()
        
    # 1. NFKC: يفك Presentation Forms إلى أحرف أساسية
    # Converts Presentation Forms (like ﻼ) to base characters (ل + ا)
    text = unicodedata.normalize('NFKC', text)
    
    # 2. إزالة Kashida (التطويل ـ)
    # Remove Tatweel/Kashida which is purely visual
    text = text.replace('\u0640', '')
    
    # 3. إزالة Zero-Width characters
    # Remove hidden layout control characters
    text = re.sub(r'[\u200b\u200c\u200d\u200e\u200f\ufeff]', '', text)
    
    # 4. NFC النهائي
    # Final normalization to ensure consistent byte representation
    text = unicodedata.normalize('NFC', text)
    
    # 5. Hash
    return hashlib.sha256(text.encode('utf-8')).hexdigest()
