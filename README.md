# DoctorCure — Historia Clínica PDF → Excel

Extracción automática de datos clínicos a partir de PDFs de historias clínicas.
Procesamiento 100% local (regex + OCR). Sin IA de pago, sin APIs externas.

---

## Arquitectura

```
DoctorCure/
├── backend/                  FastAPI (Python)
│   ├── main.py               Punto de entrada
│   ├── requirements.txt
│   ├── models/schemas.py     Pydantic models
│   ├── routers/
│   │   ├── upload.py         POST /api/upload
│   │   └── export.py         POST /api/export
│   ├── services/
│   │   ├── pdf_extractor.py  pdfplumber → PyMuPDF → OCR
│   │   ├── ocr_service.py    Tesseract wrapper
│   │   ├── field_extractor.py Regex + reglas CIE-10
│   │   └── excel_service.py  openpyxl template
│   └── utils/patterns.py     Patrones regex + mapas CIE-10
└── frontend/                 Next.js 14 + Tailwind
    ├── app/page.tsx           Página principal (toda la UI)
    ├── components/
    │   ├── DropZone.tsx       Drag & drop
    │   ├── FieldEditor.tsx    Formulario editable + confianza
    │   ├── ProcessingStatus   Animación de progreso
    │   └── ExportPanel.tsx    Botón descarga Excel
    └── lib/
        ├── api.ts             Cliente HTTP
        └── types.ts           Tipos + definición de campos
```

---

## Pre-requisitos

| Herramienta | Versión mínima | Notas |
|---|---|---|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| Tesseract | 5.x | Solo para PDFs escaneados |

### Instalar Tesseract en Windows

1. Descargar installer desde https://github.com/UB-Mannheim/tesseract/wiki
2. Instalar en `C:\Program Files\Tesseract-OCR\`
3. Agregar a PATH del sistema
4. Instalar idioma español: en el installer marcar `spa`
5. Verificar: `tesseract --version`

---

## Ejecución

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API disponible en http://localhost:8000
Docs interactivas en http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

App disponible en http://localhost:3000

---

## Flujo de uso

1. Abrir http://localhost:3000
2. Arrastrar o seleccionar un PDF de historia clínica
3. Clic en **Analizar Historia Clínica**
4. Revisar y editar los campos extraídos
5. Clic en **Exportar Excel** → descarga automática

---

## Campos extraídos

| Campo | Método |
|---|---|
| Nombre del paciente | Regex (nombre/paciente:) |
| Tipo y número de documento | Regex (CC/TI/CE + número) |
| Edad | Regex (edad: NN años) |
| Sexo | Regex (sexo/género:) |
| Código CIE-10 | Regex (CIE-10: X00.0) |
| Descripción diagnóstico | Regex contextual |
| Tipo de cáncer | CIE-10 map + keywords |
| Estadificación | Regex (Estadio I/II/III/IV, TNM) |
| Fecha diagnóstico | Regex (fecha diagnóstico:) |
| Tratamiento inicial | Regex + keywords (quimio/radio/cirugía) |
| Resultado tratamiento | Keywords (remisión/progresión) |
| Médico tratante | Regex (Dr./médico tratante:) |

### Motor de extracción

- Cada campo tiene 3-5 patrones regex en cascada
- Confianza decae 15% por patrón de respaldo usado
- Tipo de cáncer: inferencia desde código CIE-10 → keywords → texto
- Tratamiento y resultado: extracción por campo → inferencia de texto completo

---

## Variables de entorno (opcional)

Crear `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Troubleshooting

| Problema | Solución |
|---|---|
| `ModuleNotFoundError: pdfplumber` | Activar venv y `pip install -r requirements.txt` |
| `tesseract not found` | Instalar Tesseract y agregar al PATH |
| PDF escaneado sin texto | El sistema usa OCR automáticamente si Tesseract está instalado |
| CORS error en frontend | Verificar que backend corra en puerto 8000 |
| Campo vacío tras extracción | Editar manualmente en la UI antes de exportar |
