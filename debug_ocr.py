import os
import sys
from PIL import Image, ImageDraw
import numpy as np
from core.pdf_reader import PDFReader

def debug_ocr_page(pdf_path, page_num, output_image_path):
    print(f"Debugging OCR for {pdf_path}, page {page_num+1}...")
    
    with PDFReader(pdf_path) as reader:
        # 1. Convert page to image
        img = reader.convert_page_to_image(page_num, dpi=300)
        draw = ImageDraw.Draw(img)
        
        # 2. Run EasyOCR
        from core.engines.easyocr_engine import EasyOCREngine
        engine = EasyOCREngine()
        engine.initialize()
        
        # We want the raw blocks before LayoutProcessor if possible to see "noise"
        # But EasyOCREngine.extract_layout now calls LayoutProcessor. 
        # Let's see the processed regions first.
        result = engine.extract_layout(img)
        
        # 3. Draw Bounding Boxes and Print Text
        for region in result['text_blocks']:
            bbox = region['bbox']
            r_type = region['type']
            text = region.get('text', '')
            
            print(f"[{r_type}] - BBox: {bbox} - Text: {text}")
            
            # Color by type
            color = "red" if r_type == "text" else "blue"
            
            # Draw rectangle
            draw.rectangle(bbox, outline=color, width=3)
            
            # Draw label
            label = f"{r_type}: {text[:15]}..." if r_type == 'text' else 'TABLE'
            draw.text((bbox[0], bbox[1]-10), label, fill=color)
            
        img.save(output_image_path)
        print(f"Debug image saved to {output_image_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_ocr.py <pdf_path>")
    else:
        debug_ocr_page(sys.argv[1], 0, "ocr_debug_page_1.png")
