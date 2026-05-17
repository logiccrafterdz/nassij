"""Deep analysis of the Arabic text corruption in NFKC normalization."""
import unicodedata

text_raw = 'اﻟﺟﻣﻬورﯾﺔ اﻟﺟزاﺋرﯾﺔ اﻟدﯾﻣﻘراطﯾﺔ اﻟﺷﻌﺑﯾﺔ'
text_processed = unicodedata.normalize('NFKC', text_raw)

print('=== RAW PDF TEXT: Character-by-character analysis ===')
print(f'  Raw: {text_raw}')
print(f'  Len: {len(text_raw)}')
for i, c in enumerate(text_raw[:30]):
    name = unicodedata.name(c, '?')
    print(f'  [{i}] U+{ord(c):04X} = {c} ({name})')

print()
print('=== AFTER NFKC: Character-by-character analysis ===')
print(f'  NFKC: {text_processed}')
print(f'  Len:  {len(text_processed)}')
for i, c in enumerate(text_processed[:30]):
    name = unicodedata.name(c, '?')
    print(f'  [{i}] U+{ord(c):04X} = {c} ({name})')

print()
print('=== KEY ISSUES FOUND ===')

# Issue 1: Farsi Yeh
yeh_test = chr(0xFBFE) 
yeh_nfkc = unicodedata.normalize('NFKC', yeh_test)
print(f'  1. NFKC(U+FBFE) = U+{ord(yeh_nfkc):04X} ({unicodedata.name(yeh_nfkc)})')
print(f'     This is FARSI YEH, not ARABIC YEH (U+064A)')
print(f'     In standard Arabic, we MUST use U+064A (ي)')

# Issue 2: CER inflated by presentation form → base char differences
from utils.metrics import calculate_cer
cer = calculate_cer(text_raw, text_processed)
print(f'  2. CER between raw and NFKC processed: {cer:.2%}')
print(f'     This is HIGH because each presentation form char differs from its base.')
print(f'     The CER metric sees U+FEDF (ﻟ) ≠ U+0644 (ل) as an error.')
print(f'     But the ACTUAL text meaning is identical!')

# Issue 3: What about the spaces?
import re
# Count multi-line spans
raw_words = text_raw.split()
processed_words = text_processed.split()
print(f'  3. Raw words: {len(raw_words)}, Processed words: {len(processed_words)}')
print(f'     Raw:       {raw_words}')
print(f'     Processed: {processed_words}')
