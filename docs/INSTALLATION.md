# Installation & Setup

## Prerequisites
- Python 3.9+
- Windows/Linux/macOS

## Core Installation

```bash
# Clone the repository
git clone https://github.com/logiccrafterdz/nassij.git
cd nassij

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install -r requirements.txt
```

## OCR Engines (Optional but Recommended)

Nassij V3 supports three OCR engines. For best results with complex Arabic layouts, we recommend installing Surya OCR.

### 1. Surya OCR (Best for Layout & Accuracy)
```bash
pip install surya-ocr
```
*(Note: Requires PyTorch. Follow PyTorch installation instructions for your OS to get GPU support.)*

### 2. EasyOCR (Fallback 1)
```bash
pip install easyocr
```

### 3. PaddleOCR (Fallback 2)
```bash
pip install paddlepaddle paddleocr
```

## Web Interface

If you wish to use the FastAPI web interface:

```bash
pip install fastapi uvicorn python-multipart
cd web
python app.py
# Access at http://localhost:8000
```
