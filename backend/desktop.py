"""
Punto de entrada para DoctorCure como aplicación de escritorio.

Estrategia:
  1. Arranca FastAPI/uvicorn en un puerto libre (hilo demonio).
  2. Abre Edge o Chrome en modo --app (sin barra de navegador).
  3. Espera a que el usuario cierre la ventana y termina el proceso.
"""

import os
import socket
import subprocess
import sys
import threading
import time


# Rutas donde puede estar Edge o Chrome en Windows
_BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_server(port: int, timeout: float = 15.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def _start_server(port: int) -> None:
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=port,
        log_level="warning",
        reload=False,
    )


def _find_browser() -> str | None:
    for path in _BROWSERS:
        if os.path.exists(path):
            return path
    return None


def main() -> None:
    # Asegurar que los imports relativos funcionen
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if hasattr(sys, "_MEIPASS"):
        base_dir = sys._MEIPASS
    os.chdir(base_dir)
    sys.path.insert(0, base_dir)

    port = _find_free_port()

    # Arrancar servidor en hilo demonio
    thread = threading.Thread(target=_start_server, args=(port,), daemon=True)
    thread.start()

    if not _wait_for_server(port):
        print("ERROR: el servidor no respondió a tiempo.", file=sys.stderr)
        sys.exit(1)

    url = f"http://127.0.0.1:{port}"
    browser = _find_browser()

    if browser:
        # Carpeta de perfil aislada para que no mezcle con el navegador del usuario
        user_data = os.path.join(os.path.expanduser("~"), ".doctorcure_profile")
        proc = subprocess.Popen([
            browser,
            f"--app={url}",
            f"--user-data-dir={user_data}",
            "--no-first-run",
            "--disable-extensions",
            "--window-size=1280,820",
        ])
        proc.wait()  # Bloquea hasta que el usuario cierre la ventana
    else:
        # Fallback: abrir en el navegador por defecto
        import webbrowser
        webbrowser.open(url)
        thread.join()  # Mantener vivo el servidor


if __name__ == "__main__":
    main()
