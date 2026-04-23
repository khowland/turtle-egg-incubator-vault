import argparse
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

ROOT = Path('/a0/usr/workdir')
SMOKE_TESTS = [
    'tests/e2e_playwright/test_adversarial_forensic.py::test_layer1_adversarial_ui_rejections[chromium]',
    'tests/e2e_playwright/test_real_user_workflows.py::test_login_and_dashboard_render[chromium]',
    'tests/e2e_playwright/test_real_user_workflows.py::test_intake_workflow_ui_elements[chromium]',
]


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def wait_ready(base_url: str, proc: subprocess.Popen, timeout: int, log_file: Path) -> None:
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        if proc.poll() is not None:
            tail = ''
            if log_file.exists():
                tail = '\n'.join(log_file.read_text(errors='ignore').splitlines()[-40:])
            raise RuntimeError(f'Streamlit exited before readiness. Log tail:\n{tail}')
        try:
            with urlopen(base_url, timeout=2) as r:
                body = r.read().decode('utf-8', errors='ignore')
                if r.status == 200 and 'Streamlit' in body:
                    return
        except Exception as e:
            last_error = e
        time.sleep(1)
    tail = ''
    if log_file.exists():
        tail = '\n'.join(log_file.read_text(errors='ignore').splitlines()[-40:])
    raise RuntimeError(f'Timeout waiting for readiness at {base_url}. Last error: {last_error}\nLog tail:\n{tail}')


def terminate_pg(proc: subprocess.Popen) -> None:
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except Exception:
        return
    deadline = time.time() + 8
    while time.time() < deadline:
        if proc.poll() is not None:
            return
        time.sleep(0.5)
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except Exception:
        pass


def build_pytest_args(mode: str, test: str | None) -> list[str]:
    if test:
        return [test, '-v']
    if mode == 'smoke':
        return SMOKE_TESTS + ['-v']
    return ['tests/e2e_playwright/', '-v']


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--suite', choices=['smoke', 'full'], default='smoke')
    ap.add_argument('--test', default=None)
    ap.add_argument('--startup-timeout', type=int, default=60)
    ap.add_argument('--test-timeout', type=int, default=240)
    ap.add_argument('--log-file', default=None)
    args = ap.parse_args()

    port = get_free_port()
    base_url = f'http://127.0.0.1:{port}'
    log_file = Path(args.log_file or (ROOT / ('smoke_streamlit.log' if args.suite == 'smoke' else 'streamlit_e2e.log')))
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, 'w') as lf:
        proc = subprocess.Popen(
            ['streamlit', 'run', 'app.py', '--server.address', '127.0.0.1', '--server.port', str(port), '--server.headless', 'true'],
            cwd=ROOT,
            stdout=lf,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            env={**os.environ},
        )

    try:
        wait_ready(base_url, proc, args.startup_timeout, log_file)
        env = {**os.environ, 'E2E_BASE_URL': base_url}
        pytest_args = ['python3', '-m', 'pytest'] + build_pytest_args(args.suite, args.test)
        return subprocess.run(pytest_args, cwd=ROOT, env=env, timeout=args.test_timeout).returncode
    finally:
        terminate_pg(proc)


if __name__ == '__main__':
    raise SystemExit(main())
