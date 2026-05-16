# Nassij V3 Architecture

Nassij V3 is a highly modular, linguistic-first PDF-to-DOCX converter designed specifically for Arabic and right-to-left (RTL) scripts. 

## Core Modules

### 1. `core/pdf_reader.py`
Handles PDF parsing using `PyMuPDF` (fitz). Extracts digital native text or rasterizes scanned pages for OCR. Uses local heuristics to determine if a page is scanned vs digital.

### 2. `core/scanner.py` (`NassijScanner`)
For digital-native PDFs, extracts text span by span. Employs advanced Arabic ligature correction algorithms (e.g., Lam-Alif zero-width fixes).

### 3. `core/ocr_engine.py`
A Facade pattern that bridges to available OCR engines:
- **Surya OCR** (Primary): High-accuracy, modern ML-based layout and text extraction.
- **EasyOCR** (Fallback 1): Reliable deep-learning OCR.
- **PaddleOCR** (Fallback 2): Excellent multilingual layout support.

### 4. `core/arabic_processor.py` & `core/ligature_processor.py`
Manages logical-to-visual script transitions. Handles Unicode normalization, diacritics extraction, and bidirectional algorithm integration.

### 5. `core/docx_builder.py` & `core/table_handler.py` & `core/rtl_helpers.py`
Constructs OpenXML strictly adhering to Microsoft Word's RTL (`w:bidi`, `w:rtl`) requirements. `rtl_helpers.py` provides shared DOM injection logic to eliminate visual alignment bugs.

### 6. `integrity/`
Implements a Cryptographic Linguistic Proof system using Merkle Trees. 
It hashes logical text and diacritics independently (`diacritics_splitter.py`), allowing downstream verifiers to detect tampering.

## Data Flow Pipeline

1. **Input Stage:** `cli.py` / `web/app.py` accepts PDF and mode.
2. **Analysis Stage:** `pdf_reader.py` evaluates PDF type.
3. **Extraction Stage:** Uses `scanner.py` (digital) or `ocr_engine.py` (scanned).
4. **Processing Stage:** Text blocks are cleaned by `arabic_processor.py`.
5. **Assembly Stage:** Blocks are written to `.docx` via `docx_builder.py`.
6. **Integrity Stage:** (Optional) Text blocks are bound to a Merkle tree in `proof.py`.
