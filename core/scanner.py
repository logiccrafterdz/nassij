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
        Also detects tables using PyMuPDF's built-in table finder.
        """
        # --- Table Detection ---
        table_bboxes = []
        table_blocks = []
        try:
            tabs = page.find_tables()
            for tab in tabs:
                table_bboxes.append(tab.bbox)
                cells = tab.extract()
                table_blocks.append({
                    "type": "table",
                    "text": "\n".join([" | ".join([str(c) if c else "" for c in row]) for row in cells]),
                    "cells": cells,
                    "bbox": tab.bbox,
                    "spans": []
                })
        except Exception:
            pass  # find_tables may not be available in all PyMuPDF versions

        def _is_inside_table(block_bbox):
            """Check if a text block falls inside any detected table."""
            for t_bbox in table_bboxes:
                if (block_bbox[0] >= t_bbox[0] - 5 and block_bbox[1] >= t_bbox[1] - 5 and
                    block_bbox[2] <= t_bbox[2] + 5 and block_bbox[3] <= t_bbox[3] + 5):
                    return True
            return False

        # --- Text Block Extraction ---
        raw_data = page.get_text("rawdict")
        processed_blocks = []

        for block in raw_data.get("blocks", []):
            # Type 0 is text (Type 1 is image)
            if block.get("type") != 0:
                continue
            
            # Skip text blocks that fall inside detected tables
            if table_bboxes and _is_inside_table(block.get("bbox", [0,0,0,0])):
                continue
                
            classified_block = self._process_text_block(block)
            if classified_block:
                processed_blocks.append(classified_block)
        
        # Merge text and table blocks, sort top to bottom
        all_blocks = processed_blocks + table_blocks
        all_blocks.sort(key=lambda b: b["bbox"][1])
        return all_blocks

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
            
            # Do not blindly sort spans by X-coordinate (Bug B1).
            # Modern PDFs store text in logical stream order. ArabicProcessor will handle bidi later.
            
            for span in spans:
                chars = span.get("chars", [])
                
                span_bbox = span.get("bbox", [0, 0, 0, 0])
                fixed_chars = []
                for c in chars:
                    fixed_chars.append(c.get("c", ""))
                
                text = "".join(fixed_chars).strip()
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
                    "bbox": span.get("bbox"),
                    "line_idx": lines.index(line)  # Keep track of which line this span belongs to
                })
                
        if not processed_spans:
            return None
            
        # Classify based on max size and bold flag
        # Assuming size >= 14pt is a heading (can be tuned)
        if max_size >= 14 or any(s["is_bold"] for s in processed_spans if s["size"] == max_size):
            is_heading = True
            
        # Reconstruct text preserving lines (Bug B2)
        lines_text = []
        current_line_idx = -1
        current_line_spans = []
        
        for s in processed_spans:
            if s["line_idx"] != current_line_idx:
                if current_line_spans:
                    lines_text.append(" ".join(current_line_spans))
                current_line_spans = []
                current_line_idx = s["line_idx"]
            current_line_spans.append(s["text"])
            
        if current_line_spans:
            lines_text.append(" ".join(current_line_spans))
            
        full_text = "\n".join(lines_text)
        
        return {
            "type": "heading" if is_heading else "paragraph",
            "text": full_text,
            "spans": processed_spans,
            "bbox": block.get("bbox")
        }
