"""
OCR Engine Wrapper.
Delegates to specific engine implementations (PaddleOCR, Tesseract, etc.)
"""
from typing import Any, Dict, Optional
from PIL import Image

# Import specific implementation 
# Priority: EasyOCR (Python 3.14 compatible), then PaddleOCR
try:
    from core.engines.easyocr_engine import EasyOCREngine as PrimaryEngine
    ENGINE_NAME = "EasyOCR"
except ImportError:
    try:
        from core.engines.paddle_engine import PaddleOCREngine as PrimaryEngine
        ENGINE_NAME = "PaddleOCR"
    except ImportError:
        PrimaryEngine = None
        ENGINE_NAME = "None"

import logging

logger = logging.getLogger(__name__)

class OCRFacade:
    """
    Facade for OCR Engine.
    Currently delegates to: EasyOCR or PaddleOCR.
    """
    def __init__(self, lang: str = 'ar', use_table: bool = True):
        self.engine = None
        if PrimaryEngine:
            logger.info(f"Initializing Primary OCR Engine: {ENGINE_NAME}")
            if ENGINE_NAME == "EasyOCR":
                self.engine = PrimaryEngine(lang=lang)
            else:
                self.engine = PrimaryEngine(lang=lang, use_table=use_table)
            
            if not self.engine.initialize():
                logger.error(f"Failed to initialize {ENGINE_NAME}")
                self.engine = None
        else:
            logger.warning("No capable OCR Engine found (EasyOCR or PaddleOCR).")

    def extract_from_pil_image(self, image: Image.Image) -> Dict:
        if not self.engine:
             return {'text_blocks': [], 'tables': []}
        return self.engine.extract_layout(image)


