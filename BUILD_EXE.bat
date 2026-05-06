@echo off
title DoctorCure - Construir EXE

echo.
echo ============================================
echo  Construyendo DoctorCure.exe
echo ============================================
echo.

if not exist "%~dp0backend\desktop.py" (
    echo [ERROR] Ejecute este archivo desde la carpeta raiz de DoctorCure.
    pause
    exit /b 1
)

:: 1. Construir frontend
echo [1/3] Construyendo frontend...
cd /d "%~dp0frontend"
call npm run build
if %errorLevel% neq 0 (
    echo [ERROR] next build fallo.
    pause
    exit /b 1
)
echo     OK

:: 2. Dependencias Python
echo.
echo [2/3] Verificando dependencias Python...
cd /d "%~dp0backend"
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt -q
echo     OK

:: 3. Empaquetar con PyInstaller
echo.
echo [3/3] Empaquetando con PyInstaller...

set "FRONTEND_OUT=..\frontend\out"
set "TEMPLATES=templates"

pyinstaller ^
    --name "DoctorCure" ^
    --onedir ^
    --windowed ^
    --add-data "%FRONTEND_OUT%;frontend/out" ^
    --add-data "%TEMPLATES%;templates" ^
    --hidden-import "uvicorn.logging" ^
    --hidden-import "uvicorn.loops" ^
    --hidden-import "uvicorn.loops.auto" ^
    --hidden-import "uvicorn.protocols" ^
    --hidden-import "uvicorn.protocols.http" ^
    --hidden-import "uvicorn.protocols.http.auto" ^
    --hidden-import "uvicorn.lifespan" ^
    --hidden-import "uvicorn.lifespan.on" ^
    --hidden-import "pdfplumber" ^
    --hidden-import "pytesseract" ^
    --hidden-import "openpyxl" ^
    --collect-all "pdfplumber" ^
    --noconfirm ^
    desktop.py

if %errorLevel% neq 0 (
    echo.
    echo [ERROR] PyInstaller fallo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  EXE listo en: backend\dist\DoctorCure\
echo ============================================
echo.
echo Lleva toda la carpeta DoctorCure\ al PC del
echo medico. Solo necesita instalar Tesseract OCR.
echo.
pause
