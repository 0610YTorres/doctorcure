import io
import re
import zipfile
import logging
from pathlib import Path

from openpyxl import load_workbook

from models.schemas import PatientData

logger = logging.getLogger(__name__)

TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "plantilla_comite_tumores.xlsx"

# Fragmentos XML que openpyxl elimina al guardar (imagen EMF del encabezado)
_REL_DRAWING = (
    '<Relationship Id="rId2" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing" '
    'Target="../drawings/drawing1.xml"/>'
)
_TAG_DRAWING  = '<drawing r:id="rId2"/>'
_CT_EMF       = '<Default Extension="emf" ContentType="image/x-emf"/>'
_CT_DRAWING   = (
    '<Override PartName="/xl/drawings/drawing1.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.drawing+xml"/>'
)
# Archivos del template que deben copiarse intactos al output
_COPY_FROM_TEMPLATE = {
    "xl/media/image1.emf",
    "xl/drawings/drawing1.xml",
    "xl/drawings/_rels/drawing1.xml.rels",
}


def generate_excel(data: PatientData) -> bytes:
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Plantilla no encontrada en {TEMPLATE_PATH}. "
            "Copie el archivo a backend/templates/plantilla_comite_tumores.xlsx"
        )

    # ── 1. Cargar plantilla y rellenar celdas ──────────────────────────────────
    wb = load_workbook(TEMPLATE_PATH)
    ws = wb["Hoja1"]

    def put(cell: str, value):
        if value:
            ws[cell] = str(value).strip()

    # Sección I — Identificación
    put("F4",  data.documento)          # Historia Clínica No. = CC

    if data.fecha_atencion:             # Fecha atención → D / M / A
        d, m, a = _split_date(data.fecha_atencion)
        put("J4", d); put("K4", m); put("L4", a)

    put("P4",  data.edad)
    put("D6",  data.nombre)
    put("J6",  data.apellidos)
    put("F8",  data.medico_tratante)
    put("P8",  data.especialidad)
    put("E10", data.fecha_diagnostico)
    put("J10", data.entidad)

    # Sección II — Resumen
    put("B14", data.resumen_historia)

    # Sección III — Diagnóstico
    put("G25", data.diagnostico_clinico)
    put("N25", data.diagnostico_patologico)

    put("C27", data.tnm_t)
    put("E27", data.tnm_n)
    put("G27", data.tnm_m)
    put("I27", data.estadificacion)
    # J27=REH, L27=HER2, N27=KI67 → vacíos

    # Imágenes
    put("D31", data.ecografia)
    put("F31", data.tac)
    put("H31", data.rmn)
    put("J31", data.pet)
    put("O31", data.mamografia)
    put("B34", data.informes_imagenes)

    # Tratamientos
    put("D38", data.cirugia_recibio)
    put("F38", data.cirugia_fecha)
    put("J38", data.cirugia_tipo)

    put("E40", data.quimioterapia_recibio)
    put("I40", data.quimioterapia_esquema)

    put("E42", data.radioterapia_recibio)
    put("G42", data.radioterapia_dosis)

    put("E44", data.hormonoterapia_recibio)
    put("G44", data.hormonoterapia_tipo)

    # ── 2. Guardar a buffer (openpyxl descarta la imagen EMF aquí) ─────────────
    buf = io.BytesIO()
    wb.save(buf)

    # ── 3. Restaurar cabecera (imagen + drawing XML) desde la plantilla ────────
    return _restore_header(buf.getvalue(), TEMPLATE_PATH)


def _restore_header(output_bytes: bytes, template_path: Path) -> bytes:
    """
    Copia de vuelta los archivos de imagen/drawing que openpyxl eliminó,
    y parchea los XML de relaciones para que Excel vuelva a mostrar el encabezado.
    """
    out_io  = io.BytesIO(output_bytes)
    res_io  = io.BytesIO()

    with (
        zipfile.ZipFile(template_path, "r") as tmpl,
        zipfile.ZipFile(out_io, "r")        as out,
        zipfile.ZipFile(res_io, "w", zipfile.ZIP_DEFLATED) as res,
    ):
        template_files = {n: tmpl.read(n) for n in tmpl.namelist()}
        output_names   = set(out.namelist())

        # Reescribir archivos del output con parches donde sea necesario
        for name in out.namelist():
            data = out.read(name)

            if name == "xl/worksheets/_rels/sheet1.xml.rels":
                text = data.decode("utf-8")
                if "drawing" not in text:
                    text = text.replace("</Relationships>",
                                        f"{_REL_DRAWING}</Relationships>")
                data = text.encode("utf-8")

            elif name == "xl/worksheets/sheet1.xml":
                text = data.decode("utf-8")
                # openpyxl omite xmlns:r cuando no hay drawing; sin él
                # <drawing r:id="..."/> genera "Prefijo no declarado" en Excel.
                R_NS = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
                if R_NS not in text:
                    text = text.replace("<worksheet ", f"<worksheet {R_NS} ", 1)
                if _TAG_DRAWING not in text:
                    text = text.replace("</worksheet>",
                                        f"{_TAG_DRAWING}</worksheet>")
                data = text.encode("utf-8")

            elif name == "[Content_Types].xml":
                text = data.decode("utf-8")
                if _CT_EMF not in text:
                    text = text.replace("</Types>", f"{_CT_EMF}</Types>")
                if _CT_DRAWING not in text:
                    text = text.replace("</Types>", f"{_CT_DRAWING}</Types>")
                data = text.encode("utf-8")

            res.writestr(name, data)

        # Agregar archivos del template que openpyxl omitió (imagen + drawings)
        for tname in _COPY_FROM_TEMPLATE:
            if tname in template_files and tname not in output_names:
                res.writestr(tname, template_files[tname])

    return res_io.getvalue()


def _split_date(date_str: str) -> tuple[str, str, str]:
    """Devuelve (día, mes, año) desde varios formatos de fecha."""
    date_str = date_str.strip()

    # "2025 - Enero - 20"
    m = re.match(r"(\d{4})\s*[-–]\s*(\w+)\s*[-–]\s*(\d{1,2})", date_str, re.IGNORECASE)
    if m:
        return m.group(3).zfill(2), _month_to_num(m.group(2)), m.group(1)

    # ISO YYYY-MM-DD
    m = re.match(r"(\d{4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})", date_str)
    if m:
        return m.group(3).zfill(2), m.group(2).zfill(2), m.group(1)

    # DD/MM/YYYY
    m = re.match(r"(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})", date_str)
    if m:
        return m.group(1).zfill(2), m.group(2).zfill(2), m.group(3)

    return date_str, "", ""


def _month_to_num(name: str) -> str:
    return {
        "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
        "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
        "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12",
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12",
    }.get(name.lower(), name)
