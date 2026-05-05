import re
from typing import Optional

# ─── CIE-10 cancer prefix → description ───────────────────────────────────────
CIE10_CANCER_MAP: dict[str, str] = {
    "C00": "Tumor maligno del labio",
    "C01": "Tumor maligno de la base de la lengua",
    "C02": "Tumor maligno de la lengua",
    "C15": "Tumor maligno del esófago",
    "C16": "Tumor maligno del estómago",
    "C18": "Tumor maligno del colon",
    "C19": "Tumor maligno de la unión rectosigmoidea",
    "C20": "Tumor maligno del recto",
    "C22": "Tumor maligno del hígado",
    "C25": "Tumor maligno del páncreas",
    "C32": "Tumor maligno de la laringe",
    "C33": "Tumor maligno de la tráquea",
    "C34": "Tumor maligno de los bronquios y del pulmón",
    "C43": "Melanoma maligno de la piel",
    "C50": "Tumor maligno de la mama",
    "C53": "Tumor maligno del cuello del útero",
    "C54": "Tumor maligno del cuerpo del útero",
    "C56": "Tumor maligno del ovario",
    "C61": "Tumor maligno de la próstata",
    "C62": "Tumor maligno del testículo",
    "C64": "Tumor maligno del riñón",
    "C67": "Tumor maligno de la vejiga urinaria",
    "C71": "Tumor maligno del encéfalo",
    "C73": "Tumor maligno de la glándula tiroides",
    "C80": "Tumor maligno sin especificación del sitio",
    "C81": "Enfermedad de Hodgkin",
    "C82": "Linfoma no Hodgkin folicular",
    "C83": "Linfoma no Hodgkin difuso",
    "C90": "Mieloma múltiple",
    "C91": "Leucemia linfoide",
    "C92": "Leucemia mieloide",
    "C95": "Leucemia de tipo celular no especificado",
    "D05": "Carcinoma in situ de la mama",
    "D06": "Carcinoma in situ del cuello del útero",
}

# ─── Treatment keyword groups ──────────────────────────────────────────────────
TREATMENT_KEYWORDS: dict[str, list[str]] = {
    "Quimioterapia": ["quimioterapia", "quimio", " qt ", "chemotherapy", "esquema qx", "ciclo"],
    "Radioterapia": ["radioterapia", "radiación", " rt ", "radiation", "braquiterapia"],
    "Cirugía": ["cirugía", "cirugia", "resección", "extirpación", "mastectomía", "histerectomía", "prostatectomía", "lumpectomía"],
    "Inmunoterapia": ["inmunoterapia", "immunotherapy", "checkpoint", "pembrolizumab", "nivolumab"],
    "Hormonoterapia": ["hormonoterapia", "terapia hormonal", "tamoxifeno", "letrozol", "anastrozol", "exemestano"],
    "Terapia dirigida": ["terapia dirigida", "targeted therapy", "erlotinib", "imatinib", "trastuzumab", "bevacizumab"],
}

# ─── Treatment result keyword groups ──────────────────────────────────────────
RESULT_KEYWORDS: dict[str, list[str]] = {
    "Remisión completa": ["remisión completa", "remision completa", "respuesta completa", " rc ", " cr "],
    "Remisión parcial": ["remisión parcial", "remision parcial", "respuesta parcial", " rp ", " pr "],
    "Enfermedad estable": ["enfermedad estable", "estable", " sd ", "stable disease"],
    "Progresión": ["progresión", "progresion", "progresó", "progreso", " pd ", "progression"],
    "Recaída": ["recaída", "recaida", "recurrencia", "relapse"],
    "Fallecido": ["fallecido", "óbito", "obito", "defunción", "deceased"],
}

