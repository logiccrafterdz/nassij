"""
Tests for the PDFReader module.
Covers page counting, text extraction, scanned page detection, and image conversion.
"""
import pytest
import fitz
from pathlib import Path
from PIL import Image

from core.pdf_reader import PDFReader


def create_digital_pdf(path: Path, text: str = "بسم الله الرحمن الرحيم"):
    """Create a digital-native PDF with embedded text."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 100), text, fontsize=14)
    page.insert_text((50, 200), "This is a test paragraph with English text.", fontsize=12)
    doc.save(str(path))
    doc.close()


def create_empty_pdf(path: Path):
    """Create a PDF with no text (simulates a scanned page)."""
    doc = fitz.open()
    page = doc.new_page()
    # Insert a small rectangle to simulate an image-only page
    shape = page.new_shape()
    shape.draw_rect(fitz.Rect(50, 50, 200, 200))
    shape.finish(color=(0, 0, 0), fill=(0.9, 0.9, 0.9))
    shape.commit()
    doc.save(str(path))
    doc.close()


def create_multipage_pdf(path: Path, pages: int = 5):
    """Create a multi-page PDF."""
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page()
        page.insert_text((50, 100), f"Page {i + 1}: محتوى الصفحة", fontsize=12)
    doc.save(str(path))
    doc.close()


class TestPDFReader:
    """Tests for PDFReader core functionality."""

    def test_open_valid_pdf(self, tmp_path):
        """PDFReader should open a valid PDF without errors."""
        pdf_path = tmp_path / "valid.pdf"
        create_digital_pdf(pdf_path)

        with PDFReader(str(pdf_path)) as reader:
            assert reader.page_count > 0

    def test_open_nonexistent_pdf_raises(self):
        """Opening a non-existent file should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            PDFReader("nonexistent_file.pdf")

    def test_page_count(self, tmp_path):
        """Page count should match the number of pages inserted."""
        pdf_path = tmp_path / "multi.pdf"
        create_multipage_pdf(pdf_path, pages=5)

        with PDFReader(str(pdf_path)) as reader:
            assert reader.get_page_count() == 5

    def test_extract_text_from_digital_page(self, tmp_path):
        """Text extraction from a digital PDF should return content."""
        pdf_path = tmp_path / "digital.pdf"
        create_digital_pdf(pdf_path)

        with PDFReader(str(pdf_path)) as reader:
            data = reader.extract_text_from_page(0)
            assert data['text'].strip() != ""
            assert data['is_scanned'] is False
            assert data['page_num'] == 0

    def test_scanned_page_detection(self, tmp_path):
        """A page with no text should be detected as scanned."""
        pdf_path = tmp_path / "scanned.pdf"
        create_empty_pdf(pdf_path)

        with PDFReader(str(pdf_path)) as reader:
            data = reader.extract_text_from_page(0)
            assert data['is_scanned'] is True

    def test_extract_page_out_of_range_raises(self, tmp_path):
        """Extracting from an invalid page number should raise ValueError."""
        pdf_path = tmp_path / "single.pdf"
        create_digital_pdf(pdf_path)

        with PDFReader(str(pdf_path)) as reader:
            with pytest.raises(ValueError):
                reader.extract_text_from_page(999)
            with pytest.raises(ValueError):
                reader.extract_text_from_page(-1)

    def test_convert_page_to_image(self, tmp_path):
        """Page-to-image conversion should return a PIL Image."""
        pdf_path = tmp_path / "image_test.pdf"
        create_digital_pdf(pdf_path)

        with PDFReader(str(pdf_path)) as reader:
            img = reader.convert_page_to_image(0, dpi=150)
            assert isinstance(img, Image.Image)
            assert img.width > 0
            assert img.height > 0

    def test_get_page_dimensions(self, tmp_path):
        """Page dimensions should be standard A4 size (approximately)."""
        pdf_path = tmp_path / "dims.pdf"
        create_digital_pdf(pdf_path)

        with PDFReader(str(pdf_path)) as reader:
            width, height = reader.get_page_dimensions(0)
            # Standard A4 is 595 x 842 points
            assert 500 < width < 700
            assert 700 < height < 900

    def test_context_manager(self, tmp_path):
        """PDFReader should work as a context manager and close properly."""
        pdf_path = tmp_path / "ctx.pdf"
        create_digital_pdf(pdf_path)

        reader = PDFReader(str(pdf_path))
        reader.__enter__()
        assert reader.page_count == 1
        reader.__exit__(None, None, None)
