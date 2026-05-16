"""
Nassij: High-accuracy PDF-to-DOCX converter specialized for Arabic language.
"""

try:
    from cli import convert_pdf_to_docx as convert
except ImportError:
    # When installed as a package, cli may not be in the root namespace
    try:
        from .cli import convert_pdf_to_docx as convert
    except ImportError:
        convert = None

__version__ = "3.0.0"
__all__ = ["convert"]
