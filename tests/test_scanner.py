import fitz
import os
from core.scanner import NassijScanner

def create_dummy_pdf(filename="dummy_test.pdf"):
    doc = fitz.open()
    page = doc.new_page()
    text_heading = "Nassij V3 Test Heading"
    text_para = "This is a simple paragraph to test the NassijScanner. It should extract size, font, and style."
    page.insert_text((50, 50), text_heading, fontsize=16, fontname="helv", color=(1, 0, 0))
    page.insert_text((50, 100), text_para, fontsize=12, fontname="helv", color=(0, 0, 0))
    doc.save(filename)
    doc.close()
    return filename

def test_scanner():
    filename = create_dummy_pdf()
    print(f"Created {filename}")
    
    doc = fitz.open(filename)
    page = doc[0]
    
    raw_data = page.get_text("rawdict")
    print(f"Raw blocks count: {len(raw_data.get('blocks', []))}")
    
    scanner = NassijScanner()
    blocks = scanner.scan_page(page)
    print(f"Processed blocks count: {len(blocks)}")
    
    for i, block in enumerate(blocks):
        print(f"\nBlock {i+1} Type: {block['type']}")
        print(f"Full Text: {block['text']}")
        for j, span in enumerate(block['spans']):
            print(f"  Span {j+1}: '{span['text']}' | Font: {span['font']} | Size: {span['size']} | Color: {span['color']} | Bold: {span['is_bold']} | Italic: {span['is_italic']}")
            
    doc.close()

if __name__ == "__main__":
    test_scanner()
