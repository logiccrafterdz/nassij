"""
Setup script for Nassij.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="nassij",
    version="1.0.0",
    description="High-accuracy PDF-to-DOCX converter specialized for Arabic language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Nassij Contributors",
    url="https://github.com/yourusername/nassij",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "PyMuPDF>=1.23.0",
        "paddleocr>=2.7.0",
        "python-bidi>=0.4.2",
        "arabic-reshaper>=3.0.0",
        "python-docx>=1.1.0",
        "Pillow>=10.0.0",
        "regex>=2023.10.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ],
        "langdetect": [
            "polyglot>=16.7.4",
            "langdetect>=1.0.9",
        ],
    },
    entry_points={
        "console_scripts": [
            "nassij=cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Processing :: Markup",
        "Topic :: Office/Business",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ],
)

