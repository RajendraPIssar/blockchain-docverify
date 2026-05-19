"""
services/fraud_service.py
--------------------------
Simple AI fraud detection for uploaded documents.
Checks 4 signals and returns a fraud score from 0.0 to 1.0.

Score guide:
  0.0 - 0.29  →  Low risk   — auto registered on blockchain
  0.3 - 0.69  →  Medium risk — flagged for admin review
  0.7 - 1.0   →  High risk   — rejected, not registered
"""

import re

# Try to import PyMuPDF for PDF analysis
try:
    import fitz  # PyMuPDF
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("Warning: PyMuPDF not installed. PDF fraud detection disabled.")


def analyse(file_bytes: bytes, filename: str) -> float:
    """
    Analyse a document and return a fraud score (0.0 – 1.0).
    Higher score = more suspicious.
    """
    if not PDF_SUPPORT or not filename.lower().endswith(".pdf"):
        return 0.05  # Non-PDFs get a clean score by default

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception:
        return 0.1  # If we can not read the PDF, treat it as low risk

    scores = []

    # ── Check 1: Font anomaly ─────────────────────────────────────────────────
    # More than 6 unique fonts per page suggests copy-paste manipulation
    font_counts = []
    for page in doc:
        fonts = page.get_fonts(full=True)
        unique_fonts = len(set(f[3] for f in fonts))
        font_counts.append(unique_fonts)
    avg_fonts = sum(font_counts) / max(len(font_counts), 1)
    font_score = min(1.0, max(0.0, (avg_fonts - 4) / 8))
    scores.append(font_score)

    # ── Check 2: Image count ──────────────────────────────────────────────────
    # Lots of embedded images may indicate forged content pasted in
    total_images = sum(len(page.get_images()) for page in doc)
    image_score  = min(1.0, total_images / 15)
    scores.append(image_score * 0.7)

    # ── Check 3: Text density ─────────────────────────────────────────────────
    # Very sparse text suggests a scanned photo of a fake document
    text_lengths = [len(page.get_text()) for page in doc]
    avg_text     = sum(text_lengths) / max(len(text_lengths), 1)
    density_score = 0.5 if avg_text < 50 else 0.0
    scores.append(density_score)

    # ── Check 4: Suspicious keywords ─────────────────────────────────────────
    full_text  = " ".join(page.get_text() for page in doc).lower()
    bad_words  = ["lorem ipsum", "specimen", "sample document", "draft copy", "not valid"]
    kw_score   = 0.8 if any(w in full_text for w in bad_words) else 0.0
    scores.append(kw_score)

    final = sum(scores) / len(scores)
    return round(min(1.0, final), 4)
