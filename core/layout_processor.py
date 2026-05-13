from typing import List, Dict, Any, Tuple
import numpy as np

class LayoutProcessor:
    """
    Advanced layout analysis for Nassij.
    Groups OCR/PDF blocks into logical structures:
    - Paragraphs
    - Tables
    - Columns
    - Titles
    """
    
    def __init__(self, x_tolerance: int = 20, y_tolerance: int = 10):
        self.x_tolerance = x_tolerance
        self.y_tolerance = y_tolerance

    def process_layout(self, blocks: List[Dict]) -> List[Dict]:
        """
        Analyze blocks and return a structured list of regions.
        Each region has a 'type' (text, table, image).
        """
        if not blocks:
            return []
            
        # 0. Virtual Block Splitting (Split blocks that were accidentally merged by OCR)
        blocks = self._split_multicolumn_blocks(blocks)
            
        # 1. Global Direction Detection
        self.direction = self._detect_global_direction(blocks)
        print(f"  [LayoutProcessor] Global Direction Detected: {self.direction}")
            
        # 1. Group by lines
        lines = self._group_by_lines(blocks)
        
        # 2. Identify structural regions
        results = self._detect_tables(lines)
        
        return results

    def _detect_global_direction(self, blocks: List[Dict]) -> str:
        """Determines if the page is primarily RTL or LTR."""
        from utils.unicode_helpers import get_arabic_ratio
        
        # 1. Content bias
        full_text = " ".join([b['text'] for b in blocks])
        arabic_ratio = get_arabic_ratio(full_text)
        
        # 2. Alignment bias (Are blocks clustered on the right?)
        # For a standard A4 (roughly 595 units wide)
        right_weighted = sum(1 for b in blocks if b['bbox'][0] > 300)
        left_weighted = sum(1 for b in blocks if b['bbox'][2] < 300)
        
        if arabic_ratio > 0.4 or right_weighted > left_weighted:
            return "RTL"
        return "LTR"

    def _group_by_lines(self, blocks: List[Dict]) -> List[List[Dict]]:
        """Group blocks into lines using shared Y-intersection."""
        if not blocks:
            return []
            
        # 0. Convert BBox to standard types (avoid numpy.int32 etc)
        for b in blocks:
            b['bbox'] = [float(x) for x in b['bbox']]
            
        # 1. First Pass: Merge very close blocks horizontally (intra-word or intra-phrase)
        blocks = self._merge_horizontal_neighbors(blocks)
            
        # 2. Sort by Top-Y
        sorted_blocks = sorted(blocks, key=lambda b: b['bbox'][1])
        
        lines = []
        if sorted_blocks:
            current_line = [sorted_blocks[0]]
            current_y_mid = (sorted_blocks[0]['bbox'][1] + sorted_blocks[0]['bbox'][3]) / 2
            
            for b in sorted_blocks[1:]:
                b_y_mid = (b['bbox'][1] + b['bbox'][3]) / 2
                height = b['bbox'][3] - b['bbox'][1]
                tol = max(self.y_tolerance, height * 0.4)
                
                if abs(b_y_mid - current_y_mid) < tol:
                    current_line.append(b)
                else:
                    # Finalize line with script-aware sorting
                    lines.append(self._sort_line_by_script(current_line))
                    current_line = [b]
                    current_y_mid = b_y_mid
            
            lines.append(self._sort_line_by_script(current_line))
        return lines

    def _sort_line_by_script(self, line: List[Dict]) -> List[Dict]:
        """Sort line based on dominant script (RTL for Arabic, LTR otherwise)."""
        if not line: return []
        
        from utils.unicode_helpers import get_arabic_ratio
        full_text = " ".join([b['text'] for b in line])
        
        if get_arabic_ratio(full_text) > 0.3:
            # Arabic line: Sort Right-to-Left (High X first)
            return sorted(line, key=lambda x: x['bbox'][0], reverse=True)
        else:
            # Latin/Mixed line: Sort Left-to-Right (Low X first)
            return sorted(line, key=lambda x: x['bbox'][0])

    def _merge_horizontal_neighbors(self, blocks: List[Dict]) -> List[Dict]:
        """Merge blocks that are on the same line and very close horizontally."""
        if not blocks: return []
        
        # Sort by Y then X (LTR for merging logic)
        sorted_blocks = sorted(blocks, key=lambda b: (b['bbox'][1], b['bbox'][0]))
        
        merged = []
        curr = sorted_blocks[0]
        
        for next_b in sorted_blocks[1:]:
            y_overlap = min(curr['bbox'][3], next_b['bbox'][3]) - max(curr['bbox'][1], next_b['bbox'][1])
            h_dist = next_b['bbox'][0] - curr['bbox'][2]
            
            height = curr['bbox'][3] - curr['bbox'][1]
            # STRICT: Only merge if gap is very small (e.g. 10% of height)
            merge_threshold = height * 0.15 
            
            if y_overlap > height * 0.6 and h_dist < merge_threshold:
                curr['bbox'] = [
                    min(curr['bbox'][0], next_b['bbox'][0]),
                    min(curr['bbox'][1], next_b['bbox'][1]),
                    max(curr['bbox'][2], next_b['bbox'][2]),
                    max(curr['bbox'][3], next_b['bbox'][3])
                ]
                curr['text'] = curr['text'].strip() + " " + next_b['text'].strip()
            else:
                merged.append(curr)
                curr = next_b
        merged.append(curr)
        return merged

    def _detect_tables(self, lines: List[List[Dict]]) -> List[Dict]:
        """
        Detect tables by looking for multi-column lines.
        """
        processed_regions = []
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # If line has 2+ distinct blocks (after strict merging), check for table structure
            if len(line) >= 2:
                # Heuristic: If gaps are significant, it's a table row
                gaps = []
                # Line is sorted LTR for gap analysis
                line_ltr = sorted(line, key=lambda x: x['bbox'][0])
                for k in range(len(line_ltr)-1):
                    gaps.append(line_ltr[k+1]['bbox'][0] - line_ltr[k]['bbox'][2])
                
                avg_gap = sum(gaps) / len(gaps) if gaps else 0
                
                # Check for subsequent rows with similar structure
                table_rows = [line]
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    if len(next_line) >= 2 and self._structure_matches(line, next_line):
                        table_rows.append(next_line)
                        j += 1
                    else:
                        break
                
                # If we have multiple rows OR one row with VERY large gaps, it's a table
                if len(table_rows) >= 2 or avg_gap > 50:
                    print(f"  [LayoutProcessor] Detected Table with {len(table_rows)} rows. Avg Gap: {avg_gap:.1f}")
                    processed_regions.append(self._reconstruct_table_object(table_rows))
                    i = j
                    continue
            
                # Paragraph: Merge blocks. 
                # Sort based on global/detected direction
                if self.direction == "RTL":
                    sorted_line = sorted(line, key=lambda b: b['bbox'][0], reverse=True)
                else:
                    sorted_line = sorted(line, key=lambda b: b['bbox'][0])
                    
                merged_text = " ".join([b['text'].strip() for b in sorted_line if b['text'].strip()])
                x0 = min(b['bbox'][0] for b in line)
                y0 = min(b['bbox'][1] for b in line)
                x1 = max(b['bbox'][2] for b in line)
                y1 = max(b['bbox'][3] for b in line)
                
                processed_regions.append({
                    'type': 'text',
                    'text': merged_text,
                    'bbox': [x0, y0, x1, y1]
                })
            i += 1
            
        return processed_regions

    def _structure_matches(self, line1: List[Dict], line2: List[Dict]) -> bool:
        """Checks if two lines share similar column count and roughly similar X-boundaries."""
        if len(line1) != len(line2) and abs(len(line1) - len(line2)) > 1:
            return False
            
        # Check overall span
        span1 = (line1[0]['bbox'][0], line1[-1]['bbox'][2])
        span2 = (line2[0]['bbox'][0], line2[-1]['bbox'][2])
        
        # Overlap in horizontal span
        overlap = min(span1[1], span2[1]) - max(span1[0], span2[0])
        total = max(span1[1], span2[1]) - min(span1[0], span2[0])
        
        if total == 0: return False
        # Lenient match for tables (noisy OCR)
        return (overlap / total) > 0.6

    def _split_multicolumn_blocks(self, blocks: List[Dict]) -> List[Dict]:
        """
        Split a single block into multiple if it contains a large horizontal gap 
        represented by multiple spaces. This fixes OCR 'over-merging' in tables.
        """
        split_blocks = []
        for b in blocks:
            text = b['text']
            # Look for 2+ consecutive spaces (more aggressive)
            if "  " in text:
                # Use regex to find gaps of 2+ spaces
                import regex as re
                parts = re.split(r'(\s{2,})', text)
                if len(parts) > 1:
                    x0, y0, x1, y1 = b['bbox']
                    total_chars = len(text)
                    curr_char_idx = 0
                    width = x1 - x0
                    
                    for part in parts:
                        p_len = len(part)
                        if not part.strip():
                            # This is a gap
                            curr_char_idx += p_len
                            continue
                        
                        # Estimate start/end X based on char index
                        start_x = x0 + (curr_char_idx / total_chars) * width
                        part_width = (p_len / total_chars) * width
                        
                        split_blocks.append({
                            'text': part.strip(),
                            'bbox': [start_x, y0, start_x + part_width, y1],
                            'confidence': b.get('confidence', 1.0),
                            'type': 'text'
                        })
                        curr_char_idx += p_len
                    continue
            split_blocks.append(b)
        return split_blocks

    def _reconstruct_table_object(self, rows: List[List[Dict]]) -> Dict:
        """Convert clustered rows into a Nassij Table Object."""
        from core.arabic_processor import ArabicProcessor
        ap = ArabicProcessor()
        
        cells = []
        for row in rows:
            # Sort individual row by X based on global direction
            if self.direction == "RTL":
                sorted_row = sorted(row, key=lambda b: b['bbox'][0], reverse=True)
            else:
                sorted_row = sorted(row, key=lambda b: b['bbox'][0])
            
            # Process each cell's text through the ArabicProcessor (Logical Order)
            row_texts = []
            for b in sorted_row:
                text = b['text'].strip()
                if self.direction == "RTL":
                    # Process as logical RTL for table cell
                    text = ap.normalize_arabic_text(text, logical=True)
                row_texts.append(text)
            cells.append(row_texts)
            
        # Full bbox
        all_blocks = [b for row in rows for b in row]
        x0 = min(b['bbox'][0] for b in all_blocks)
        y0 = min(b['bbox'][1] for b in all_blocks)
        x1 = max(b['bbox'][2] for b in all_blocks)
        y1 = max(b['bbox'][3] for b in all_blocks)
        
        return {
            "type": "table",
            "bbox": [x0, y0, x1, y1],
            "cells": cells,
            "is_arabic": self.direction == "RTL"
        }
