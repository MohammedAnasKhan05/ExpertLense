"""
ExpertLens AI — Document Text Extractor

Extracts plain text from multi-format transcript files:
- .txt (Plain Text with UTF-8 / Latin-1 / CP1252 fallback)
- .pdf (Adobe PDF via pypdf)
- .docx (Microsoft Word via python-docx)
- .doc (Legacy Word fallback)
"""

import io
import os
import re
from typing import Optional


def extract_text_from_file(filename: str, content: bytes) -> str:
    """
    Extract readable text content from a file buffer.

    Args:
        filename: Original file name (used for extension detection)
        content: Raw binary content of the file

    Returns:
        Extracted plain text string

    Raises:
        ValueError: If file type is unsupported or corrupted
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".txt":
        return _extract_txt(content)
    elif ext == ".pdf":
        return _extract_pdf(content)
    elif ext == ".docx":
        return _extract_docx(content)
    elif ext == ".doc":
        return _extract_doc(content)
    else:
        raise ValueError(
            f"Unsupported file format '{ext}'. Supported formats: .txt, .pdf, .docx, .doc"
        )


def _extract_txt(content: bytes) -> str:
    """Extract text from plain text file with multiple encoding fallbacks."""
    for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return content.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    raise ValueError("Unable to decode text file. Ensure it is encoded in UTF-8 or standard text encoding.")


def _extract_pdf(content: bytes) -> str:
    """Extract text from PDF pages using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(content))
        text_parts = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text.strip())

        extracted = "\n\n".join(text_parts).strip()
        if not extracted:
            raise ValueError("No extractable text found in PDF. (Scanned image-only PDFs require OCR).")
        return extracted
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Failed to read PDF document: {str(e)}")


def _extract_docx(content: bytes) -> str:
    """Extract text from Microsoft Word DOCX document."""
    try:
        import docx
        doc = docx.Document(io.BytesIO(content))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

        # Also extract table text if present
        for table in doc.tables:
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if cells:
                    paragraphs.append(" | ".join(cells))

        extracted = "\n\n".join(paragraphs).strip()
        if not extracted:
            raise ValueError("No extractable text found in DOCX document.")
        return extracted
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Failed to read DOCX document: {str(e)}")


def _extract_doc(content: bytes) -> str:
    """Attempt extraction from legacy .doc file."""
    # First attempt: Many .doc files are actually docx format
    try:
        return _extract_docx(content)
    except Exception:
        pass

    # Fallback: Extract ASCII / UTF-8 printable string runs from binary stream
    try:
        # Look for sequences of printable characters
        printable_pattern = re.compile(rb'[\x20-\x7E\r\n\t]{4,}')
        matches = printable_pattern.findall(content)
        decoded_parts = []
        for m in matches:
            try:
                decoded_parts.append(m.decode('utf-8', errors='ignore'))
            except Exception:
                continue

        extracted = "\n".join(decoded_parts).strip()
        if len(extracted) > 100:
            return extracted
    except Exception:
        pass

    raise ValueError(
        "Legacy .doc binary format cannot be parsed reliably. Please save or convert the file to .docx, .pdf, or .txt."
    )
