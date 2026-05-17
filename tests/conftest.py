import sys
from pathlib import Path
import fitz
import pytest

# Add project root to path so tests can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def create_pdf_with_text(path: Path, text: str, font_size=14, fontname="helv", rtl=False) -> Path:
    """Create a digital-native PDF with specific text for testing."""
    doc = fitz.open()
    page = doc.new_page()
    
    # insert_text with 'right' alignment doesn't fully mimic complex RTL PDFs
    # but it provides a baseline. For true complex RTL, we might need pre-made PDFs
    # or to use insert_textbox with specific flags.
    page.insert_textbox(fitz.Rect(50, 50, 500, 800), text, fontsize=font_size, fontname=fontname, align=2 if rtl else 0)
    
    doc.save(str(path))
    doc.close()
    return path

def create_pdf_with_paragraphs(path: Path, paragraphs: list, font_size=14, fontname="helv") -> Path:
    """Create a PDF with multiple separate paragraphs."""
    doc = fitz.open()
    page = doc.new_page()
    
    y = 50
    for p in paragraphs:
        page.insert_textbox(fitz.Rect(50, y, 500, y + 100), p, fontsize=font_size, fontname=fontname)
        y += 120
        
    doc.save(str(path))
    doc.close()
    return path

@pytest.fixture
def pdf_generator(tmp_path):
    """Fixture that provides a temporary path and generation helpers."""
    class Generator:
        def __init__(self, tmpdir):
            self.tmpdir = tmpdir
            
        def with_text(self, text: str, rtl=False, filename="test.pdf") -> Path:
            return create_pdf_with_text(self.tmpdir / filename, text, rtl=rtl)
            
        def with_paragraphs(self, paragraphs: list, filename="test.pdf") -> Path:
            return create_pdf_with_paragraphs(self.tmpdir / filename, paragraphs)
            
    return Generator(tmp_path)
