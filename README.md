# Nassij v2.0

**A High-Accuracy PDF-to-DOCX Converter Specialized for Arabic Language**

---

## Overview

**Nassij** is a local-first, open-source tool that converts PDF documents (both text-based and scanned) into fully editable `.docx` files with **exceptional fidelity for Arabic content**, including:

- Right-to-left (RTL) text direction
- Arabic ligatures (e.g., "لا", "إلا", "الله")
- Diacritics/tashkeel preservation (e.g., فَتْحَة, ضَمَّة)
- Complex tables (merged cells, mixed Arabic/English, borderless)
- Mixed-script paragraphs (Arabic + Latin)

> **Key Principle**: Never sacrifice linguistic accuracy for speed. If a component fails, degrade gracefully—but never corrupt meaning.

---

## Quick Start

### Installation

1. **Clone or download this repository**

2. **Install using pip**:
   ```bash
   # Install with standard dependencies
   pip install -e .
   
   # Install with PaddleOCR dependencies (recommended for accurate tables)
   pip install -e .[paddle]
   
   # Install dev dependencies
   pip install -e .[dev]
   ```

   > **Note**: PaddleOCR requires additional system dependencies. See [PaddleOCR Installation Guide](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_en/installation_en.md) for details. EasyOCR also requires PyTorch.

3. **Verify installation**:
   ```bash
   nassij --help
   # Or using python
   python cli.py --help
   ```

### Basic Usage

```bash
# Convert a PDF to DOCX
nassij convert input.pdf -o output.docx

# Get info about a PDF before converting
nassij --info input.pdf

# Benchmark conversion
nassij --benchmark input.pdf -o output.docx

# Use accurate mode for scanned documents
nassij convert input.pdf -o output.docx --mode accurate

# High-resolution OCR for scanned pages
nassij convert input.pdf -o output.docx --dpi 400
```

---

## Command-Line Options

### `convert` Command

| Option | Description | Default |
|--------|-------------|---------|
| `input` | Input PDF file path | *Required* |
| `-o, --output` | Output DOCX file path | *Required* |
| `--mode` | Conversion mode: `fast`, `balanced`, `accurate` | `balanced` |
| `--preserve-diacritics` | Preserve Arabic diacritics (tashkeel) | `True` |
| `--font` | Font name for Arabic text | `Arial` |
| `--dpi` | DPI for scanned page conversion | `300` |

### Global Options

| Option | Description |
|--------|-------------|
| `--info` | Analyze PDF and report type (Scanned, Hybrid, Native) |
| `--benchmark` | Run conversion and report time elapsed |

### Conversion Modes

- **`fast`**: Text extraction only, skips scanned pages
- **`balanced`**: Text extraction + OCR for scanned pages (uses EasyOCR/PaddleOCR)
- **`accurate`**: Full OCR processing with table detection and Image Preprocessing

---

## Architecture

```text
nassij/
├── core/
│   ├── pdf_reader.py          # Extract raw text + coords from PDF
│   ├── image_preprocessor.py  # Deskew, Denoise, and Adaptive Binarization
│   ├── engines/               # Strategy pattern for OCR
│   │   ├── base_engine.py     # Base abstract class
│   │   ├── easyocr_engine.py  # EasyOCR implementation
│   │   └── paddle_engine.py   # PaddleOCR implementation (Text + Tables)
│   ├── arabic_processor.py    # Ligatures + diacritics + RTL
│   ├── table_handler.py       # Reconstruct tables from OCR boxes
│   ├── layout_processor.py    # Block grouping and column detection
│   └── docx_builder.py        # Generate RTL-compliant DOCX
├── utils/
│   ├── unicode_helpers.py     # NFC normalization, diacritic regex
│   └── metrics.py             # CER, WER, diacritics rate, ligature check
├── cli.py                     # Command-line interface
├── pyproject.toml             # Modern package config
└── README.md                  # This file
```

---

## Key Features

### 1. Arabic Text Processing

