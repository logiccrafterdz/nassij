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

class PaddleOCREngine: # Keeping name for compatibility, or alias it
    """
    Wrapper for OCR Engine.
    Currently delegates to: EasyOCR or PaddleOCR check logs.
    """
    def __init__(self, lang: str = 'ar', use_table: bool = True):
        self.engine = None
        if PrimaryEngine:
            print(f"Initializing Primary OCR Engine: {ENGINE_NAME}")
            # EasyOCR doesn't use 'use_table' in constructor logic same way, but we pass what we can
            # Our wrappers match args loosely or we adapt
            if ENGINE_NAME == "EasyOCR":
                self.engine = PrimaryEngine(lang=lang)
            else:
                self.engine = PrimaryEngine(lang=lang, use_table=use_table)
            
            if not self.engine.initialize():
                print(f"Failed to initialize {ENGINE_NAME}")
                self.engine = None
        else:
            print("Warning: No capable OCR Engine found (EasyOCR or PaddleOCR).")

    def extract_from_pil_image(self, image: Image.Image) -> Dict:
        if not self.engine:
             return {'text_blocks': [], 'tables': []}
        return self.engine.extract_layout(image)


