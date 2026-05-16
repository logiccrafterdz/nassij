import pytest
import os
from pathlib import Path
from cli import convert_pdf_to_docx
import fitz

def create_dummy_pdf(path):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello World Nassij Test", fontsize=12)
    doc.save(path)
    doc.close()

def test_convert_pdf_to_docx(tmp_path):
    input_pdf = tmp_path / "input.pdf"
    output_docx = tmp_path / "output.docx"
    
    create_dummy_pdf(str(input_pdf))
    
    # Test scan mode
    success = convert_pdf_to_docx(
        input_pdf=str(input_pdf),
        output_docx=str(output_docx),
        mode='scan',
        generate_proof=False
    )
    
    assert success is True
    assert output_docx.exists()

def test_convert_with_proof(tmp_path):
    input_pdf = tmp_path / "input2.pdf"
    output_docx = tmp_path / "output2.docx"
    
    create_dummy_pdf(str(input_pdf))
    
    success = convert_pdf_to_docx(
        input_pdf=str(input_pdf),
        output_docx=str(output_docx),
        mode='scan',
        generate_proof=True
    )
    
    assert success is True
    assert output_docx.exists()
    
    proof_path = Path(str(output_docx) + ".nassij-proof")
    assert proof_path.exists()
