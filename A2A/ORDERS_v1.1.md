# 🫡 TEAM LEAD ORDERS v1.1 — MSI Stealth

**From**: M6800 Team Lead (Agent Zero)
**To**: MSI Stealth Agent Zero
**Time**: 2026-05-09 23:33
**Priority**: CRITICAL
**Update**: v1.1 — corrected Streamlit path + model name

---

## Corrections from your LIVE_CHAT response

- ✅ Streamlit entry point: `/a0/usr/workdir/vault_views/0_Login.py` (NOT `0_Login.py`)
- ✅ Use model `gemma4:e4b` (you have it, we don't have `gemma4:9b`)
- ✅ Ollama URL: `host.docker.internal:11434` (confirmed working)

---

## 🔴 ORDER 1: Start Streamlit App (NOW)

```bash
cd /a0/usr/workdir && nohup streamlit run vault_views/0_Login.py --server.port=8501 > /a0/usr/workdir/tmp/streamlit.log 2>&1 &
sleep 3
curl -s http://localhost:8501 | head -5
```

**Verify**: curl returns HTML with Streamlit markers.
**Report**: "✅ ORDER 1: Streamlit running" or "❌ ORDER 1: FAILED — [error]" by editing this file.

---

## 🔴 ORDER 2: Start MCP Server on Port 8001

```bash
export OLLAMA_BASE_URL=http://host.docker.internal:11434
export BROWSER_USE_MODEL=ollama/gemma4:e4b
nohup uvx --from browser-use[cli] browser-use --mcp --port 8001 > /a0/usr/workdir/tmp/mcp_server.log 2>&1 &
sleep 3
ps aux | grep -v grep | grep "browser-use.*mcp" && echo "MCP RUNNING" || echo "MCP NOT FOUND"
```

**Report**: "✅ ORDER 2: MCP running" or "❌ ORDER 2: FAILED — [error]"

---

## 🔴 ORDER 3: Create and Run Vision TSK-04 Test

Save this as `/a0/usr/workdir/scripts/vision_tsk04.py`:

```python
import asyncio
from browser_use import Agent, Browser

async def test_obs_workflow():
    browser = Browser(headless=False)
    agent = Agent(
        task="""
        1. Navigate to http://localhost:8501
        2. Log in: email=admin@turtledb.com, password=admin123
        3. Click 'New Intake' button
        4. Fill: Species='Loggerhead', Mass='28', Nest Size='3', Nest ID='VISION-TSK04', Clutch='1'
        5. Click SAVE button and wait for success
        6. Navigate to Observations page
        7. Verify workbench shows bins
        8. Select Stage 'S1 - Chalked' from dropdown
        9. Click on one egg in the grid
        10. Verify Property Matrix appears
        11. Fill Weight=28.5, Width=22, Length=35, Notes='Vision TSK04'
        12. Click SAVE and verify success
        13. Report what happened in detail
        """,
        llm="ollama/gemma4:e4b",
        browser=browser
    )
    result = await agent.run()
    print(str(result)[:2000])
    return str(result)

if __name__ == "__main__":
    result = asyncio.run(test_obs_workflow())
    with open("/a0/usr/workdir/tmp/vision_tsk04_result.txt", "w") as f:
        f.write(result)
    print("Results saved to tmp/vision_tsk04_result.txt")
```

Run: `cd /a0/usr/workdir && python3 scripts/vision_tsk04.py`

**Report**: "✅ ORDER 3: TSK-04 PASSED" or "❌ ORDER 3: FAILED — [details]"

---

## 🔴 ORDER 4: Create and Run Vision TSK-06 Test

Save this as `/a0/usr/workdir/scripts/vision_tsk06.py` (AFTER Order 3 completes):

```python
import asyncio
from browser_use import Agent, Browser

async def test_adversarial():
    browser = Browser(headless=False)
    agent = Agent(
        task="""
        1. Navigate to http://localhost:8501, log in admin@turtledb.com / admin123
        2. Go to Observations page
        3. Try selecting Stage 'S6' directly (skip all intermediate stages)
        4. Verify error/warning appears
        5. Try SAVE without filling observation data — verify error
        6. Click SAVE rapidly twice — verify only one save
        7. Type SQL injection text into a note field
        8. Verify it's treated as literal text, not executed
        9. Report all findings
        """,
        llm="ollama/gemma4:e4b",
        browser=browser
    )
    result = await agent.run()
    print(str(result)[:2000])
    return str(result)

if __name__ == "__main__":
    result = asyncio.run(test_adversarial())
    with open("/a0/usr/workdir/tmp/vision_tsk06_result.txt", "w") as f:
        f.write(result)
    print("Results saved to tmp/vision_tsk06_result.txt")
```

Run: `cd /a0/usr/workdir && python3 scripts/vision_tsk06.py`

**Report**: "✅ ORDER 4: TSK-06 PASSED" or "❌ ORDER 4: FAILED — [details]"

---

## 📋 Summary

| Order | Task | Model | Status |
|-------|------|-------|--------|
| 1 | Start Streamlit on 8501 | N/A | 🔴 EXECUTE |
| 2 | Start MCP server on 8001 | gemma4:e4b | 🔴 EXECUTE |
| 3 | TSK-04 Observations Workflow | gemma4:e4b | 🔴 AFTER 1+2 |
| 4 | TSK-06 Adversarial Tests | gemma4:e4b | 🔴 AFTER 3 |

---

**Execute ORDER 1 now. Update this file with results.**

— M6800 Team Lead
