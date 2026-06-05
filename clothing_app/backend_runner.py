"""앱 실행 시 FastAPI 백엔드를 자동으로 켜는 보조 모듈."""

import atexit
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000
_backend_process = None
_backend_server = None


def _is_port_open(host=BACKEND_HOST, port=BACKEND_PORT):
    try:
        with socket.create_connection((host, port), timeout=0.3):
            return True
    except OSError:
        return False


def _backend_health_ok():
    try:
        with urllib.request.urlopen(f"http://{BACKEND_HOST}:{BACKEND_PORT}/", timeout=0.5) as response:
            return response.status == 200
    except Exception:
        return False


def _start_backend_in_thread():
    """PyInstaller exe 환경에서도 백엔드를 같은 프로세스 안에서 실행합니다."""
    global _backend_server
    try:
        import uvicorn
        from backend.app import app

        config = uvicorn.Config(
            app,
            host=BACKEND_HOST,
            port=BACKEND_PORT,
            log_level="warning",
            access_log=False,
        )
        _backend_server = uvicorn.Server(config)
        thread = threading.Thread(target=_backend_server.run, daemon=True)
        thread.start()
        return True
    except Exception as exc:
        print("백엔드 스레드 실행 실패:", exc)
        return False


def _start_backend_subprocess():
    global _backend_process
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cmd = [sys.executable, "-m", "uvicorn", "backend.app:app", "--host", BACKEND_HOST, "--port", str(BACKEND_PORT), "--log-level", "warning"]

    creationflags = 0
    startupinfo = None
    if os.name == "nt":
        creationflags = subprocess.CREATE_NO_WINDOW
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    _backend_process = subprocess.Popen(
        cmd,
        cwd=base_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
        startupinfo=startupinfo,
    )
    return True


def start_backend_if_needed():
    """이미 서버가 켜져 있으면 그대로 쓰고, 꺼져 있으면 자동 실행합니다."""
    if _is_port_open() and _backend_health_ok():
        return True

    try:
        if getattr(sys, "frozen", False):
            ok = _start_backend_in_thread()
        else:
            ok = _start_backend_subprocess()
    except Exception as exc:
        print("백엔드 자동 실행 실패:", exc)
        ok = _start_backend_in_thread()

    if not ok:
        return False

    for _ in range(50):
        if _backend_health_ok():
            return True
        time.sleep(0.15)

    return _is_port_open()


def stop_backend():
    global _backend_process, _backend_server
    if _backend_server is not None:
        try:
            _backend_server.should_exit = True
        except Exception:
            pass
    if _backend_process is not None:
        try:
            _backend_process.terminate()
        except Exception:
            pass
        _backend_process = None


atexit.register(stop_backend)