# ─── Field extraction patterns ─────────────────────────────────────────────────
PATTERNS: dict[str, list[str]] = {
    "nombre_paciente": [
        # "Paciente: CC 22444779 - JUANA LEOTIDES ESPITIA ALVAREZ"
        # Captura hasta fin de línea (no corta por doble espacio dentro del nombre)
        r"(?i)paciente\s*[:\-]\s*(?:[A-Z]{1,3}\.?\s+)?\d[\d\.\s]{3,15}[-–]\s*([A-ZÁÉÍÓÚÑa-záéíóúñ][A-ZÁÉÍÓÚÑa-záéíóúñ\s]+?)(?=[ \t]*[\n\r]|[ \t]*$)",
        r"(?i)nombre\s*(?:completo|del?\s*paciente)?\s*[:\-]\s*([A-ZÁÉÍÓÚÑa-záéíóúñ][A-ZÁÉÍÓÚÑa-záéíóúñ\s,]+?)(?=[ \t]*[\n\r]|[ \t]*$|\s{3,})",
        r"(?i)paciente\s*[:\-]\s*([A-ZÁÉÍÓÚÑa-záéíóúñ][A-ZÁÉÍÓÚÑa-záéíóúñ\s,]+?)(?=[ \t]*[\n\r]|[ \t]*$|\s{3,})",
        r"(?i)sr[a]?\.?\s*[:\-]?\s*([A-ZÁÉÍÓÚÑa-záéíóúñ][A-ZÁÉÍÓÚÑa-záéíóúñ\s,]+?)(?=[ \t]*[\n\r]|[ \t]*$|\s{3,})",
        r"(?i)nombre\s+y\s+apellidos?\s*[:\-]\s*([A-ZÁÉÍÓÚÑa-záéíóúñ][A-ZÁÉÍÓÚÑa-záéíóúñ\s,]+?)(?=[ \t]*[\n\r]|[ \t]*$|\s{3,})",
    ],
    "documento": [
        r"(?i)c\.?\s*c\.?\s*(?:n[°º.]?)?\s*[:\-#]?\s*(\d[\d\.\- ]{4,18}\d)",
        r"(?i)(?:t\.?\s*i\.?|tarjeta\s*de\s*identidad)\s*[:\-#]?\s*(\d[\d\.\- ]{4,18}\d)",
        r"(?i)(?:c\.?\s*e\.?|cédula\s*de\s*extranjería)\s*[:\-#]?\s*(\d[\d\.\- ]{4,18}\d)",
        r"(?i)(?:documento|identificación|nro\.?\s*doc)\s*[:\-#]?\s*(\d[\d\.\- ]{4,18}\d)",
        r"(?i)n[°º]\s*(?:de\s*)?(?:documento|identificación)\s*[:\-]?\s*(\d[\d\.\- ]{4,18}\d)",
    ],
    "tipo_documento": [
        r"(?i)(cédula\s*de\s*ciudadanía|c\.?\s*c\.?)\b",
        r"(?i)(tarjeta\s*de\s*identidad|t\.?\s*i\.?)\b",
        r"(?i)(cédula\s*de\s*extranjería|c\.?\s*e\.?)\b",
        r"(?i)(pasaporte)\b",
    ],
    "edad": [
        r"(?i)edad\s*[:\-]?\s*(\d{1,3})\s*(?:años?|a[ñn]os?)?",
        r"(?i)paciente\s*(?:de|con)?\s*(\d{1,3})\s*años?",
        r"(?i)(\d{1,3})\s*años?\s*(?:de\s*edad)?(?:\s*de\s*edad)?",
    ],
    "sexo": [
        r"(?i)sexo\s*[:\-]\s*(masculino|femenino|\bm\b|\bf\b)",
        r"(?i)género\s*[:\-]\s*(masculino|femenino|\bm\b|\bf\b)",
        r"(?i)\b(masculino|femenino)\b",
    ],
    "diagnostico_cie10": [
        # Máxima prioridad: diagnóstico principal explícito "Principal: C20X"
        r"(?i)\bprincipal\s*[:\-]\s*([A-Z]\d{2}[A-Z0-9]?)\b",
        # CIE-10 con código explícito
        r"(?i)(?:CIE[\s\-]?10|c[oó]d(?:igo)?\s*CIE)\s*[:\-]?\s*([A-Z]\d{2}[A-Z0-9]?(?:\.\d{1,2})?)",
        r"(?i)(?:diagnóstico|dx\.?)\s*[:\-]\s*([A-Z]\d{2}[A-Z0-9]?(?:\.\d{1,2})?)",
        # Fallback amplio: solo como último recurso
        r"\b([C-D]\d{2}[A-Z0-9]?(?:\.\d{1,2})?)\b",
    ],
    "estadificacion": [
        # "Estado Clínico: IIIB" — forma más específica usada en SISPRO/SIVIGILA
        r"(?i)estado\s+cl[ií]nico\s*[:\-]\s*((?:I{1,3}V?|IV)[ABC]?)\b",
        # "ec IIIB" — abreviatura oncológica colombiana
        r"(?i)\bec\s+((?:I{1,3}V?|IV)[ABC]?)\b",
        r"(?i)estadio\s*(?:cl[ií]nico|patol[oó]gico|tumoral)?\s*[:\-]\s*((?:I{1,3}V?|IV)[ABC]?)\b",
        r"(?i)(?:estadificaci[oó]n|estadiaje|stage)\s*[:\-]\s*((?:I{1,3}V?|IV)[ABC]?)\b",
        r"(?i)estadio\s+([1-4][ABC]?)",
        r"(?i)\bT(\d)[a-c]?\s*N(\d)\s*M([01])\b",
    ],
    "fecha_diagnostico": [
        # "Fecha de ingreso ... diagnóstico ... remisión: 2025 - Enero - 20"
        r"(?i)fecha\s+de\s+ingreso.*?(?:diagn[oó]stico|remisi[oó]n)\s*[:\-]\s*(\d{4}\s*[-–]\s*\w+\s*[-–]\s*\d{1,2})",
        # ISO "2025-03-05"
        r"(?i)fecha\s+de\s+(?:estudio\s+de\s+patolog[ií]a|patolog[ií]a)\s*[:\-]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})",
        # Formatos clásicos
        r"(?i)fecha\s*(?:de)?\s*(?:diagn[oó]stico|dx\.?)\s*[:\-]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        r"(?i)fecha\s*(?:de)?\s*(?:diagn[oó]stico|dx\.?)\s*[:\-]\s*(\d{1,2}\s+de\s+\w+\s+(?:de\s+)?\d{4})",
        r"(?i)diagnosticado\s+(?:el\s+)?(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
    ],
    "medico_tratante": [
        # ── Máxima prioridad: bloque de firma al final del documento ──────────
        # Formato: NOMBRE EN MAYÚSCULAS \n ESPECIALIDAD \n CC.NNNNNN - REGNNNNNN
        r"([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{8,60}?)\s*[\n\r]+\s*[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{3,40}?[\n\r]+\s*CC\.?\s*\d{5,}",
        # Variante: nombre seguido directamente de CC. en la misma o siguiente línea
        r"([A-ZÁÉÍÓÚÑ]{2,}(?:\s+[A-ZÁÉÍÓÚÑ]{2,}){2,5})\s*[\n\r]+\s*CC\.?\s*\d{5,}",
        # ── Fallbacks: etiquetas explícitas (pueden traer el médico del header) ─
        r"(?i)m[eé]dic[oa]\s*(?:tratante|trat\.?)\s*[:\-]\s*([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\. ]+?)(?=\n|\r|$|\s{2,})",
        r"(?i)oncol[oó]g[oa]\s*(?:tratante)?\s*[:\-]\s*([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\. ]+?)(?=\n|\r|$|\s{2,})",
        r"(?i)(?:dr\.?|dra\.?)\s+([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\. ]+?)(?=\n|\r|$|\s{2,}|\bCC\b|\bm[eé]dic)",
        r"(?i)responsable\s*[:\-]\s*([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\. ]+?)(?=\n|\r|$|\s{2,})",
    ],
    "tratamiento_inicial": [
        r"(?i)tratamiento\s*inicial\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]|\Z)",
        r"(?i)primera\s*l[ií]nea\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]|\Z)",
        r"(?i)plan\s*de\s*tratamiento\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]|\Z)",
        r"(?i)tratamiento\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]|\Z)",
    ],
    "resultado_tratamiento": [
        r"(?i)resultado\s*(?:del?\s*tratamiento)?\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]|\Z)",
        r"(?i)respuesta\s*(?:al\s*tratamiento)?\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]|\Z)",
        r"(?i)evoluci[oó]n\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]|\Z)",
        r"(?i)seguimiento\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]|\Z)",
    ],
    "tipo_cancer": [
        # "Tipo de tumor sólido: CÁNCER DE RECTO"  (cualquier modificador entre tumor/cáncer y los dos puntos)
        r"(?i)tipo\s*(?:de\s*)?(?:tumor|c[aá]ncer|neoplasia)\s*(?:\w+\s*)?[:\-]\s*(.+?)(?=\n|\r|$|\s{2,})",
        r"(?i)(?:c[aá]ncer|tumor|neoplasia)\s+(?:de|del?|maligno\s+de)\s+([\w\sáéíóúñÁÉÍÓÚÑ]+?)(?=\n|\r|$|\s{2,}|,|\.)",
        r"(?i)\b(carcinoma|adenocarcinoma|sarcoma|linfoma|leucemia|melanoma|mieloma)\b\s*([\w\sáéíóúñÁÉÍÓÚÑ]*?)(?=\n|\r|$|,|\.|\s{2,})",
    ],
    "diagnostico_descripcion": [
        # "Principal: C20X - TUMOR MALIGNO DEL RECTO"
        r"(?i)\bprincipal\s*[:\-]\s*[A-Z]\d{2}[A-Z0-9]?\s*[-–]\s*(.+?)(?=\n|\r|$)",
        r"(?i)descripci[oó]n\s*(?:del?\s*)?(?:diagn[oó]stico)?\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]|\Z)",
        r"(?i)(?:diagn[oó]stico|dx\.?)\s*[:\-]\s*(?:[A-Z]\d{2}[A-Z0-9]?(?:\.\d{1,2})?\s+)?(.+?)(?=\n\n|\n[A-Z]|\Z)",
    ],

    # ── Nuevos campos ──────────────────────────────────────────────────────────
    "fecha_atencion": [
        r"(?i)fecha\s+de\s+atenci[oó]n\s*[:\-]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        r"(?i)fecha\s+atenci[oó]n\s*[:\-]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        r"(?i)atenci[oó]n\s*[:\-]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
    ],
    "especialidad": [
        # ── Máxima prioridad: línea entre el nombre y el CC. en bloque de firma ─
        # NOMBRE \n ESPECIALIDAD \n CC.NNNNNN
        r"[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{8,60}?[\n\r]+\s*([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{3,40}?)[\n\r]+\s*CC\.?\s*\d{5,}",
        # ── Fallbacks: etiquetas explícitas ──────────────────────────────────────
        r"(?i)especialidad\s*[:\-]\s*([A-ZÁÉÍÓÚÑA-Za-záéíóúñ\s]+?)(?=\n|\r|$|\s{2,})",
        r"(?i)servicio\s*[:\-]\s*([A-ZÁÉÍÓÚÑA-Za-záéíóúñ\s]+?)(?=\n|\r|$|\s{2,})",
    ],
    "entidad": [
        # Header del documento (primera institución mencionada)
        r"(?i)^([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s]+(?:ltda|s\.a\.s?|e\.s\.e|eps|ips|hospital|cl[ií]nica|centro|instituto|fundaci[oó]n)\.?)(?=\n|\r|$)",
        r"(?i)(?:instituci[oó]n|entidad|ips|hospital|cl[ií]nica|centro\s+m[eé]dic[oa]|centro\s+oncol[oó]gic[oa])\s*[:\-]\s*([A-ZÁÉÍÓÚÑA-Za-záéíóúñ\s,\.]+?)(?=\n|\r|$|\s{2,})",
    ],
    "diagnostico_patologico": [
        r"(?i)(?:diagn[oó]stico\s+patol[oó]gico|resultado\s+de?\s*patolog[ií]a|biopsia|histopatolog[ií]a|informe\s+patol[oó]gico)\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]|\Z)",
        r"(?i)patolog[ií]a\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]|\Z)",
        r"(?i)tipo\s+de\s+estudio.*?diagn[oó]stico.*?[:\-]\s*(.+?)(?=\n|\r|$|\s{2,})",
    ],
    # TNM components
    "tnm_t": [
        r"(?i)\bT([0-4][abc]?)\b",
        r"(?i)T\s*[:\-]\s*([0-4][abc]?)\b",
    ],
    "tnm_n": [
        r"(?i)\bN([0-3][abc]?)\b",
        r"(?i)N\s*[:\-]\s*([0-3][abc]?)\b",
    ],
    "tnm_m": [
        r"(?i)\bM([01][abc]?)\b",
        r"(?i)M\s*[:\-]\s*([01][abc]?)\b",
    ],
    # Imágenes
    "ecografia": [
        r"(?i)ecograf[ií]a\s*(?:abdominal|pélvica|mamaria|renal)?\s*[:\-]\s*(.{5,120}?)(?=\n|\r|$|\bTAC\b|\bRMN\b|\bPET\b)",
        r"(?i)ultrasonido\s*[:\-]\s*(.{5,120}?)(?=\n|\r|$)",
    ],
    "tac": [
        r"(?i)(?:TAC|tomograf[ií]a\s*axial|tomograf[ií]a\s*computarizada?)\s*(?:de\s*\w+\s*)?[:\-]\s*(.{5,150}?)(?=\n|\r|$|\bRMN\b|\bPET\b)",
    ],
    "rmn": [
        r"(?i)(?:RMN|resonancia\s*magn[eé]tica)\s*(?:de\s*\w+\s*)?[:\-]\s*(.{5,150}?)(?=\n|\r|$|\bPET\b)",
    ],
    "pet": [
        r"(?i)(?:PET|PET[\/\-]CT|tomograf[ií]a\s*por\s*emisi[oó]n)\s*[:\-]\s*(.{5,150}?)(?=\n|\r|$)",
    ],
    "mamografia": [
        r"(?i)mamograf[ií]a\s*[:\-]\s*(.{5,120}?)(?=\n|\r|$)",
    ],
    "informes_imagenes": [
        r"(?i)(?:informes?\s*(?:de\s*)?(?:im[aá]genes?|radiol[oó]gicos?|ayudas)|resultados?\s*(?:de\s*)?im[aá]genes?)\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]{2,}|\Z)",
    ],
    # Tratamientos
    "cirugia_fecha": [
        r"(?i)cirug[ií]a.*?(?:fecha|realizada?|practicada?)\s*[:\-]?\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        r"(?i)(?:fecha\s*(?:de\s*)?)?(?:intervenci[oó]n|cirug[ií]a)\s*[:\-]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
    ],
    "cirugia_tipo": [
        r"(?i)tipo\s*(?:de\s*)?cirug[ií]a\s*[:\-]\s*(.+?)(?=\n|\r|$|\s{2,})",
        r"(?i)(?:mastectom[ií]a|histerectom[ií]a|prostatectom[ií]a|resección|colectom[ií]a|lumpectom[ií]a|nefrectom[ií]a|tiroidectom[ií]a)(?:\s+\w+)?",
    ],
    "quimioterapia_esquema": [
        r"(?i)(?:esquema|ciclos?\s*y\s*esquemas?|protocolo|r[eé]gimen)\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]|\Z)",
        r"(?i)quimioterapia.*?(?:esquema|ciclos?)\s*[:\-]\s*(.+?)(?=\n\n|\n[A-Z]|\Z)",
        r"(?i)(\d+\s*ciclos?\s*(?:de\s*)?[\w\s\+\/\-]+?)(?=\n|\r|$|\s{2,})",
    ],
    "radioterapia_dosis": [
        r"(?i)(?:dosis|gray|gy|cgy)\s*[:\-]?\s*(\d+[\d\s\.,]*\s*(?:gray|gy|cgy|rad)?)\b",
        r"(?i)radioterapia.*?(\d+[\d\s\.,]*\s*(?:gray|gy|cgy)\b.{0,40}?)(?=\n|\r|$)",
    ],
    "hormonoterapia_tipo": [
        r"(?i)hormonoterapia\s*[:\-]\s*(.+?)(?=\n|\r|$|\s{2,})",
        r"(?i)(tamoxifeno|letrozol|anastrozol|exemestano|fulvestrant|goserelina|leuprolida)(?:\s+\w+)?",
    ],
}


