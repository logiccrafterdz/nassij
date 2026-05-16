"""
Helper functions for enforcing Right-to-Left (RTL) formatting in DOCX files.
Ensures consistency across paragraphs, runs, and tables.
"""
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def apply_rtl_paragraph(paragraph, alignment=WD_PARAGRAPH_ALIGNMENT.JUSTIFY):
    """Set paragraph-level RTL with strict XML tags."""
    pPr = paragraph._element.get_or_add_pPr()
    bidi = pPr.find(qn('w:bidi'))
    if bidi is None:
        bidi = OxmlElement('w:bidi')
        bidi.set(qn('w:val'), '1')
        pPr.append(bidi)
    paragraph.alignment = alignment

def apply_rtl_run(run, font_name, lang="ar-SA"):
    """Set run-level RTL with font, language, and direction tags."""
    rPr = run._element.get_or_add_rPr()
    
    rtl = rPr.find(qn('w:rtl'))
    if rtl is None:
        rtl = OxmlElement('w:rtl')
        rtl.set(qn('w:val'), '1')
        rPr.append(rtl)
        
    lang_tag = rPr.find(qn('w:lang'))
    if lang_tag is None:
        lang_tag = OxmlElement('w:lang')
        lang_tag.set(qn('w:val'), lang)
        lang_tag.set(qn('w:bidi'), lang)
        rPr.append(lang_tag)
    
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    rFonts.set(qn('w:hint'), 'cs')
    rPr.append(rFonts)

def apply_rtl_table(table):
    """Set table-level RTL properties."""
    tbl = table._element
    tblPr = tbl.tblPr
    if tblPr is None:
        tblPr = OxmlElement('w:tblPr')
        tbl.insert(0, tblPr)
        
    bidiVisual = tblPr.find(qn('w:bidiVisual'))
    if bidiVisual is None:
        bidiVisual = OxmlElement('w:bidiVisual')
        tblPr.append(bidiVisual)
        
    jc = tblPr.find(qn('w:jc'))
    if jc is None:
        jc = OxmlElement('w:jc')
        jc.set(qn('w:val'), 'right')
        tblPr.append(jc)
