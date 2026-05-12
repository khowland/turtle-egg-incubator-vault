import subprocess
import json
import time
import os
import re

test_configs = [
    ("TSK-03", "tests/e2e_playwright/test_intake_extended.py"),
    ("TSK-04", "tests/e2e_playwright/test_observation_workflows.py"),
    ("TSK-06", "tests/e2e_playwright/test_adversarial_observations.py"),
    ("TSK-07", "tests/e2e_playwright/test_phase5_scalability_loop.py"),
    ("TSK-08", "tests/e2e_playwright/test_adversarial_input.py"),
]
results = []
workdir = "/a0/usr/workdir"
output_path = os.path.join(workdir, "tmp", "BATCH_6_RESULTS_RAW.json")

def parse_pytest_output(stdout, stderr):
    """Extract per-test results from pytest verbose short-traceback output."""
    tests = []
    # pattern for PASSED/FAILED/ERROR at start of line
    lines = stdout.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        match = re.match(r'^(PASSED|FAILED|ERROR)\s+(.+)', line)
        if match:
            status = match.group(1)
            test_name = match.group(2).strip()
            error_message = ""
            error_line = ""
            # for failures, collect subsequent traceback lines until next PASSED/FAILED or blank line pattern
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if re.match(r'^(PASSED|FAILED|ERROR)\s', next_line) or next_line.startswith('='):
                    break
                if next_line.startswith('E '):
                    error_message += next_line[2:] + "\n"
                if 'AssertionError' in next_line or 'TimeoutError' in next_line or 'Error' in next_line:
                    error_message += next_line + "\n"
                if next_line.startswith('tests/') or next_line.startswith('../../'):
                    # traceback line with file:line
                    if error_line == "":
                        error_line = next_line
                j += 1
            i = j
            tests.append({
                "test_name": test_name,
                "status": status,
                "error_message": error_message.strip()[:500],
                "error_line": error_line.strip()[:200]
            })
        else:
            i += 1
    # also look for "no tests ran" or collection errors
    if "no tests ran" in stdout.lower():
        tests.append({
            "test_name": "collection",
            "status": "ERROR",
            "error_message": "No tests ran (collection error)",
            "error_line": ""
        })
    if stderr and "Error" in stderr:
        tests.append({
            "test_name": "collection_setup",
            "status": "ERROR",
            "error_message": stderr.strip()[:500],
            "error_line": ""
        })
    return tests

for tsk, test_rel_path in test_configs:
    print(f"Starting {tsk} ...", flush=True)
    start = time.time()
    try:
        proc = subprocess.run(
            ["python", "-m", "pytest", test_rel_path, "-v", "--tb=short", "--timeout=300"],
            capture_output=True, text=True,
            timeout=350,  # extra buffer
            cwd=workdir
        )
        duration = round(time.time() - start, 3)
        parsed = parse_pytest_output(proc.stdout, proc.stderr)
        if not parsed:
            # fallback: check for summary line
            if "= " in proc.stdout:
                # try to get a single result from the summary
                summary_line = [l for l in proc.stdout.splitlines() if "= " in l and ("passed" in l or "failed" in l)]
                if summary_line:
                    # extract numbers? not per test
                    parsed.append({
                        "test_name": "summary",
                        "status": proc.returncode == 0 and "PASSED" or "FAILED",
                        "error_message": proc.stdout.strip()[-500:],
                        "error_line": ""
                    })
        for p in parsed:
            p["tsk"] = tsk
            p["duration_seconds"] = duration
            results.append(p)
        print(f"{tsk} completed in {duration}s with {len(parsed)} entries", flush=True)
    except subprocess.TimeoutExpired:
        duration = round(time.time() - start, 3)
        results.append({
            "tsk": tsk,
            "test_name": "timeout",
            "status": "TIMEOUT",
            "duration_seconds": duration,
            "error_message": "Test suite timed out after 350 seconds",
            "error_line": ""
        })
        print(f"{tsk} TIMEOUT after {duration}s", flush=True)
    except Exception as e:
        duration = round(time.time() - start, 3)
        results.append({
            "tsk": tsk,
            "test_name": "error",
            "status": "ERROR",
            "duration_seconds": duration,
            "error_message": str(e)[:500],
            "error_line": ""
        })
        print(f"{tsk} ERROR: {e}", flush=True)

# Build final JSON with summary and root cause/remediation placeholders
summary = {"total": len(results), "passed": 0, "failed": 0, "timeout": 0, "error": 0}
for r in results:
    s = r["status"]
    if s == "PASSED": summary["passed"] += 1
    elif s == "FAILED": summary["failed"] += 1
    elif s == "TIMEOUT": summary["timeout"] += 1
    elif s == "ERROR": summary["error"] += 1

final = {
    "batch_id": "BATCH_6",
    "results": results,
    "summary": summary,
    "notes": ""
}

with open(output_path, "w") as f:
    json.dump(final, f, indent=2)
print(f"JSON written to {output_path}", flush=True)
print("BATCH_6_RUNNER_COMPLETE", flush=True)
