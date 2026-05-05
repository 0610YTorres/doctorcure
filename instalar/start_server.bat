@echo off
:: Agrega Tesseract al PATH si no esta (por si el instalador no lo hizo)
set "TESS_PATHS=C:\Program Files\Tesseract-OCR;C:\Program Files (x86)\Tesseract-OCR;C:\Tesseract-OCR"
for %%P in (%TESS_PATHS%) do (
    if exist "%%P\tesseract.exe" set "PATH=%PATH%;%%P"
)

cd /d C:\DoctorCure\backend
call venv\Scripts\activate
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1
