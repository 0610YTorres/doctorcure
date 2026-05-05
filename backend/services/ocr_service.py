import logging

logger = logging.getLogger(__name__)


def ocr_pdf(file_content: bytes) -> str:
    """
    Render each PDF page via pdf2image (needs Poppler) and OCR with Tesseract.
    Falls back to a helpful error if dependencies are missing.
    """
    try:
        import pytesseract
        from pdf2image import convert_from_bytes
    except ImportError as exc:
        raise RuntimeError(
            f"OCR requiere 'pytesseract' y 'pdf2image' instalados, y Poppler en PATH. Error: {exc}"
        ) from exc

    try:
        images = convert_from_bytes(file_content, dpi=300)
    except Exception as exc:
        raise RuntimeError(
            f"pdf2image falló. ¿Está Poppler instalado y en PATH? Error: {exc}"
        ) from exc

    parts: list[str] = []
    for img in images:
        page_text = pytesseract.image_to_string(
            img,
            lang="spa+eng",
            config="--oem 3 --psm 6",
        )
        parts.append(page_text)

    return "\n".join(parts)
