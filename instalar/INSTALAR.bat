@echo off
setlocal EnableDelayedExpansion
title DoctorCure - Instalador

echo.
echo ==============================================
echo    INSTALADOR DE DOCTORCURE
echo    Historia Clinica a Excel (local)
echo ==============================================
echo.

:: ── Verificar que se ejecuta como Administrador ───────────────────────────
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Ejecute este archivo como Administrador.
    echo Clic derecho sobre INSTALAR.bat y seleccione
    echo "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

:: ── Detectar usuario real (no "Administrator") para el escritorio ─────────
for /f "tokens=*" %%U in (
    'powershell -NoProfile -Command "(Get-WMIObject Win32_ComputerSystem).UserName -replace '^.*\\\\',''"'
) do set "REAL_USER=%%U"

if "!REAL_USER!"=="" (
    :: Fallback: leer de la carpeta Users
    for /f "tokens=*" %%U in (
        'powershell -NoProfile -Command "(Get-ChildItem C:\Users | Where-Object {$_.Name -notmatch ''Public|Default|Administrator|All Users''} | Select-Object -First 1).Name"'
    ) do set "REAL_USER=%%U"
)

set "REAL_DESKTOP=C:\Users\!REAL_USER!\Desktop"
if not exist "!REAL_DESKTOP!" set "REAL_DESKTOP=%PUBLIC%\Desktop"

echo Usuario detectado : !REAL_USER!
echo Escritorio        : !REAL_DESKTOP!
echo.

:: ── Paso 0: Copiar archivos a C:\DoctorCure si no existen ─────────────────
set "INSTALL_DIR=C:\DoctorCure"
set "SOURCE=%~dp0.."

echo [0/5] Preparando archivos en %INSTALL_DIR%...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

robocopy "%SOURCE%\backend"  "%INSTALL_DIR%\backend"        /E /XD venv __pycache__ /XF *.pyc /NFL /NDL /NJH /NJS
robocopy "%SOURCE%\frontend" "%INSTALL_DIR%\frontend"       /E /NFL /NDL /NJH /NJS
robocopy "%SOURCE%\instalar" "%INSTALL_DIR%\instalar"       /E /NFL /NDL /NJH /NJS

echo     Archivos listos.

:: ── Paso 1: Python ────────────────────────────────────────────────────────
echo.
echo [1/5] Verificando Python...

:: Intentar primero con "py" (Python Launcher, siempre disponible como admin)
set "PYTHON_CMD="
py --version >nul 2>&1
if %errorLevel% equ 0 (
    set "PYTHON_CMD=py"
    goto python_ok
)

:: Intentar con "python"
python --version >nul 2>&1
if %errorLevel% equ 0 (
    set "PYTHON_CMD=python"
    goto python_ok
)

:: Buscar en rutas tipicas de instalacion
for %%P in (
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "C:\Users\!REAL_USER!\AppData\Local\Programs\Python\Python313\python.exe"
    "C:\Users\!REAL_USER!\AppData\Local\Programs\Python\Python312\python.exe"
    "C:\Users\!REAL_USER!\AppData\Local\Programs\Python\Python311\python.exe"
    "C:\Users\!REAL_USER!\AppData\Local\Programs\Python\Python310\python.exe"
) do (
    if exist %%P (
        set "PYTHON_CMD=%%P"
        :: Agregar al PATH del sistema para que funcione siempre
        for %%D in (%%P) do (
            setx PATH "%PATH%;%%~dpD" /M >nul 2>&1
            set "PATH=%PATH%;%%~dpD"
        )
        goto python_ok
    )
)

echo.
echo [ERROR] Python no encontrado.
echo Descargue e instale Python desde:
echo   https://www.python.org/downloads/
echo.
echo IMPORTANTE al instalar Python:
echo   - Marque "Add Python to PATH"
echo   - Seleccione "Install for all users"
echo.
pause
exit /b 1

:python_ok
!PYTHON_CMD! --version
echo     OK - usando: !PYTHON_CMD!

:: ── Paso 2: Tesseract ─────────────────────────────────────────────────────
echo.
echo [2/5] Verificando Tesseract OCR...

tesseract --version >nul 2>&1
if %errorLevel% equ 0 (
    echo     OK - encontrado en PATH
    goto tesseract_ok
)

