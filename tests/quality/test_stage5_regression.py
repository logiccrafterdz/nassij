import pytest
from core.scanner import NassijScanner
from unittest.mock import Mock

class TestStage5Regression:
    """
    Stage 5 Tests: Edge cases and regression tests to ensure the system doesn't crash
    on unexpected input.
    """
    
    def test_empty_page(self):
        """Test R1: Empty pages should not crash the scanner."""
        mock_page = Mock()
        mock_page.get_text.return_value = {"blocks": []}
        mock_page.find_tables.return_value = []
        
        scanner = NassijScanner()
        blocks = scanner.scan_page(mock_page)
        
        assert len(blocks) == 0

    def test_single_character(self):
        """Test R2: Single character pages should process correctly."""
        mock_page = Mock()
        mock_page.get_text.return_value = {
            "blocks": [{
                "type": 0, "bbox": [0, 0, 10, 10],
                "lines": [{
                    "bbox": [0, 0, 10, 10],
                    "spans": [
                        {"bbox": [0, 0, 10, 10], "chars": [{"c": "ب"}]}
                    ]
                }]
            }]
        }
        mock_page.find_tables.return_value = []
        
        scanner = NassijScanner()
        blocks = scanner.scan_page(mock_page)
        
        assert len(blocks) == 1
        assert blocks[0]["text"] == "ب"

    def test_mangled_cid_corruption(self, pdf_generator):
        """Test R3: Detect CID mapping corruption (e.g., 3+ consecutive Alifs)."""
        from core.pdf_reader import PDFReader
        pdf_path = pdf_generator.with_text("dummy")
        reader = PDFReader(str(pdf_path))
        
        # User provided corrupted text from a broken PDF
        corrupted_text = "يُعدّ االتصال  اددالي  ن  يي  ادنضواضتلا ااسالسايت ادت   بيا يلمتنلس ضاسام ا  ن لتيضس اإلتالس ضاالتصااال ي الساااينل ا   ل  االتصااال  ادتببين ي ضلد  يلدبب   د  ن لبتادن ض يات دالا  ادنسسااااساااات"
        
        is_mangled = reader._is_text_mangled(corrupted_text)
        assert is_mangled is True, "Failed to detect CID corrupted Arabic text"
