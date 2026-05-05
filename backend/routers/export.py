import logging
import urllib.parse

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from models.schemas import ExportRequest
from services.excel_service import generate_excel

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/export")
async def export_excel(payload: ExportRequest):
    try:
        excel_bytes = generate_excel(payload.data)
    except Exception as exc:
        logger.exception("Excel generation failed")
        raise HTTPException(status_code=500, detail=f"Error generando Excel: {exc}") from exc

    patient_name = (payload.data.nombre_paciente or "paciente").replace(" ", "_")
    filename = payload.filename or f"historia_clinica_{patient_name}.xlsx"
    encoded = urllib.parse.quote(filename)

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded}",
            "Content-Length": str(len(excel_bytes)),
        },
    )