def normalize_doc_number(doc: str) -> str:
    return re.sub(r"[\.\-\s]", "", doc).strip()


def normalize_sex(sex: str) -> str:
    s = sex.strip().lower()
    if s in ("m", "masculino", "male"):
        return "Masculino"
    if s in ("f", "femenino", "female"):
        return "Femenino"
    return sex.strip().capitalize()


def infer_cancer_type_from_cie10(cie10_code: Optional[str]) -> Optional[str]:
    if not cie10_code:
        return None
    prefix = cie10_code[:3].upper()
    return CIE10_CANCER_MAP.get(prefix)


def infer_cancer_type_from_text(text: str) -> Optional[str]:
    text_lower = text.lower()
    keywords = [
        ("mama", "Cáncer de mama"),
        ("seno ", "Cáncer de mama"),
        ("pulmón", "Cáncer de pulmón"),
        ("pulmon", "Cáncer de pulmón"),
        ("colorrectal", "Cáncer colorrectal"),
        ("colon", "Cáncer de colon"),
        ("recto", "Cáncer de recto"),
        ("próstata", "Cáncer de próstata"),
        ("prostata", "Cáncer de próstata"),
        ("cuello uterino", "Cáncer de cuello uterino"),
        ("cérvix", "Cáncer de cuello uterino"),
        ("cervix", "Cáncer de cuello uterino"),
        ("ovario", "Cáncer de ovario"),
        ("endometrio", "Cáncer de endometrio"),
        ("estómago", "Cáncer de estómago"),
        ("gástrico", "Cáncer gástrico"),
        ("gastrico", "Cáncer gástrico"),
        ("hígado", "Cáncer de hígado"),
        ("hepato", "Cáncer hepático"),
        ("páncreas", "Cáncer de páncreas"),
        ("pancreas", "Cáncer de páncreas"),
        ("tiroides", "Cáncer de tiroides"),
        ("riñón", "Cáncer de riñón"),
        ("renal", "Cáncer renal"),
        ("vejiga", "Cáncer de vejiga"),
        ("piel", "Cáncer de piel"),
        ("melanoma", "Melanoma maligno"),
        ("leucemia", "Leucemia"),
        ("linfoma", "Linfoma"),
        ("hodgkin", "Linfoma de Hodgkin"),
        ("mieloma", "Mieloma múltiple"),
        ("cerebro", "Cáncer cerebral"),
        ("encéfalo", "Cáncer cerebral"),
        ("hueso", "Cáncer óseo"),
        ("sarcoma", "Sarcoma"),
        ("carcinoma", "Carcinoma"),
    ]
    for keyword, cancer_name in keywords:
        if keyword in text_lower:
            return cancer_name
    return None


def identify_treatment_from_text(text: str) -> Optional[str]:
    text_lower = text.lower()
    found: list[str] = []
    for treatment_type, keywords in TREATMENT_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            found.append(treatment_type)
    return " + ".join(found) if found else None


def identify_result_from_text(text: str) -> Optional[str]:
    text_lower = text.lower()
    for label, keywords in RESULT_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return label
    return None
