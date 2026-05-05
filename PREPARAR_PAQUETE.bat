@echo off
title DoctorCure - Preparar paquete de distribucion

echo.
echo ============================================
echo  Generando build de produccion del frontend
echo ============================================
echo.

:: Ir a la carpeta del frontend (relativa a este .bat)
cd /d "%~dp0frontend"

echo [1/3] Instalando dependencias npm...
call npm install
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] npm install fallo. Verifique que Node.js este instalado.
    pause
    exit /b 1
)

echo.
echo [2/3] Construyendo frontend con next build...
call npm run build
if %errorLevel% neq 0 (
    echo.
    echo [ERROR] next build fallo. Revise los mensajes anteriores.
    pause
    exit /b 1
)

echo.
echo [3/3] Build listo en: frontend\out\
echo.

:: Crear carpeta de distribucion limpia
set "DIST=%~dp0_DISTRIBUCION\DoctorCure"

echo Limpiando carpeta de distribucion anterior...
if exist "%DIST%" rmdir /s /q "%DIST%"
mkdir "%DIST%"
mkdir "%DIST%\backend"
mkdir "%DIST%\frontend"
mkdir "%DIST%\instalar"

echo Copiando backend...
robocopy "%~dp0backend" "%DIST%\backend" /E /XD venv __pycache__ .pytest_cache /XF *.pyc /NFL /NDL /NJH /NJS

echo Copiando frontend build...
robocopy "%~dp0frontend\out" "%DIST%\frontend\out" /E /NFL /NDL /NJH /NJS

echo Copiando scripts de instalacion...
robocopy "%~dp0instalar" "%DIST%\instalar" /E /NFL /NDL /NJH /NJS

echo.
echo ============================================
echo  PAQUETE LISTO en:
echo  %DIST%
echo ============================================
echo.
echo Pasos para instalar en el PC del medico:
echo.
echo  1. Copie la carpeta DoctorCure a C:\
echo     (debe quedar como C:\DoctorCure)
echo.
echo  2. Instale Python 3.11+ desde python.org
echo     IMPORTANTE: marque "Add Python to PATH"
echo.
echo  3. (Opcional) Instale Tesseract OCR para
echo     PDFs escaneados.
echo.
echo  4. Clic derecho en:
echo     C:\DoctorCure\instalar\INSTALAR.bat
echo     -> Ejecutar como administrador
echo.
pause
