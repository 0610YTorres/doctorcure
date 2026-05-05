"""
Punto de entrada para la versión de escritorio de DoctorCure.
Arranca uvicorn en un puerto libre y abre una ventana nativa con pywebview.
"""

import socket
import sys
import threading
import time
import logging

logger = logging.getLogger(__name__)


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _start_server(port: int) -> None:
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=port,
        log_level="warning",
        # Desactiva el reload — no aplica en producción
        reload=False,
    )


def _wait_for_server(port: int, timeout: float = 15.0) -> bool:
    """Espera hasta que el servidor responda."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def main() -> None:
    import webview

    port = _find_free_port()

    # Arrancar FastAPI en hilo demonio
    server_thread = threading.Thread(
        target=_start_server, args=(port,), daemon=True
    )
    server_thread.start()

    # Esperar a que el servidor esté listo
    if not _wait_for_server(port):
        print("ERROR: el servidor no arrancó a tiempo.", file=sys.stderr)
        sys.exit(1)

    # Crear y mostrar la ventana
    webview.create_window(
        title="DoctorCure — Historia Clínica a Excel",
        url=f"http://127.0.0.1:{port}",
        width=1280,
        height=820,
        min_size=(900, 650),
        resizable=True,
        text_select=True,
    )
    webview.start(debug=False)


if __name__ == "__main__":
    # Cambiar al directorio del script para que los imports relativos funcionen
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
