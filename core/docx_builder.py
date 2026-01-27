"""
DOCX generation module with full RTL support.
Creates Microsoft Word-compatible documents with proper Arabic rendering.
"""
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from typing import Optional, List, Dict

from core.arabic_processor import ArabicProcessor
from core.table_handler import TableHandler


class DOCXBuilder:
    """
    Builds RTL-compliant DOCX files with Arabic text support.
    """
    
    def __init__(self, 
                 font_name: str = "Arial",
                 preserve_diacritics: bool = True):
        """
        Initialize DOCX builder.
        
        Args:
            font_name: Font name for Arabic text (default: Arial)
            preserve_diacritics: Whether to preserve diacritics
        """
        self.font_name = font_name
        self.arabic_processor = ArabicProcessor(preserve_diacritics=preserve_diacritics)
        self.table_handler = TableHandler(self.arabic_processor)
        self.doc: Optional[Document] = None
    
    def create_document(self) -> Document:
        """
        Create a new DOCX document.
        
        Returns:
            Document object
        """
        self.doc = Document()
        return self.doc
    
    def add_rtl_paragraph(self, 
                         text: str, 
                         font_name: Optional[str] = None,
                         font_size: int = 11) -> None:
        """
        Add a right-to-left paragraph with Arabic text support.
        
        Args:
            text: Text content
            font_name: Font name (defaults to instance font_name)
            font_size: Font size in points
        """
        if not self.doc:
            raise RuntimeError("Document not created. Call create_document() first.")
        
        font_name = font_name or self.font_name
        
        # Process Arabic text in LOGICAL order for DOCX
        # Word handles shaping and bidi reordering itself
        processed = self.arabic_processor.process_paragraph(text, logical_output=True)
        processed_text = processed['text']
        is_arabic = processed['is_arabic']
        
        # Create paragraph
        p = self.doc.add_paragraph()
        
        # Set RTL if Arabic
        if is_arabic:
            # Enforce RTL at XML level (CRITICAL for Word rendering)
            pPr = p._element.pPr
            if pPr is None:
                pPr = OxmlElement('w:pPr')
                p._element.insert(0, pPr)
            bidi = OxmlElement('w:bidi')
            pPr.append(bidi)
            
            # Set right alignment
            p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        else:
            # Left alignment for non-Arabic text
            p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        
        # Add text with font settings
        run = p.add_run(processed_text)
        run.font.name = font_name
        run.font.size = Pt(font_size)
        
        # Set RTL font property for Arabic
        if is_arabic:
            # Set rFonts (right-to-left font) - critical for RTL rendering
            rPr = run._element.rPr
            if rPr is None:
                rPr = OxmlElement('w:rPr')
                run._element.insert(0, rPr)
            rFonts = OxmlElement('w:rFonts')
            rFonts.set(qn('w:ascii'), font_name)
            rFonts.set(qn('w:hAnsi'), font_name)
            rFonts.set(qn('w:cs'), font_name)
            rFonts.set(qn('w:hint'), 'cs')  # Hint that this run contains complex script text
            rPr.append(rFonts)
    
    def add_mixed_paragraph(self, 
                           text: str,
                           font_name: Optional[str] = None,
                           font_size: int = 11) -> None:
        """
        Add a paragraph that may contain mixed Arabic and Latin text.
        Automatically detects script and applies appropriate formatting.
        
        Args:
            text: Text content (may be mixed)
            font_name: Font name
            font_size: Font size in points
        """
        if not self.doc:
            raise RuntimeError("Document not created. Call create_document() first.")
        
        font_name = font_name or self.font_name
        
        # Process text in LOGICAL order for Word
        processed = self.arabic_processor.process_paragraph(text, logical_output=True)
        processed_text = processed['text']
        is_arabic = processed['is_arabic']
        
        # Create paragraph
        p = self.doc.add_paragraph()
        
        # For mixed text, use RTL if primarily Arabic
        if is_arabic:
            # Paragraph level RTL
            pPr = p._element.pPr
            if pPr is None:
                pPr = OxmlElement('w:pPr')
                p._element.insert(0, pPr)
            bidi = OxmlElement('w:bidi')
            pPr.append(bidi)
            p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
            
            # Add text with run level RTL properties
            run = p.add_run(processed_text)
            run.font.name = font_name
            run.font.size = Pt(font_size)
            
            rPr = run._element.rPr
            if rPr is None:
                rPr = OxmlElement('w:rPr')
                run._element.insert(0, rPr)
            # Set complex script properties
            rtl = OxmlElement('w:rtl')
            rPr.append(rtl)
            
            rFonts = OxmlElement('w:rFonts')
            rFonts.set(qn('w:ascii'), font_name)
            rFonts.set(qn('w:hAnsi'), font_name)
            rFonts.set(qn('w:cs'), font_name)
            rPr.append(rFonts)
        else:
            p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
            run = p.add_run(processed_text)
            run.font.name = font_name
            run.font.size = Pt(font_size)
    
    def add_table(self, table_data: Dict) -> None:
        """
        Add a table to the document.
        
        Args:
            table_data: Table data dictionary from OCR or text extraction
        """
        if not self.doc:
            raise RuntimeError("Document not created. Call create_document() first.")
        
        self.table_handler.process_table_from_ocr(table_data, self.doc)
    
    def add_text_blocks(self, text_blocks: List[Dict]) -> None:
        """
        Add multiple blocks (text or table) to the document.
        
        Args:
            text_blocks: List of block dictionaries:
                [{'text': str, 'type': 'text'}, {'cells': [...], 'type': 'table'}]
        """
        if not self.doc:
            raise RuntimeError("Document not created. Call create_document() first.")
        
        for block in text_blocks:
            b_type = block.get('type', 'text')
            if b_type == 'text':
                text = block.get('text', '').strip()
                if text:
                    self.add_mixed_paragraph(text)
            elif b_type == 'table':
                self.add_table(block)
    
    def save(self, output_path: str) -> str:
        """
        Save document to file.
        
        Args:
            output_path: Path to save DOCX file
            
        Returns:
            Path to saved file
        """
        if not self.doc:
            raise RuntimeError("Document not created. Call create_document() first.")
        
        self.doc.save(output_path)
        return output_path

