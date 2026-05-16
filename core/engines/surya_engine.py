from typing import Dict, Any, List
import logging
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

from core.engines.base_engine import OCREngine

class SuryaOCREngine(OCREngine):
    """
    Surya OCR implementation for Arabic text and layout extraction.
    Significantly faster and more accurate than EasyOCR for complex layouts.
    """
    
    def __init__(self, lang: str = 'ar', use_gpu: bool = True):
        self.lang = lang
        self.use_gpu = use_gpu
        self.is_ready = False
        
        self.det_model = None
        self.det_processor = None
        self.rec_model = None
        self.rec_processor = None
        
    def initialize(self) -> bool:
        """Initialize Surya OCR models."""
        try:
            from surya.model.detection.model import load_model as load_det_model
            from surya.model.detection.model import load_processor as load_det_processor
            from surya.model.recognition.model import load_model as load_rec_model
            from surya.model.recognition.processor import load_processor as load_rec_processor
            
            logger.info("Initializing Surya OCR models (this may take a moment)...")
            
            self.det_model = load_det_model()
            self.det_processor = load_det_processor()
            
            self.rec_model = load_rec_model()
            self.rec_processor = load_rec_processor()
            
            self.is_ready = True
            logger.info("Surya OCR initialized successfully.")
            return True
        except ImportError:
            logger.error("Error: surya-ocr not installed. Install via: pip install surya-ocr")
            return False
        except Exception as e:
            logger.error(f"Error initializing Surya OCR: {e}")
            return False

    def extract_text(self, image_input: Any) -> str:
        if not self.is_ready:
            raise RuntimeError("Surya OCR not initialized")
            
        img = self._prepare_image(image_input)
        
        from surya.ocr import run_ocr
        # run_ocr expects list of images, list of languages
        langs = [self.lang]
        predictions = run_ocr([img], [langs], self.det_model, self.det_processor, self.rec_model, self.rec_processor)
        
        if not predictions or not predictions[0].text_lines:
            return ""
            
        lines = [line.text for line in predictions[0].text_lines]
        return "\n".join(lines)

    def extract_layout(self, image_input: Any) -> Dict[str, Any]:
        """
        Extract text blocks using Surya.
        """
        if not self.is_ready:
            raise RuntimeError("Surya OCR not initialized")
            
        img = self._prepare_image(image_input)
        
        from surya.ocr import run_ocr
        langs = [self.lang]
        predictions = run_ocr([img], [langs], self.det_model, self.det_processor, self.rec_model, self.rec_processor)
        
        text_blocks = []
        full_text_parts = []
        
        if predictions and predictions[0].text_lines:
            for line in predictions[0].text_lines:
                # Surya bbox is [x1, y1, x2, y2]
                text_blocks.append({
                    'text': line.text,
                    'bbox': line.bbox,
                    'confidence': getattr(line, 'confidence', 1.0),
                    'type': 'text'
                })
                full_text_parts.append(line.text)
                
        # Note: Surya has a dedicated layout analysis module (run_layout) we could use,
        # but for simplicity we rely on the core pipeline grouping or basic line text for now.
        return {
            'text_blocks': text_blocks,
            'tables': [],
            'full_text': "\n".join(full_text_parts)
        }

    def _prepare_image(self, image_input: Any) -> Image.Image:
        """Convert input to PIL Image."""
        if isinstance(image_input, str):
            return Image.open(image_input).convert("RGB")
        elif isinstance(image_input, np.ndarray):
            return Image.fromarray(image_input).convert("RGB")
        elif isinstance(image_input, Image.Image):
            return image_input.convert("RGB")
        else:
            raise ValueError(f"Unsupported image type: {type(image_input)}")