Nassij uses a **strict, non-negotiable order** for Arabic text processing:

1. Unicode NFC normalization (MUST be first)
2. Bidi direction correction (`get_display`)
3. Arabic reshaping (ligatures + connections)
4. Final NFC normalization (after reshaping)

This ensures:
- Correct ligature formation ("لا", "إلا", "الله")
- Proper RTL rendering in Microsoft Word
- Diacritics preservation (>=90% target)

### 2. OCR Engine

- **PaddleOCR PP-OCRv5**: Best open-source Arabic OCR model (2025)
- **PP-TableMagic**: Integrated table detection and reconstruction
- **Offline-first**: No internet required at runtime

### 3. RTL-Compliant DOCX

- XML-level RTL enforcement (compatible with Microsoft Word)
- Right-aligned paragraphs for Arabic text
- Proper font configuration for RTL rendering

### 4. Table Support

- Automatic table detection from OCR
- Merged cell support (heuristic-based)
- Mixed Arabic/English cell content
- Borderless table handling

---

## Quality Metrics

Nassij implements comprehensive quality metrics:

| Metric | Target | Description |
|-------|--------|-------------|
| **CER** | < 0.08 | Character Error Rate (Levenshtein distance) |
| **WER** | < 0.20 | Word Error Rate |
| **Diacritics Preservation** | ≥ 90% | Tashkeel marks preserved |
| **Ligature Accuracy** | 100% | Known ligatures unchanged |
| **Table Cell Accuracy** | ≥ 90% | Cell count & content accuracy |

---

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=core --cov=utils
```

### Test Cases

Create a test PDF with:
- Arabic text with ligatures: "لا", "أسدٌ"
- Diacritics: "فَتْحَة", "ضَمَّة"
- Simple table with Arabic content
- Mixed Arabic/English paragraphs

Run conversion and verify:
- Text renders correctly in Microsoft Word (RTL, connected letters)
- Text is editable (not images)
- Table structure is preserved
- CER <= 8% on clean scans

---

## Constraints

- **No internet required** at runtime (offline-first)
- **No cloud dependencies**
- **All processing must preserve original meaning**—never "guess" broken text
- **Unicode NFC normalization is mandatory** on all text inputs

---

## Technical Stack

| Component | Technology | Why |
|---------|-----------|-----|
| **PDF Parsing** | `PyMuPDF` (`fitz`) | Best coordinate-aware text extraction; handles embedded fonts |
| **OCR Engine** | `PaddleOCR` (PP-OCRv5 + PP-TableMagic) | Only open-source engine with integrated table detection + Arabic support |
| **Arabic Text Processing** | `python-bidi` + `arabic-reshaper` + `unicodedata` | Mandatory trio for RTL + ligatures + Unicode normalization |
| **DOCX Generation** | `python-docx` | Full control over paragraph properties, fonts, and RTL via XML |
| **Language Detection** | `polyglot` (fallback: `langdetect`) | Accurate per-paragraph script detection |

> ❌ **Do NOT use**: Tesseract, Camelot, pdf2image alone, or any tool without explicit Arabic RTL support.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Please ensure:
- All Arabic text processing follows the strict order (see `arabic_processor.py`)
- Tests pass with quality metrics within targets
- RTL rendering is verified in Microsoft Word

---


## Arabic Version / النسخة العربية

**نسيج** هو أداة مفتوحة المصدر لتحويل ملفات PDF إلى DOCX مع دقة عالية للمحتوى العربي.

### المميزات الرئيسية:
- دعم كامل للنص العربي من اليمين لليسار (RTL)
- الحفاظ على الروابط العربية (لا، إلا، الله)
- الحفاظ على التشكيل (الفتحة، الضمة، الكسرة)
- دعم الجداول المعقدة
- دعم النصوص المختلطة (عربي + إنجليزي)

### الاستخدام:
```bash
python cli.py convert input.pdf -o output.docx
```

---

**Version**: 1.0  
**Last Updated**: 2025

