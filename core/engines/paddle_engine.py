from typing import Dict, Any, List
import logging
import numpy as np
from PIL import Image

from core.engines.base_engine import OCREngine

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
                    tables.append({
                        'html': res['html'],
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
            return np.array(Image.open(image_input))
        elif isinstance(image_input, Image.Image):
            return np.array(image_input)
        elif isinstance(image_input, np.ndarray):
            return image_input
        else:
            raise ValueError(f"Unsupported image type: {type(image_input)}")
