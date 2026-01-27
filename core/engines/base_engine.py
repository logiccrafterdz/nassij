from abc import ABC, abstractmethod
from typing import Dict, List, Any, Union

class OCREngine(ABC):
    """
    Abstract base class for OCR engines (PaddleOCR, Tesseract, QARI, etc.)
    """
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the OCR engine models/resources."""
        pass
        
    @abstractmethod
    def extract_text(self, image_input: Any) -> str:
        """Extract raw text from image."""
        pass
        
    @abstractmethod
    def extract_layout(self, image_input: Any) -> Dict[str, Any]:
        """
        Extract structured layout (blocks, tables, lines).
        
        Returns:
            Dictionary containing 'text_blocks', 'tables', etc.
        """
        pass
