"""
Command-line interface for Nassij PDF-to-DOCX converter.
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

from core.pdf_reader import PDFReader
from core.ocr_engine import PaddleOCREngine
from core.docx_builder import DOCXBuilder
from utils.metrics import calculate_all_metrics


def convert_pdf_to_docx(
    input_pdf: str,
    output_docx: str,
    mode: str = 'balanced',
    preserve_diacritics: bool = True,
    font_name: str = 'Arial',
    dpi: int = 300
) -> bool:
    """
    Convert PDF to DOCX with Arabic support.
    
    Args:
        input_pdf: Path to input PDF file
        output_docx: Path to output DOCX file
        mode: Conversion mode ('fast', 'balanced', 'accurate')
        preserve_diacritics: Whether to preserve Arabic diacritics
        font_name: Font name for Arabic text
        dpi: DPI for scanned page conversion
        
    Returns:
        True if conversion successful, False otherwise
    """
    try:
        print(f"Reading PDF: {input_pdf}")
        
        # Initialize PDF reader
        with PDFReader(input_pdf) as pdf_reader:
            page_count = pdf_reader.get_page_count()
            print(f"Found {page_count} page(s)")
            
            # Initialize DOCX builder
            docx_builder = DOCXBuilder(
                font_name=font_name,
                preserve_diacritics=preserve_diacritics
            )
            docx_builder.create_document()
            
            # Initialize OCR engine (only if needed)
            ocr_engine = None
            if mode in ('balanced', 'accurate'):
                try:
                    ocr_engine = PaddleOCREngine(lang='ar', use_table=True)
                    print("OCR engine initialized")
                except Exception as e:
                    print(f"Warning: OCR engine initialization failed: {e}")
                    print("Falling back to text extraction only")
                    mode = 'fast'
            
            # Process each page
            for page_num in range(page_count):
                print(f"Processing page {page_num + 1}/{page_count}...")
                
                # Extract text from page
                page_data = pdf_reader.extract_text_from_page(page_num)
                
                # Check if page is scanned OR if accurate mode forces OCR
                # Accurate mode forces OCR to bypass potentially corrupted/visual PDF text extraction
                should_use_ocr = (mode == 'accurate') or (page_data['is_scanned'] and mode != 'fast')
                
                if should_use_ocr:
                    if ocr_engine:
                        reason = "scanned page" if page_data['is_scanned'] else "accurate mode forced"
                        print(f"  Page {page_num + 1} processing using OCR ({reason})...")
                        # Convert page to image
                        page_image = pdf_reader.convert_page_to_image(page_num, dpi=dpi)
                        
                        # Run OCR
                        ocr_result = ocr_engine.extract_from_pil_image(page_image)
                        
                        # Add text blocks
                        if ocr_result['text_blocks']:
                            docx_builder.add_text_blocks(ocr_result['text_blocks'])
                        
                        # Add tables
                        for table_data in ocr_result['tables']:
                            docx_builder.add_table(table_data)
                    else:
                        print(f"  Warning: OCR requested but engine unavailable. Falling back to text.")
                        # Text-based fallback
                        if page_data['text'].strip():
                             if page_data['blocks']:
                                docx_builder.add_text_blocks(page_data['blocks'])
                             else:
                                docx_builder.add_mixed_paragraph(page_data['text'])
                else:
                    # Text-based page
                    if page_data['text'].strip():
                        # Add text blocks
                        if page_data['blocks']:
                            docx_builder.add_text_blocks(page_data['blocks'])
                        else:
                            # Fallback: add full text as paragraph
                            docx_builder.add_mixed_paragraph(page_data['text'])
            
            # Save document
            print(f"Saving DOCX: {output_docx}")
            docx_builder.save(output_docx)
            print("Conversion completed successfully!")
            return True
            
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Nassij: High-accuracy PDF-to-DOCX converter for Arabic content',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nassij convert input.pdf -o output.docx
  nassij convert input.pdf -o output.docx --mode accurate --font "Noto Sans Arabic"
  nassij convert input.pdf -o output.docx --preserve-diacritics --dpi 400
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert PDF to DOCX')
    convert_parser.add_argument('input', type=str, help='Input PDF file path')
    convert_parser.add_argument('-o', '--output', type=str, required=True,
                               help='Output DOCX file path')
    convert_parser.add_argument('--mode', type=str, 
                               choices=['fast', 'balanced', 'accurate'],
                               default='balanced',
                               help='Conversion mode (default: balanced)')
    convert_parser.add_argument('--preserve-diacritics', action='store_true',
                               default=True,
                               help='Preserve Arabic diacritics (tashkeel)')
    convert_parser.add_argument('--no-preserve-diacritics', 
                               dest='preserve_diacritics',
                               action='store_false',
                               help='Do not preserve Arabic diacritics')
    convert_parser.add_argument('--font', type=str, default='Arial',
                               help='Font name for Arabic text (default: Arial)')
    convert_parser.add_argument('--dpi', type=int, default=300,
                               help='DPI for scanned page conversion (default: 300)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'convert':
        # Validate input file
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        
        # Validate output directory
        output_path = Path(args.output)
        output_dir = output_path.parent
        if output_dir and not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Perform conversion
        success = convert_pdf_to_docx(
            input_pdf=str(input_path),
            output_docx=str(output_path),
            mode=args.mode,
            preserve_diacritics=args.preserve_diacritics,
            font_name=args.font,
            dpi=args.dpi
        )
        
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

