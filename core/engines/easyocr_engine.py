from typing import Dict, Any, List
import numpy as np
from PIL import Image
import logging

from core.engines.base_engine import OCREngine

class EasyOCREngine(OCREngine):
    """
    EasyOCR implementation for Arabic text extraction.
    Supports Python 3.14 via PyTorch backend.
    """
    
    def __init__(self, lang: str = 'ar', use_gpu: bool = False):
        self.lang = lang
        self.use_gpu = use_gpu
        self.reader = None
        self.is_ready = False
        
    def initialize(self) -> bool:
        """Initialize EasyOCR Reader."""
        try:
            import easyocr
            # Initialize reader with Arabic and English
            # EasyOCR downloads model on first run
            print("Initializing EasyOCR model (this may take a moment)...")
            self.reader = easyocr.Reader(['ar', 'en'], gpu=self.use_gpu)
            self.is_ready = True
            print("EasyOCR initialized successfully.")
            return True
        except ImportError:
            print("Error: easyocr not installed.")
            return False
        except Exception as e:
            print(f"Error initializing EasyOCR: {e}")
            return False

    def extract_text(self, image_input: Any) -> str:
        if not self.is_ready:
            raise RuntimeError("EasyOCR not initialized")
        
        results = self.reader.readtext(self._prepare_image(image_input), detail=0)
        return "\n".join(results)

    def extract_layout(self, image_input: Any) -> Dict[str, Any]:
        """
        Extract text blocks using EasyOCR.
        Note: EasyOCR doesn't detect tables natively like Paddle. 
        We return text blocks, and table detection would need a separate heuristic or model.
        """
        if not self.is_ready:
            raise RuntimeError("EasyOCR not initialized")
            
        img = self._prepare_image(image_input)
        
        # EasyOCR returns: [[bbox, text, conf], ...]
        # bbox is [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
        raw_results = self.reader.readtext(img)
        
        text_blocks = []
        full_text_parts = []
        
        for bbox, text, conf in raw_results:
            # Normalize bbox to [min_x, min_y, max_x, max_y]
            xs = [p[0] for p in bbox]
            ys = [p[1] for p in bbox]
            simple_bbox = [min(xs), min(ys), max(xs), max(ys)]
            
            text_blocks.append({
                'text': text,
                'bbox': simple_bbox,
                'confidence': float(conf),
                'type': 'text'
            })
            full_text_parts.append(text)
            
        return {
            'text_blocks': text_blocks,
            'tables': [], # Table detection pending (requires Table Transformer)
            'full_text': "\n".join(full_text_parts)
        }

    def _prepare_image(self, image_input: Any) -> np.ndarray:
        """Convert input to numpy array."""
        if isinstance(image_input, str):
            return np.array(Image.open(image_input))
        elif isinstance(image_input, Image.Image):
            return np.array(image_input)
        elif isinstance(image_input, np.ndarray):
            return image_input
        else:
            raise ValueError(f"Unsupported image type: {type(image_input)}")
