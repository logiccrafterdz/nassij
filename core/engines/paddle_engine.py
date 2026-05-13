from typing import Dict, Any, List, Tuple
import logging
import numpy as np
from PIL import Image

from core.engines.base_engine import OCREngine
from core.image_preprocessor import ImagePreprocessor

class PaddleOCREngine(OCREngine):
    """
    PaddleOCR implementation for Arabic text and table extraction.
    """
    
    def __init__(self, lang: str = 'ar', use_table: bool = True):
        self.lang = lang
        self.use_table = use_table
        self.ocr_engine = None
        self.table_engine = None
        self.structure_engine = None
        self.is_ready = False
        self.preprocessor = ImagePreprocessor()
        
    def initialize(self) -> bool:
        """Initialize PaddleOCR models."""
        try:
            from paddleocr import PaddleOCR, PPStructure
            
            # Text + Layout OCR
            # disable_angle_cls=True might improve speed if pages are upright
            self.ocr_engine = PaddleOCR(use_angle_cls=True, lang=self.lang, show_log=False)
            
            if self.use_table:
                # PP-Structure for table analysis
                self.structure_engine = PPStructure(show_log=False, image_orientation=True)
                
            self.is_ready = True
            print("PaddleOCR initialized successfully.")
            return True
        except ImportError:
            print("Error: PaddleOCR not installed. Please install with: pip install paddlepaddle paddleocr")
            return False
        except Exception as e:
            print(f"Error initializing PaddleOCR: {e}")
            return False

    def extract_text(self, image_input: Any) -> str:
        if not self.is_ready:
            raise RuntimeError("PaddleOCR not initialized")
            
        result = self.ocr_engine.ocr(self._prepare_image(image_input), cls=True)
        if not result or not result[0]:
            return ""
            
        # result structure: [[[[x1,y1],[x2,y2]..],("text",conf)], ...]
        text_lines = [line[1][0] for line in result[0]]
        return "\n".join(text_lines)

    def extract_layout(self, image_input: Any) -> Dict[str, Any]:
        """
        Extract text blocks and tables using PaddleOCR + PP-Structure.
        """
        if not self.is_ready:
            raise RuntimeError("PaddleOCR not initialized")
            
        img_array = self._prepare_image(image_input)
        
        # 1. Run Layout/Table analysis (PP-Structure)
        # This gives us regions: Table, Image, Text, Title, etc.
        structure_results = []
        if self.structure_engine:
            structure_results = self.structure_engine(img_array)
            
        tables = []
        text_blocks = []
        
        # Process structure results
        for region in structure_results:
            region_type = region.get('type')
            bbox = region.get('bbox') # [x1, y1, x2, y2]
            res = region.get('res')
            
            if region_type == 'table':
                # res containing html or cell info
                # verify if it has reliable html or if requires rebuilding
                if 'html' in res:
                    html_content = res['html']
                    parsed_cells, merged_cells = self._parse_html_table(html_content)
                    tables.append({
                        'type': 'table',
                        'html': html_content,
                        'cells': parsed_cells,
                        'merged_cells': merged_cells,
                        'bbox': bbox,
                        'confidence': region.get('score', 0.0)
                    })
            else:
                # Text regions (Title, Text, List, etc.)
                # PP-Structure returns OCR results inside 'res' for these regions usually
                # Or we can re-run OCR on crops if structure output is insufficient
                if isinstance(res, list):
                    for line in res:
                         if isinstance(line, dict) and 'text' in line:
                             # Some versions of PPStructure return detailed dicts
                             text_blocks.append({
                                 'text': line['text'],
                                 'bbox': line.get('bbox', bbox), # fallback to region bbox
                                 'type': 'text'
                             })
        
        # Fallback: If no structure found or just simple page, run standard OCR for text
        if not text_blocks and not tables:
             raw_ocr = self.ocr_engine.ocr(img_array, cls=True)
             if raw_ocr and raw_ocr[0]:
                 for line in raw_ocr[0]:
                     # line: [box, (text, score)]
                     box = line[0]
                     text = line[1][0]
                     # Convert box points to bbox [min_x, min_y, max_x, max_y]
                     xs = [p[0] for p in box]
                     ys = [p[1] for p in box]
                     bbox = [min(xs), min(ys), max(xs), max(ys)]
                     
                     text_blocks.append({
                         'text': text,
                         'bbox': bbox,
                         'type': 'text'
                     })
                     
        return {
            'text_blocks': text_blocks,
            'tables': tables
        }

    def _prepare_image(self, image_input: Any) -> np.ndarray:
        """Convert input (path or PIL) to numpy array for Paddle."""
        if isinstance(image_input, str):
            img = np.array(Image.open(image_input))
        elif isinstance(image_input, Image.Image):
            img = np.array(image_input)
        elif isinstance(image_input, np.ndarray):
            img = image_input
        else:
            raise ValueError(f"Unsupported image type: {type(image_input)}")
            
        return self.preprocessor.process(img)

    def _parse_html_table(self, html_str: str) -> Tuple[List[List[str]], List[Dict]]:
        import regex as re
        rows = []
        merged_cells = []
        
        # Find all tr tags
        tr_matches = re.findall(r'<tr[^>]*>(.*?)</tr>', html_str, re.IGNORECASE | re.DOTALL)
        for row_idx, tr in enumerate(tr_matches):
            # Find all td or th tags
            cell_matches = re.finditer(r'<t[dh]([^>]*)>(.*?)</t[dh]>', tr, re.IGNORECASE | re.DOTALL)
            row = []
            col_idx = 0
            for match in cell_matches:
                attrs = match.group(1)
                content = match.group(2)
                
                colspan = 1
                rowspan = 1
                cs_match = re.search(r'colspan\s*=\s*["\']?(\d+)["\']?', attrs, re.IGNORECASE)
                if cs_match: colspan = int(cs_match.group(1))
                rs_match = re.search(r'rowspan\s*=\s*["\']?(\d+)["\']?', attrs, re.IGNORECASE)
                if rs_match: rowspan = int(rs_match.group(1))
                
                if colspan > 1 or rowspan > 1:
                    merged_cells.append({
                        'row': row_idx,
                        'col': col_idx,
                        'row_span': rowspan,
                        'col_span': colspan
                    })
                
                # Remove inner HTML tags if any
                clean_text = re.sub(r'<[^>]+>', '', content).strip()
                # Unescape common HTML entities
                clean_text = clean_text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
                row.append(clean_text)
                
                # Pad for colspan so grid aligns
                for _ in range(colspan - 1):
                    row.append("")
                
                col_idx += colspan
                
            if row:
                rows.append(row)
        return rows, merged_cells
