# DoctorCure — Historia Clínica → Excel

Aplicación web local que extrae automáticamente los campos clínicos de una historia clínica en PDF y genera un Excel listo para el **Comité de Tumores**, respetando la plantilla institucional.

> **100 % local — sin IA externa — sin envío de datos a terceros.**

---

## Características

- 📄 **PDF nativo**: extracción directa de texto digital
- 🔍 **OCR local**: soporte para PDFs escaneados vía Tesseract
- 🤖 **Extracción automática**: regex en cascada con puntuación de confianza
- ✏️ **Editor de campos**: revisión y corrección manual antes de exportar
- 📊 **Excel con plantilla**: respeta formato, cabecera EMF y celdas fusionadas
- 🖥️ **Arranque automático**: se inicia con Windows, sin intervención del usuario

---

## Tecnologías

| Capa | Stack |
|---|---|
| Backend | Python 3.11+, FastAPI, uvicorn |
| Extracción PDF | pdfplumber, pypdf, pdf2image + Tesseract OCR |
| Excel | openpyxl + restauración de imagen EMF vía zipfile |
| Frontend | Next.js 14 (App Router), Tailwind CSS |
| Despliegue | FastAPI sirve el frontend estático (sin Node.js en producción) |

---

## Estructura del proyecto

```
DoctorCure/
├── backend/
│   ├── main.py                  # FastAPI + sirve el frontend
│   ├── requirements.txt
│   ├── models/schemas.py        # PatientData, ExtractionResult
│   ├── routers/
│   │   ├── upload.py            # POST /api/upload
│   │   └── export.py            # POST /api/export
│   ├── services/
│   │   ├── field_extractor.py   # Extracción de campos con regex
│   │   └── excel_service.py     # Generación del Excel
│   ├── utils/patterns.py        # Patrones regex + CIE-10 map
│   └── templates/               # plantilla_comite_tumores.xlsx (no incluida)
├── frontend/
│   ├── app/page.tsx             # UI principal
│   ├── components/              # DropZone, FieldEditor, ExportPanel...
│   └── lib/                     # api.ts, types.ts
├── instalar/
│   ├── INSTALAR.bat             # Instalador para Windows (ejecutar como admin)
│   ├── arrancar.vbs             # Inicio silencioso del servidor
│   └── start_server.bat         # Arranca FastAPI
└── PREPARAR_PAQUETE.bat         # Genera el paquete de distribución
```

---

## Instalación para desarrollo

### Requisitos

- Python 3.11+
- Node.js 18+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (opcional, para PDFs escaneados)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (desarrollo)

```bash
cd frontend
npm install
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000).

### Plantilla Excel

La plantilla institucional **no está incluida** en el repositorio.
Cópiala manualmente a `backend/templates/plantilla_comite_tumores.xlsx`.

---

## Instalación en PC del médico (producción)

1. Ejecuta `PREPARAR_PAQUETE.bat` en tu PC de desarrollo — genera `_DISTRIBUCION/DoctorCure/`
2. Copia esa carpeta a `C:\DoctorCure` en el PC destino
3. Clic derecho en `C:\DoctorCure\instalar\INSTALAR.bat` → **Ejecutar como administrador**
4. El instalador configura el arranque automático y crea el acceso directo en el Escritorio

El servidor corre en `http://localhost:8000` y arranca solo al iniciar sesión en Windows.

---

## Campos extraídos

| Sección | Campos |
|---|---|
| Identificación | Nombres, apellidos, CC, tipo documento, edad, sexo, fecha atención, médico tratante, especialidad, entidad, fecha diagnóstico |
| Diagnóstico | CIE-10, descripción, diagnóstico patológico, TNM (T/N/M), estadificación |
| Imágenes | Ecografía, TAC, RMN, PET/CT, mamografía, informes |
| Tratamientos | Cirugía, quimioterapia, radioterapia, hormonoterapia (recibió + detalles) |

---

## Licencia

MIT
