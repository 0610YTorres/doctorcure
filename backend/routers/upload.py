import logging

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from models.schemas import ExtractionResult
from services.field_extractor import extract_fields
from services.pdf_extractor import extract_text_from_pdf

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/upload", response_model=ExtractionResult)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos PDF")

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="El archivo supera el límite de 20 MB")

    if len(content) < 100:
        raise HTTPException(status_code=400, detail="El archivo PDF está vacío o dañado")

    try:
        raw_text, method = extract_text_from_pdf(content)
    except Exception as exc:
        logger.exception("PDF extraction failed")
        raise HTTPException(status_code=422, detail=f"No se pudo procesar el PDF: {exc}") from exc

    if not raw_text.strip():
        return ExtractionResult(
            success=False,
            data={},
            raw_text="",
            method=method,
            warnings=["No se pudo extraer texto del PDF. Verifique que no sea una imagen sin capa de texto."],
        )

    try:
        patient_data, confidence, warnings = extract_fields(raw_text)
    except Exception as exc:
        logger.exception("Field extraction failed")
        raise HTTPException(status_code=500, detail=f"Error extrayendo campos: {exc}") from exc

    return ExtractionResult(
        success=True,
        data=patient_data,
        raw_text=raw_text[:5000],
        confidence=confidence,
        warnings=warnings,
        method=method,
    )
