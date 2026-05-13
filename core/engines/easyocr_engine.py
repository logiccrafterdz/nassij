from typing import Dict, Any, List
import numpy as np
from PIL import Image
import logging

from core.engines.base_engine import OCREngine
from core.image_preprocessor import ImagePreprocessor

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
        self.preprocessor = ImagePreprocessor()
        
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
        Extract text blocks using EasyOCR and analyze layout.
        Uses LayoutProcessor for table detection.
        """
        if not self.is_ready:
            raise RuntimeError("EasyOCR not initialized")
            
        img = self._prepare_image(image_input)
        
        # EasyOCR returns: [[bbox, text, conf], ...]
        # Granular settings to avoid merging columns
        raw_results = self.reader.readtext(
            img, 
            paragraph=False, 
            width_ths=0.001,  # Minimum possible merging
            link_threshold=0.1, # Break blocks on even small gaps
            add_margin=0.0,
            slope_ths=0.1
        )
        
        raw_blocks = []
        full_text_parts = []
        
        for bbox, text, conf in raw_results:
            xs = [p[0] for p in bbox]
            ys = [p[1] for p in bbox]
            simple_bbox = [min(xs), min(ys), max(xs), max(ys)]
            
            raw_blocks.append({
                'text': text,
                'bbox': simple_bbox,
                'confidence': float(conf),
                'type': 'text'
            })
            full_text_parts.append(text)
            
        # Analyze Layout (Detect Tables/Columns)
        from core.layout_processor import LayoutProcessor
        lp = LayoutProcessor()
        regions = lp.process_layout(raw_blocks)
        
        # Separate tables and text blocks for backward compatibility if needed,
        # but Nassij DOCXBuilder now supports interleaved blocks.
        text_blocks = [r for r in regions if r['type'] == 'text']
        tables = [r for r in regions if r['type'] == 'table']
            
        return {
            'text_blocks': regions, # Interleaved regions (preserving reading order)
            'tables': [], # Keep empty as 'text_blocks' contains everything correctly typed
            'full_text': "\n".join(full_text_parts)
        }

    def _prepare_image(self, image_input: Any) -> np.ndarray:
        """Convert input to numpy array."""
        if isinstance(image_input, str):
            img = np.array(Image.open(image_input))
        elif isinstance(image_input, Image.Image):
            img = np.array(image_input)
        elif isinstance(image_input, np.ndarray):
            img = image_input
        else:
            raise ValueError(f"Unsupported image type: {type(image_input)}")
            
        return self.preprocessor.process(img)
