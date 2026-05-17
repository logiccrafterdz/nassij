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
