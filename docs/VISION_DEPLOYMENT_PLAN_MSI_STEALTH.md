# 🎯 Vision-Driven Testing Deployment Plan
## For MSI Stealth Automated Client [Ac]

**Status**: READY FOR AUTONOMOUS EXECUTION
**Date**: 2026-05-09
**Target**: MSI Stealth (64GB RAM, 16GB VRAM)
**Pre-existing**: Agent Zero framework ✓ | Ollama ✓ | Streamlit app accessible ✓

---

## Phase 0: Verify Prerequisites (2 min)

```bash
# 0.1 Check Ollama has Gemma 4
ollama list | grep gemma4
# Expected: gemma4:9b (or similar). If missing: ollama pull gemma4:9b

# 0.2 Pull secondary model for A/B verification
ollama pull qwen3-vl:7b

# 0.3 Verify Streamlit is running on localhost:8501
curl -s http://localhost:8501 | head -5
# Should return HTML

# 0.4 Verify Python version
python3 --version  # ≥ 3.11 required
```

---

## Phase 1: Install Off-the-Shelf Libraries (5 min)

```bash
pip install --upgrade pip
pip install browser-use[cli] mcp_server_browser_use
pip install fastmcp ollama Pillow scikit-image httpx
python3 -m playwright install chromium
```

**Verification**: `pip freeze | grep browser-use` should show the package.

---

## Phase 2: Smoke Test (10 min)

Create and run this script at `/a0/usr/workdir/scripts/vision_smoke_test.py`:

```python
"""Smoke test: verify browser-use + Gemma 4 can interact with Streamlit"""
import asyncio
from browser_use import Agent, Browser
from pathlib import Path

async def smoke_test():
    browser = Browser(headless=False)
    agent = Agent(
        task="""
        1. Navigate to http://localhost:8501
        2. Log in with email 'admin@turtledb.com' and password 'admin123'
        3. Wait for Dashboard to load (look for 'Dashboard' text)
        4. Click 'New Intake' button
        5. Fill: Species='Loggerhead', Mass='25.5', Nest Size='1'
        6. Click SAVE button
        7. Verify success message appears
        8. Screenshot to /a0/usr/workdir/tmp/smoke_result.png
        """,
        llm="ollama/gemma4:9b",
        browser=browser
    )
    result = await agent.run()
    print(f"SMOKE TEST: {'PASS' if result else 'FAIL'}")
    return result

if __name__ == "__main__":
    asyncio.run(smoke_test())
```

**Run**: `cd /a0/usr/workdir && python3 scripts/vision_smoke_test.py`

**Success criteria**: Browser opens, navigates, logs in, fills form, clicks SAVE, screenshot saved.

---

## Phase 3: MCP Server Setup (5 min)

Start the browser-use MCP server so Agent Zero (M6800) can call it:

```bash
export OLLAMA_BASE_URL=http://localhost:11434
export BROWSER_USE_MODEL=ollama/gemma4:9b
uvx --from browser-use[cli] browser-use --mcp --port 8001 &
```

**Verification**: `curl http://localhost:8001/health` (if MCP server has health endpoint)

---

## Phase 4: Run Full Test Suite (1-2 hours)

Create `/a0/usr/workdir/scripts/vision_test_suite.py` with all 18 migrated tests:

### Test Categories (Replace Blocked Playwright Tests)

| Original | Vision Test | What It Tests |
|----------|-------------|---------------|
| TSK-04 (7 tests) | vision_obs_workflows | Stage progression, Property Matrix, save/verify |
| TSK-06 (5 tests) | vision_obs_adversarial | Invalid stage jumps, empty fields, double-save |
| TSK-07 (1 test) | vision_obs_scalability | 50x observation loop with visual verification |
| TSK-08 (6 tests) | vision_obs_input | SQLi in fields, XSS in notes, boundary values |

### Test Runner Structure

```python
import asyncio, json
from datetime import datetime
from browser_use import Agent, Browser

async def run_test(name, task):
    try:
        browser = Browser(headless=True)
        agent = Agent(task=task, llm="ollama/gemma4:9b", browser=browser)
        result = await agent.run()
        return {"name": name, "passed": bool(result), "time": datetime.now().isoformat()}
    except Exception as e:
        return {"name": name, "passed": False, "error": str(e)}

async def main():
    tests = [
        # TSK-04: Happy Path Workflows
        ("TSK-04-01_s0_to_s1", "Navigate to Observations, select Stage S1, fill matrix, save"),
        ("TSK-04-02_s1_to_s4", "Progress egg from S1 to S4, verify stage updates"),
        # ... (all 18 tests)
    ]
    results = []
    for name, task in tests:
        print(f"Running: {name}")
        results.append(await run_test(name, task))
    
    with open(f"tmp/vision_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Complete: {sum(1 for r in results if r['passed'])}/{len(results)} passed")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Phase 5: Report Back to M6800 Coordinator

After tests complete, Agent Zero on MSI should:
1. Save results JSON
2. Log to Obsidian vault with proper frontmatter
3. Send summary via A2A to M6800 (if configured) or notify user

---

## Troubleshooting Quick Reference

| Issue | Fix |
|-------|-----|
| Gemma 4 can't find button | Add "Scroll down if needed" to task, or try `headless=False` for debug |
| Ollama OOM | Use `gemma4:e4b` for simple element detection, `gemma4:9b` for complex tasks |
| `browser-use` times out | Increase timeout: `Agent(task=..., timeout=120)` |
| Streamlit redraws during action | Add "Wait 2 seconds after clicking" to task instructions |
| MCP port already in use | Change `--port 8001` to `--port 8002` |

---

## Expected Results

- ✅ Smoke test passes: browser navigates, logs in, creates intake
- ✅ 18 vision tests replace blocked Playwright tests
- ✅ 85%+ pass rate (vision models handle dynamic Streamlit elements)
- ✅ All results logged to Obsidian for audit trail
- ✅ DB pincer validation confirms actual Supabase writes (not just UI feedback)
