import fitz
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class NassijScanner:
    """
    Direct character-level extraction scanner (Nassij V3).
    Extracts text preserving font, size, style, and exact reading order without OCR.
    """
    def __init__(self):
        pass

    def scan_page(self, page: fitz.Page) -> List[Dict[str, Any]]:
        """
        Scan a single PyMuPDF page using rawdict and return structured blocks.
        """
        raw_data = page.get_text("rawdict")
        processed_blocks = []

        for block in raw_data.get("blocks", []):
            # Type 0 is text (Type 1 is image)
            if block.get("type") != 0:
                continue
                
            classified_block = self._process_text_block(block)
            if classified_block:
                processed_blocks.append(classified_block)
                
        # Sort blocks top to bottom
        processed_blocks.sort(key=lambda b: b["bbox"][1])
        return processed_blocks

    def _process_text_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a text block: sort lines vertically, sort spans RTL for Arabic, 
        and determine if it's a heading or paragraph.
        """
        lines = block.get("lines", [])
        
        # Sort lines vertically (top to bottom)
        lines.sort(key=lambda l: l["bbox"][1])
        
        processed_spans = []
        is_heading = False
        max_size = 0
        
        for line in lines:
            spans = line.get("spans", [])
            
            # Simple heuristic for RTL sorting of spans: sort by X-coordinate descending
            # This ensures right-most text appears first in the sequence.
            spans.sort(key=lambda s: s["bbox"][0], reverse=True)
            
            for span in spans:
                chars = span.get("chars", [])
                text = "".join([c.get("c", "") for c in chars]).strip()
                if not text:
                    continue
                    
                size = span.get("size", 10.0)
                font = span.get("font", "")
                flags = span.get("flags", 0)
                color = span.get("color", 0)
                
                # Check formatting flags
                is_bold = bool(flags & (1 << 4))
                is_italic = bool(flags & (1 << 1))
                
                if size > max_size:
                    max_size = size
                
                processed_spans.append({
                    "text": text,
                    "font": font,
                    "size": size,
                    "is_bold": is_bold,
                    "is_italic": is_italic,
                    "color": color,
                    "bbox": span.get("bbox")
                })
                
        if not processed_spans:
            return None
            
        # Classify based on max size and bold flag
        # Assuming size >= 14pt is a heading (can be tuned)
        if max_size >= 14 or any(s["is_bold"] for s in processed_spans if s["size"] == max_size):
            is_heading = True
            
        # Join text for the whole block for easy access
        full_text = " ".join([s["text"] for s in processed_spans])
        
        return {
            "type": "heading" if is_heading else "paragraph",
            "text": full_text,
            "spans": processed_spans,
            "bbox": block.get("bbox")
        }
