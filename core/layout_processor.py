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
            
        # 1. Group by lines
        lines = self._group_by_lines(blocks)
        
        # 2. Identify structural regions (simple grid-based table detection)
        results = self._detect_tables(lines)
        
        return results

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
                    # IMPORTANT: Sort line RTL (Right-to-Left) for Arabic processing
                    # x[bbox][0] is the left edge. For RTL, we want higher x first.
                    current_line.sort(key=lambda x: x['bbox'][0], reverse=True)
                    lines.append(current_line)
                    current_line = [b]
                    current_y_mid = b_y_mid
            
            current_line.sort(key=lambda x: x['bbox'][0], reverse=True)
            lines.append(current_line)
        return lines

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
                if len(table_rows) >= 2 or avg_gap > 60:
                    processed_regions.append(self._reconstruct_table_object(table_rows))
                    i = j
                    continue
            
            if line:
                # Paragraph: Merge blocks. 
                # IMPORTANT: For Arabic paragraphs, if we have fragments, 
                # we must join them such that the RIGHT-most is first (logical start).
                # line is already sorted RTL in _group_by_lines
                merged_text = " ".join([b['text'].strip() for b in line])
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
        return (overlap / total) > 0.7

    def _reconstruct_table_object(self, rows: List[List[Dict]]) -> Dict:
        """Convert clustered rows into a Nassij Table Object."""
        cells = []
        for row in rows:
            # Sort individual row by X (descending for Arabic RTL)
            sorted_row = sorted(row, key=lambda b: b['bbox'][0], reverse=True)
            cells.append([b['text'] for b in sorted_row])
            
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
            "is_arabic": True # Heuristic, can be refined
        }