for %%P in (
    "C:\Program Files\Tesseract-OCR"
    "C:\Program Files (x86)\Tesseract-OCR"
    "C:\Tesseract-OCR"
) do (
    if exist "%%~P\tesseract.exe" (
        echo     Encontrado en %%~P
        setx PATH "%PATH%;%%~P" /M >nul 2>&1
        set "PATH=%PATH%;%%~P"
        echo     Agregado al PATH del sistema.
        goto tesseract_ok
    )
)

echo     AVISO: Tesseract no encontrado.
echo     Los PDFs escaneados no podran procesarse.
echo     (Los PDFs digitales funcionan sin Tesseract)
echo.
set /p CONT="Continuar sin Tesseract? (S/N): "
if /i "!CONT!" neq "S" (
    pause
    exit /b 0
)
goto tesseract_done

:tesseract_ok
:tesseract_done

:: ── Paso 3: Entorno virtual e instalacion de dependencias ─────────────────
echo.
echo [3/5] Instalando dependencias Python...
cd /d "%INSTALL_DIR%\backend"

if not exist venv (
    echo     Creando entorno virtual...
    !PYTHON_CMD! -m venv venv
    if %errorLevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
)

call venv\Scripts\activate
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt -q
if %errorLevel% neq 0 (
    echo [ERROR] Fallo la instalacion de dependencias.
    pause
    exit /b 1
)
echo     OK

:: ── Paso 4: Arranque automatico ───────────────────────────────────────────
echo.
echo [4/5] Configurando arranque automatico...

copy /Y "%INSTALL_DIR%\instalar\arrancar.vbs"    "%INSTALL_DIR%\arrancar.vbs"    >nul
copy /Y "%INSTALL_DIR%\instalar\start_server.bat" "%INSTALL_DIR%\start_server.bat" >nul

schtasks /delete /tn "DoctorCure" /f >nul 2>&1
schtasks /create /tn "DoctorCure" /tr "wscript.exe \"%INSTALL_DIR%\arrancar.vbs\"" /sc ONLOGON /rl HIGHEST /f >nul

if %errorLevel% equ 0 (
    echo     Tarea programada creada correctamente.
) else (
    echo     AVISO: No se pudo crear la tarea automatica.
)

:: ── Paso 5: Acceso directo en el Escritorio del usuario real ──────────────
echo.
echo [5/5] Creando acceso directo en el Escritorio...

set "SHORTCUT=!REAL_DESKTOP!\DoctorCure.lnk"
set "EDGE=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
set "CHROME=C:\Program Files\Google\Chrome\Application\chrome.exe"

if exist "!EDGE!" (
    powershell -NoProfile -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut('!SHORTCUT!'); $s.TargetPath='!EDGE!'; $s.Arguments='--app=http://localhost:8000'; $s.IconLocation='!EDGE!,0'; $s.Description='DoctorCure - Historia Clinica a Excel'; $s.Save()"
) else if exist "!CHROME!" (
    powershell -NoProfile -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut('!SHORTCUT!'); $s.TargetPath='!CHROME!'; $s.Arguments='--app=http://localhost:8000'; $s.IconLocation='!CHROME!,0'; $s.Description='DoctorCure - Historia Clinica a Excel'; $s.Save()"
) else (
    powershell -NoProfile -Command "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut('!SHORTCUT!'); $s.TargetPath='http://localhost:8000'; $s.Description='DoctorCure'; $s.Save()"
)

if exist "!SHORTCUT!" (
    echo     Acceso directo creado en: !REAL_DESKTOP!
) else (
    echo     AVISO: No se pudo crear en el escritorio.
    echo     Cree un acceso directo manualmente a:
    echo     http://localhost:8000
)

:: ── Resumen final ─────────────────────────────────────────────────────────
echo.
echo ==============================================
echo    INSTALACION COMPLETADA
echo ==============================================
echo.
echo  El servidor arrancara solo al iniciar sesion.
echo  Haga doble clic en "DoctorCure" del Escritorio.
echo.
echo  Para iniciar AHORA sin reiniciar el PC:
echo.

set /p INICIO="Desea iniciar DoctorCure ahora mismo? (S/N): "
if /i "!INICIO!"=="S" (
    start "" wscript.exe "%INSTALL_DIR%\arrancar.vbs"
    timeout /t 4 /nobreak >nul
    start "" "http://localhost:8000"
)

endlocal
pause
