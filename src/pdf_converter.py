import logging
from pathlib import Path

from pdfminer.high_level import extract_text

# pdfminer logs non-fatal font-parsing issues (e.g. FontBBox) at WARNING level.
# Suppress them so they don't pollute the run output.
_pdfminer_log = logging.getLogger("pdfminer")


def pdf_to_text(pdf_path: Path) -> str:
    """Extract plain text from a PDF file. Returns empty string on failure."""
    prev_level = _pdfminer_log.level
    _pdfminer_log.setLevel(logging.ERROR)
    try:
        return extract_text(str(pdf_path))
    except Exception as exc:
        print(f"[warn] Could not extract text from {pdf_path.name}: {exc}")
        return ""
    finally:
        _pdfminer_log.setLevel(prev_level)
