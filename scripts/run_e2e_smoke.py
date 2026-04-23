import os, signal, socket, subprocess, sys, time
from pathlib import Path

PORT = 8501
ROOT = Path('/a0/usr/workdir')
STREAMLIT_LOG = ROOT / 'smoke_streamlit.log'
RESULTS_LOG = ROOT / 'smoke_results.log'

TESTS = [
    'tests/e2e_playwright/test_adversarial_forensic.py::test_layer1_adversarial_ui_rejections[chromium]',
    'tests/e2e_playwright/test_real_user_workflows.py::test_login_and_dashboard_render[chromium]',
    'tests/e2e_playwright/test_real_user_workflows.py::test_intake_workflow_ui_elements[chromium]',
]

def run(cmd, check=False, **kwargs):
    return subprocess.run(cmd, shell=isinstance(cmd, str), check=check, **kwargs)

def cleanup_port():
    run("pkill -f 'streamlit run app.py' || true")
    run("pkill -f 'python3 -m pytest tests/e2e_playwright' || true")
    run("pkill -f 'chrome-headless-shell' || true")
    run("pkill -f 'playwright/driver/package/cli.js run-driver' || true")
    run(f"fuser -k {PORT}/tcp 2>/dev/null || true")
    time.sleep(2)

def wait_http(port, timeout=60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except OSError:
            time.sleep(1)
    return False

def main():
    cleanup_port()
    with open(STREAMLIT_LOG, 'w') as lf:
        proc = subprocess.Popen(
            ['streamlit', 'run', 'app.py', '--server.port', str(PORT)],
            cwd=ROOT,
            stdout=lf,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    try:
        if not wait_http(PORT, 60):
            RESULTS_LOG.write_text('SMOKE_FAIL: Streamlit never became reachable\n')
            return 1
        with open(RESULTS_LOG, 'w') as out:
            for test in TESTS:
                out.write(f'=== {test} ===\n')
                out.flush()
                res = subprocess.run(
                    ['python3', '-m', 'pytest', test, '-v'],
                    cwd=ROOT,
                    stdout=out,
                    stderr=subprocess.STDOUT,
                    timeout=120,
                )
                out.write(f'STATUS={res.returncode}\n\n')
                out.flush()
        return 0
    finally:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except Exception:
            pass
        cleanup_port()

if __name__ == '__main__':
    raise SystemExit(main())
