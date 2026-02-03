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
        """Group blocks that share similar Y coordinates."""
        if not blocks:
            return []
            
        # Sort by top-Y
        sorted_blocks = sorted(blocks, key=lambda b: b['bbox'][1])
        
        lines = []
        if sorted_blocks:
            current_line = [sorted_blocks[0]]
            current_y = sorted_blocks[0]['bbox'][1]
            
            for b in sorted_blocks[1:]:
                if abs(b['bbox'][1] - current_y) < self.y_tolerance:
                    current_line.append(b)
                else:
                    # Sort line horizontally (default RTL for Arabic heuristic later)
                    lines.append(current_line)
                    current_line = [b]
                    current_y = b['bbox'][1]
            lines.append(current_line)
        return lines

    def _detect_tables(self, lines: List[List[Dict]]) -> List[Dict]:
        """
        Heuristic: If multiple lines have similar horizontal gaps, group them as a table.
        """
        processed_blocks = []
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Simple heuristic: If a line has many gaps, it might be a table row
            if len(line) >= 2:
                table_row_candidate = self._analyze_line_structure(line)
                
                # Check followers
                table_rows = [line]
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    if len(next_line) >= 2 and self._lines_align(line, next_line):
                        table_rows.append(next_line)
                        j += 1
                    else:
                        break
                
                if len(table_rows) >= 2:
                    # Form a table
                    processed_blocks.append(self._reconstruct_table_object(table_rows))
                    i = j
                    continue
            
            # Not a table, flatten to individual text blocks (or paragraphs)
            # For now, we return individual blocks to match docx_builder expectation
            processed_blocks.extend(line)
            i += 1
            
        return processed_blocks

    def _analyze_line_structure(self, line: List[Dict]) -> Dict:
        # Sort LTR for analysis
        sorted_line = sorted(line, key=lambda b: b['bbox'][0])
        return {"count": len(sorted_line), "x0": sorted_line[0]['bbox'][0], "x1": sorted_line[-1]['bbox'][2]}

    def _lines_align(self, line1: List[Dict], line2: List[Dict]) -> bool:
        """Helper to check if two lines have similar column counts/alignments."""
        if len(line1) != len(line2):
            return False
            
        # Basic check: do they start/end at similar places?
        s1 = self._analyze_line_structure(line1)
        s2 = self._analyze_line_structure(line2)
        
        start_diff = abs(s1['x0'] - s2['x0'])
        end_diff = abs(s1['x1'] - s2['x1'])
        
        return start_diff < 50 and end_diff < 50

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
