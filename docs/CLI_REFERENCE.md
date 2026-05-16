# Nassij CLI Reference

The Nassij Command Line Interface is the primary way to interact with the engine.

## Basic Usage

```bash
nassij convert <input.pdf> -o <output.docx>
```

## Commands

### `convert`
Converts a PDF to a DOCX file.

**Arguments:**
- `input`: Path to the input PDF file.
- `-o`, `--output`: Path to the output DOCX file.
- `--mode`: Conversion mode.
  - `scan`: Direct text extraction (digital natives only).
  - `fast`: Quick OCR / minimal layout processing.
  - `balanced`: Default OCR + layout handling.
  - `accurate`: Forces OCR and deep layout analysis.
  - `legal`: Forces OCR, high DPI (400+), preserves diacritics, and generates cryptographic linguistic proof.
  - `research`: Extracts natively but guarantees proof generation.
- `--preserve-diacritics` (default) / `--no-preserve-diacritics`: Toggle Arabic tashkeel preservation.
- `--font`: Font to apply to Arabic text (default: `Arial`).
- `--dpi`: Rendering resolution for OCR (default: `300`).
- `--proof`: Generates a `.nassij-proof` Merkle Tree file.

### `batch`
Converts multiple PDFs inside a directory.

**Arguments:**
- `input_dir`: Directory containing PDFs.
- `-o`, `--output_dir`: Directory to save generated DOCX files.
- `--mode`: Conversion mode (same as `convert`).
- `--workers`: Number of parallel processing workers (default: `4`).
- `--proof`: Generates a `.nassij-proof` file for every document.

### `verify`
Verifies a generated DOCX against its linguistic proof file.

**Arguments:**
- `docx`: The output DOCX file.
- `--proof`: Path to the `.nassij-proof` JSON file.

**Example:**
```bash
nassij verify output.docx --proof output.docx.nassij-proof
```

### Global Flags
- `--info <file>`: Analyzes a PDF to determine if it's scanned or digital native without converting.
- `--benchmark <file>`: Runs a speed test on the given PDF.
