"""
PDF reading module using PyMuPDF (fitz).
Handles both text-based and scanned PDFs.
"""
import fitz  # PyMuPDF
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import io
from PIL import Image

from utils.unicode_helpers import is_likely_reversed_arabic, is_arabic_char


class PDFReader:
    """
    Reads PDF files and extracts text or converts pages to images for OCR.
    """
    
    def __init__(self, pdf_path: str):
        """
        Initialize PDF reader.
        
        Args:
            pdf_path: Path to PDF file
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        self.doc = fitz.open(str(self.pdf_path))
        self.page_count = len(self.doc)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the PDF document."""
        if hasattr(self, 'doc') and self.doc:
            self.doc.close()
    
    def get_page_count(self) -> int:
        """Get total number of pages."""
        return self.page_count
    
    def _sort_and_group_blocks(self, text_blocks: List[Dict]) -> List[Dict]:
        """
        Sort and group extracted text blocks by lines (Y-axis clustering) and RTL (X-axis desc).
        """
        if not text_blocks:
            return []
            
        # Group blocks by lines with tolerance
        lines = []
        
        # Sort by Y strictly first
        text_blocks.sort(key=lambda x: x["bbox"][1])
        
        if not text_blocks:
            return []
            
        # Cluster blocks into lines
        clustered_lines = []
        if text_blocks:
            current_line = [text_blocks[0]]
            current_y = text_blocks[0]["bbox"][1]
            
            for block in text_blocks[1:]:
                # Increased tolerance to 15pts to handle different fonts/alignments on same line
                # Also check if they overlap significantly in Y axis
                b_y_min, b_y_max = block["bbox"][1], block["bbox"][3]
                c_y_min, c_y_max = current_y, current_y + 12 # Estimate height
                
                # Check for overlap or small distance
                y_dist = abs(b_y_min - current_y)
                if y_dist < 15:
                    current_line.append(block)
                else:
                    clustered_lines.append(current_line)
                    current_line = [block]
                    current_y = b_y_min
            clustered_lines.append(current_line)
            
        # Process each line
        for line in clustered_lines:
            # Sort blocks within line
            # Heuristic: If line is primarily Arabic, sort RTL (descending X)
            # Otherwise sort LTR (ascending X)
            arabic_count = sum(1 for b in line if any(is_arabic_char(c) for c in b.get('text', '')))
            # Lower threshold for Arabic detection in mixed lines
            is_primarily_arabic = (arabic_count / len(line)) > 0.3 if line else False
            
            if is_primarily_arabic:
                # For Arabic lines, we want the rightmost block to be FIRST in the logical list
                # because we are converting to a format that handles RTL display (Word).
                # Logical order for "تم إنشاء هذا المستند بواسطة Nassij" is 
                # [تم...] then [Nassij]. In PDF, [تم...] is on the right (higher X).
                line.sort(key=lambda x: x["bbox"][0], reverse=True)
            else:
                line.sort(key=lambda x: x["bbox"][0])
            
            lines.extend(line)
                
        return lines

    def _detect_tables(self, sorted_blocks: List[Dict]) -> List[Dict]:
        """
        Heuristic to detect if a set of blocks forms a table.
        Groups blocks into 'table' types if they share Y coordinates and have gaps.
        """
        if not sorted_blocks:
            return []
            
        # Group by lines with tolerance
        lines = []
        if sorted_blocks:
            current_line = [sorted_blocks[0]]
            current_y = sorted_blocks[0]["bbox"][1]
            for block in sorted_blocks[1:]:
                # Check for overlap or small distance in Y
                if abs(block["bbox"][1] - current_y) < 12:
                    current_line.append(block)
                else:
                    lines.append(current_line)
                    current_line = [block]
                    current_y = block["bbox"][1]
            lines.append(current_line)
            
        processed_blocks = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # A line is a table row candidate if it has multiple blocks separated by horizontal gaps
            # OR if it aligns with previous/next table rows
            is_table_row = len(line) > 1
            
            if is_table_row:
                # Look ahead to see if subsequent lines also have multiple blocks
                # or if they align with this row's columns
                table_rows = [line]
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    # Heuristic: next line is part of table if it has multiple blocks
                    # OR if it's a single block that aligns with one of the columns
                    if len(next_line) > 1:
                        table_rows.append(next_line)
                        j += 1
                    else:
                        # Could be a single-column row in a multi-column table (merged cell)
                        # For now, let's stick to simple multi-block rows
                        break
                
                if len(table_rows) >= 2:
                    # We found a potential table!
                    table_cells = []
                    
                    # Determine table-wide column boundaries (x-coordinates)
                    # This helps in aligning cells that might be slightly shifted
                    col_boundaries = []
                    for row in table_rows:
                        for b in row:
                            col_boundaries.append((b["bbox"][0], b["bbox"][2]))
                    
                    # Sort boundaries by x0
                    col_boundaries.sort()
                    
                    # Construct table data
                    for row in table_rows:
                        # Determine if row is primarily Arabic
                        arabic_count = sum(1 for b in row if any(is_arabic_char(c) for c in b.get('text', '')))
                        is_arabic_row = (arabic_count / len(row)) > 0.3 if row else False
                        
                        # Sort row by X (descending for Arabic, ascending otherwise)
                        if is_arabic_row:
                            row.sort(key=lambda x: x["bbox"][0], reverse=True)
                        else:
                            row.sort(key=lambda x: x["bbox"][0])
                        
                        table_cells.append([b.get('text', '') for b in row])
                    
                    # Create a combined bbox for the table
                    x0 = min(b["bbox"][0] for row in table_rows for b in row)
                    y0 = min(b["bbox"][1] for row in table_rows for b in row)
                    x1 = max(b["bbox"][2] for row in table_rows for b in row)
                    y1 = max(b["bbox"][3] for row in table_rows for b in row)
                    
                    processed_blocks.append({
                        'type': 'table',
                        'bbox': (x0, y0, x1, y1),
                        'cells': table_cells,
                        'is_arabic': any(sum(1 for c in str(cell) if is_arabic_char(c)) > 0 for row in table_cells for cell in row)
                    })
                    i = j # Skip the lines we just processed
                else:
                    processed_blocks.extend(line)
                    i += 1
            else:
                processed_blocks.extend(line)
                i += 1
                
        return processed_blocks

    def _is_text_mangled(self, text: str) -> bool:
        """
        Check if text is likely corrupted/mangled (mojibake).
        Heuristic: High percentage of replacement characters or non-printable chars.
        """
        if not text:
            return False
            
        # Count replacement characters or suspicious patterns
        bad_chars = text.count('\ufffd') # Replacement char
        
        # Check for non-printable characters (excluding common whitespace)
        total_len = len(text)
        if total_len == 0:
            return False
            
        unprintable = sum(1 for c in text if not c.isprintable() and c not in ('\n', '\r', '\t'))
        
        # Also check for lack of common Arabic/Latin characters if the text is long enough
        arabic_ratio = sum(1 for c in text if is_arabic_char(c)) / total_len if total_len > 0 else 0
        
        # If text is long but has very few printable/arabic/latin chars, it might be mangled
        if total_len > 100 and (bad_chars / total_len > 0.1 or unprintable / total_len > 0.2):
            return True
            
        return False

    def extract_text_from_page(self, page_num: int) -> Dict:
        """
        Extract text from a specific page using PyMuPDF's text extraction.
        
        Args:
            page_num: Page number (0-indexed)
            
        Returns:
            Dictionary with extraction results and 'is_scanned' flag
        """
        if page_num < 0 or page_num >= self.page_count:
            raise ValueError(f"Page number {page_num} out of range")
        
        page = self.doc[page_num]
        
        # Try to extract tables using fitz's built-in table finder (if available)
        tables_found = []
        try:
            tabs = page.find_tables()
            for tab in tabs:
                table_data = {
                    'type': 'table',
                    'bbox': tab.bbox,
                    'cells': tab.extract()
                }
                tables_found.append(table_data)
        except Exception:
            pass # Tables finder might not be available in all fitz versions
        
        # Extract raw blocks
        raw_blocks = page.get_text("dict")["blocks"]
        text_blocks = []
        
        # Filter out blocks that are inside tables to avoid duplication
        # Use a slightly larger margin (5pts) for better intersection detection
        def is_inside_table(bbox):
            for tab in tables_found:
                t_bbox = tab['bbox']
                if (bbox[0] >= t_bbox[0] - 5 and bbox[1] >= t_bbox[1] - 5 and 
                    bbox[2] <= t_bbox[2] + 5 and bbox[3] <= t_bbox[3] + 5):
                    return True
            return False

        for block in raw_blocks:
            if block.get('type') == 0 and "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            if not is_inside_table(span["bbox"]):
                                text_blocks.append({
                                    "text": text,
                                    "bbox": span["bbox"],
                                    "font": span.get("font", ""),
                                    "size": span.get("size", 0),
                                    'type': 'text'
                                })
        
        # Apply sorting/grouping to non-table text
        sorted_text_blocks = self._sort_and_group_blocks(text_blocks)
        
        # Heuristic table detection for blocks that fitz might have missed
        # Only run if text_blocks is not empty
        refined_blocks = self._detect_tables(sorted_text_blocks)
        
        # Merge tables and text blocks into final list, sorted by Y
        final_blocks = refined_blocks + tables_found
        final_blocks.sort(key=lambda x: x["bbox"][1])
        
        # Reconstruct full text for metadata/fallback
        full_text_list = []
        for b in final_blocks:
            if b['type'] == 'text':
                full_text_list.append(b['text'])
            elif b['type'] == 'table':
                # Convert table to text representation
                table_text = "\n".join([" | ".join([str(c) if c else "" for c in row]) for row in b['cells']])
                full_text_list.append(table_text)
                
        full_text = "\n".join(full_text_list)
        
        # Scan/Mangle detection
        raw_text_dump = page.get_text()
        text_len = len(raw_text_dump.strip())
        is_mangled = self._is_text_mangled(full_text)
        is_scanned = (text_len < 50 and not tables_found) or is_mangled
        
        return {
            'text': full_text,
            'blocks': final_blocks,
            'is_scanned': is_scanned,
            'is_mangled': is_mangled,
            'page_num': page_num
        }

    
    def convert_page_to_image(self, page_num: int, dpi: int = 300) -> Image.Image:
        """
        Convert a PDF page to a PIL Image for OCR processing.
        
        Args:
            page_num: Page number (0-indexed)
            dpi: Resolution for image conversion (default: 300)
            
        Returns:
            PIL Image object
        """
        if page_num < 0 or page_num >= self.page_count:
            raise ValueError(f"Page number {page_num} out of range (0-{self.page_count-1})")
        
        page = self.doc[page_num]
        
        # Calculate zoom factor for desired DPI
        # PyMuPDF default is 72 DPI
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        
        # Render page to pixmap
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        return img
    
    def save_page_as_image(self, page_num: int, output_path: str, dpi: int = 300) -> str:
        """
        Save a PDF page as an image file.
        
        Args:
            page_num: Page number (0-indexed)
            output_path: Path to save image
            dpi: Resolution for image conversion
            
        Returns:
            Path to saved image file
        """
        img = self.convert_page_to_image(page_num, dpi)
        img.save(output_path, 'PNG', dpi=(dpi, dpi))
        return output_path
    
    def extract_all_pages(self, mode: str = 'balanced') -> List[Dict]:
        """
        Extract text from all pages.
        
        Args:
            mode: Extraction mode ('fast', 'balanced', 'accurate')
                - 'fast': Text extraction only, skip scanned pages
                - 'balanced': Text extraction + detect scanned pages
                - 'accurate': Full extraction with image conversion ready
        
        Returns:
            List of page extraction results
        """
        results = []
        
        for page_num in range(self.page_count):
            page_data = self.extract_text_from_page(page_num)
            
            if mode == 'fast' and page_data['is_scanned']:
                # Skip scanned pages in fast mode
                page_data['text'] = ''
                page_data['blocks'] = []
            
            results.append(page_data)
        
        return results
    
    def get_page_dimensions(self, page_num: int) -> Tuple[float, float]:
        """
        Get page dimensions in points.
        
        Args:
            page_num: Page number (0-indexed)
            
        Returns:
            Tuple of (width, height) in points
        """
        if page_num < 0 or page_num >= self.page_count:
            raise ValueError(f"Page number {page_num} out of range")
        
        page = self.doc[page_num]
        rect = page.rect
        return (rect.width, rect.height)

