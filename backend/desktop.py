"""
Punto de entrada para DoctorCure como aplicación de escritorio.
"""

import os
import socket
import subprocess
import sys
import threading
import time
import traceback

_BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

# Log de errores junto al exe
LOG_FILE = os.path.join(os.path.expanduser("~"), "doctorcure_error.log")


def _log(msg: str) -> None:
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_server(port: int, timeout: float = 20.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def _start_server(port: int) -> None:
    try:
        _log(f"Iniciando servidor en puerto {port}")
        _log(f"sys.path = {sys.path[:3]}")
        _log(f"cwd = {os.getcwd()}")

        # En modo windowed stdout/stderr son None — evitar que uvicorn falle
        import io
        if sys.stdout is None:
            sys.stdout = io.StringIO()
        if sys.stderr is None:
            sys.stderr = io.StringIO()

        import uvicorn
        _log("uvicorn importado OK")

        from main import app
        _log("main.app importado OK")

        # log_config=None evita el formatter de colores que falla sin terminal
        uvicorn.run(app, host="127.0.0.1", port=port,
                    log_level="warning", reload=False, log_config=None)
    except Exception:
        _log("ERROR en servidor:")
        _log(traceback.format_exc())


def _find_browser() -> str | None:
    for path in _BROWSERS:
        if os.path.exists(path):
            return path
    return None


def main() -> None:
    # Limpiar log anterior
    try:
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
    except Exception:
        pass

    if hasattr(sys, "_MEIPASS"):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    _log(f"base_dir = {base_dir}")
    _log(f"_MEIPASS = {getattr(sys, '_MEIPASS', 'NO')}")

    os.chdir(base_dir)
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    port = _find_free_port()
    _log(f"Puerto elegido: {port}")

    thread = threading.Thread(target=_start_server, args=(port,), daemon=True)
    thread.start()

    if not _wait_for_server(port):
        _log("Timeout esperando al servidor")
        import tkinter, tkinter.messagebox
        tkinter.Tk().withdraw()
        tkinter.messagebox.showerror(
            "DoctorCure — Error",
            f"El servidor no pudo iniciar.\n\n"
            f"Revise el archivo de log:\n{LOG_FILE}"
        )
        sys.exit(1)

    _log("Servidor listo — abriendo ventana")
    url = f"http://127.0.0.1:{port}"
    browser = _find_browser()

    if browser:
        user_data = os.path.join(os.path.expanduser("~"), ".doctorcure_profile")
        proc = subprocess.Popen([
            browser,
            f"--app={url}",
            f"--user-data-dir={user_data}",
            "--no-first-run",
            "--disable-extensions",
            "--window-size=1280,820",
        ])
        proc.wait()
    else:
        import webbrowser
        webbrowser.open(url)
        thread.join()


if __name__ == "__main__":
    main()
