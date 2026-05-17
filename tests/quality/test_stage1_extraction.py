import pytest
from unittest.mock import Mock
from core.scanner import NassijScanner

class TestStage1Extraction:
    """
    Stage 1 Tests: Verify that PDF extraction accurately captures the original structure,
    content, and reading order without loss or reversal.
    """
    
    def test_arabic_word_order_in_line(self):
        """Test B1: Arabic words should remain in their correct logical order."""
        # Mock a rawdict response where the words are already in logical order
        # (which is how most modern PDFs store Arabic)
        mock_page = Mock()
        mock_page.get_text.return_value = {
            "blocks": [{
                "type": 0, "bbox": [0, 0, 100, 20],
                "lines": [{
                    "bbox": [0, 0, 100, 20],
                    "spans": [
                        {"bbox": [70, 0, 100, 20], "chars": [{"c": c} for c in "بسم "]},
                        {"bbox": [40, 0, 70, 20], "chars": [{"c": c} for c in "الله "]},
                        {"bbox": [0, 0, 40, 20], "chars": [{"c": c} for c in "الرحمن"]}
                    ]
                }]
            }]
        }
        mock_page.find_tables.return_value = []
        
        scanner = NassijScanner()
        blocks = scanner.scan_page(mock_page)
        
        extracted = " ".join(b["text"] for b in blocks if b["type"] != "table")
        
        # Verify word order is preserved as logical (بسم then الله then الرحمن)
        # Even though "بسم" has a higher X coordinate (70) than "الرحمن" (0),
        # they shouldn't be blindly sorted by X if they are already logical.
        assert "بسم" in extracted
        assert "الله" in extracted
        assert "الرحمن" in extracted
        
        pos1 = extracted.find("بسم")
        pos2 = extracted.find("الله")
        pos3 = extracted.find("الرحمن")
        
        assert pos1 < pos2 < pos3, f"Words reversed! Output: {extracted}"

    def test_mixed_arabic_english_line(self):
        """Test B1: Mixed content should preserve logical order."""
        mock_page = Mock()
        mock_page.get_text.return_value = {
            "blocks": [{
                "type": 0, "bbox": [0, 0, 100, 20],
                "lines": [{
                    "bbox": [0, 0, 100, 20],
                    "spans": [
                        {"bbox": [70, 0, 100, 20], "chars": [{"c": c} for c in "اسمي "]},
                        {"bbox": [40, 0, 70, 20], "chars": [{"c": c} for c in "Ahmed "]},
                        {"bbox": [0, 0, 40, 20], "chars": [{"c": c} for c in "وعمري"]}
                    ]
                }]
            }]
        }
        mock_page.find_tables.return_value = []
        
        scanner = NassijScanner()
        blocks = scanner.scan_page(mock_page)
        extracted = " ".join(b["text"] for b in blocks if b["type"] != "table")
        
        assert "اسمي" in extracted
        assert "Ahmed" in extracted
        assert "وعمري" in extracted
        
        pos1 = extracted.find("اسمي")
        pos2 = extracted.find("Ahmed")
        pos3 = extracted.find("وعمري")
        
        assert pos1 < pos2 < pos3, f"Mixed words rearranged! Output: {extracted}"

    def test_separate_paragraphs(self):
        """Test B2: Ensure distinct paragraphs are not merged into a single block without newlines."""
        mock_page = Mock()
        mock_page.get_text.return_value = {
            "blocks": [{
                "type": 0, "bbox": [0, 0, 100, 50],
                "lines": [
                    {
                        "bbox": [0, 0, 100, 20],
                        "spans": [{"bbox": [0, 0, 100, 20], "chars": [{"c": c} for c in "السطر الأول"]}]
                    },
                    {
                        "bbox": [0, 30, 100, 50],
                        "spans": [{"bbox": [0, 30, 100, 50], "chars": [{"c": c} for c in "السطر الثاني"]}]
                    }
                ]
            }]
        }
        mock_page.find_tables.return_value = []
        
        scanner = NassijScanner()
        blocks = scanner.scan_page(mock_page)
        text_blocks = [b for b in blocks if b["type"] in ("paragraph", "heading")]
        
        assert len(text_blocks) == 1
        # The text inside the block should preserve the newline between lines
        text = text_blocks[0]["text"]
        assert "السطر الأول" in text
        assert "السطر الثاني" in text
        assert "\n" in text, f"Lines were merged with a space instead of newline: {repr(text)}"
