import io
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

MIN_TEXT_LENGTH = 80


def extract_text_from_pdf(file_content: bytes) -> Tuple[str, str]:
    """
    Layered extraction: pdfplumber → pypdf → Tesseract OCR.
    Returns (text, method_used).
    """
    text, method = _try_pdfplumber(file_content)
    if _is_sufficient(text):
        return text.strip(), method

    logger.info("pdfplumber insufficient, trying pypdf")
    text, method = _try_pypdf(file_content)
    if _is_sufficient(text):
        return text.strip(), method

    logger.info("pypdf insufficient, attempting OCR")
    text, method = _try_ocr(file_content)
    return text.strip(), method


def _is_sufficient(text: str) -> bool:
    return bool(text) and len(text.strip()) >= MIN_TEXT_LENGTH


def _try_pdfplumber(file_content: bytes) -> Tuple[str, str]:
    try:
        import pdfplumber

        parts: list[str] = []
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    parts.append(page_text)
        return "\n".join(parts), "pdfplumber"
    except Exception as exc:
        logger.warning("pdfplumber failed: %s", exc)
        return "", "pdfplumber_failed"


def _try_pypdf(file_content: bytes) -> Tuple[str, str]:
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(file_content))
        parts: list[str] = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                parts.append(text)
        return "\n".join(parts), "pypdf"
    except Exception as exc:
        logger.warning("pypdf failed: %s", exc)
        return "", "pypdf_failed"


def _try_ocr(file_content: bytes) -> Tuple[str, str]:
    try:
        from services.ocr_service import ocr_pdf

        text = ocr_pdf(file_content)
        return text, "ocr_tesseract"
    except Exception as exc:
        logger.warning("OCR failed: %s", exc)
        return "", "ocr_failed"
