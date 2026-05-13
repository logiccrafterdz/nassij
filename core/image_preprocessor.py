"""
Image preprocessing module.
Improves OCR accuracy for scanned documents through deskewing, binarization, and denoising.
"""
import cv2
import numpy as np
from PIL import Image
from typing import Union, Tuple

class ImagePreprocessor:
    """
    Handles image preprocessing before passing to OCR engines.
    """
    
    def __init__(self, deskew: bool = True, binarize: bool = False, denoise: bool = True):
        self.deskew = deskew
        self.binarize = binarize
        self.denoise = denoise
        
    def process(self, image: Union[str, Image.Image, np.ndarray]) -> np.ndarray:
        """
        Run the full preprocessing pipeline.
        """
        img = self._to_numpy(image)
        
        # Convert to grayscale if it's color
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
            
        processed = gray
        
        if self.deskew:
            processed = self._deskew_image(processed)
            
        if self.denoise:
            # Non-local means denoising preserves edges better than Gaussian blur
            processed = cv2.fastNlMeansDenoising(processed, h=10)
            
        if self.binarize:
            # Sauvola binarization or Otsu depending on lighting
            # We use adaptive thresholding here as a robust default
            processed = cv2.adaptiveThreshold(
                processed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
        # If the original image was color, we convert back to BGR for compatibility with some OCR engines
        # that expect 3 channels (like PaddleOCR in some configurations)
        if len(img.shape) == 3:
            processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
            
        return processed
        
    def _to_numpy(self, image: Union[str, Image.Image, np.ndarray]) -> np.ndarray:
        """Convert input to numpy array."""
        if isinstance(image, str):
            img = cv2.imread(image)
            if img is None:
                raise ValueError(f"Could not read image from {image}")
            return img
        elif isinstance(image, Image.Image):
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        elif isinstance(image, np.ndarray):
            return image
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")
            
    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """
        Detect and correct skew in the image.
        Uses projection profile method or Hough lines.
        """
        # Threshold the image
        _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find coordinates of non-zero pixels
        coords = np.column_stack(np.where(thresh > 0))
        
        if len(coords) == 0:
            return image
            
        # Get minAreaRect
        angle = cv2.minAreaRect(coords)[-1]
        
        # The `cv2.minAreaRect` function returns values in the range [-90, 0)
        # We need to adjust the angle based on its orientation
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        # If angle is very small, ignore (to avoid blurring from rotation)
        if abs(angle) < 0.5:
            return image
            
        # Rotate image
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h), 
            flags=cv2.INTER_CUBIC, 
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return rotated
