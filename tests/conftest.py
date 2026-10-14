"""
Pytest configuration and shared fixtures for the Job Application QA test suite.
Manages test server lifecycle, storage isolation, and temporary test assets.
"""

import os
import json
import time
import socket
import threading
import urllib.request
import pytest
from portal.app import app
from portal.storage import store

PORT = 5555
BASE_URL = f"http://127.0.0.1:{PORT}"


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def get_app_count(base_url: str = BASE_URL) -> int:
    """Fetch application count from the live server API or fallback to store."""
    try:
        with urllib.request.urlopen(f"{base_url}/api/applications", timeout=2) as response:
            if response.status == 200:
                payload = json.loads(response.read().decode())
                return int(payload.get("count", 0))
    except Exception:
        pass
    return store.get_count()


def get_stored_applications(base_url: str = BASE_URL) -> list:
    """Fetch list of stored applications from the live server API."""
    try:
        with urllib.request.urlopen(f"{base_url}/api/applications", timeout=2) as response:
            if response.status == 200:
                payload = json.loads(response.read().decode())
                return payload.get("applications", [])
    except Exception:
        pass
    return store.get_all()


@pytest.fixture(scope="session", autouse=True)
def run_test_server():
    """Ensure the local Flask portal is running for the entire test session."""
    if not is_port_in_use(PORT):
        server_thread = threading.Thread(
            target=lambda: app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False),
            daemon=True
        )
        server_thread.start()

        # Poll health endpoint until responsive
        ready = False
        for _ in range(30):
            try:
                with urllib.request.urlopen(f"{BASE_URL}/health", timeout=1) as response:
                    if response.status == 200:
                        ready = True
                        break
            except Exception:
                time.sleep(0.1)

        if not ready:
            raise RuntimeError(f"Could not connect to test server at {BASE_URL} within timeout.")

    yield


@pytest.fixture(autouse=True)
def reset_storage_state():
    """Reset application store before and after each test to guarantee complete test isolation."""
    store.clear()
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/reset", data=b"", method="POST")
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass
    yield
    store.clear()
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/reset", data=b"", method="POST")
        urllib.request.urlopen(req, timeout=1)
    except Exception:
        pass


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture
def test_files(tmp_path):
    """Generate temporary test files for valid and invalid file upload scenarios."""
    pdf_file = tmp_path / "valid_resume.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 Mock PDF resume content for testing purposes.")

    docx_file = tmp_path / "valid_resume.docx"
    docx_file.write_bytes(b"PK\x03\x04 Mock DOCX resume file content.")

    exe_file = tmp_path / "malicious_script.exe"
    exe_file.write_bytes(b"MZ\x90\x00 Executable binary payload mock.")

    png_file = tmp_path / "profile_photo.png"
    png_file.write_bytes(b"\x89PNG\r\n\x1a\n Image content.")

    return {
        "pdf": str(pdf_file),
        "docx": str(docx_file),
        "exe": str(exe_file),
        "png": str(png_file),
    }
