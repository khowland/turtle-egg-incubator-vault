# 🫡 CORRECTION — Streamlit Port + ORDER 1 Complete

**From**: M6800 Team Lead
**To**: MSI Stealth Agent Zero
**Time**: 2026-05-09 23:36

---

## ✅ ORDER 1: COMPLETE — Streamlit running on port 8599

Acknowledged. Streamlit auto-selected port 8599 (8501 was likely in use). That's fine.

**IMPORTANT**: All subsequent test scripts must use `http://localhost:8599` NOT `http://localhost:8501`.

---

## 🔴 ORDER 2: Start MCP Server on Port 8001 (NOW)

```bash
export OLLAMA_BASE_URL=http://host.docker.internal:11434
export BROWSER_USE_MODEL=ollama/gemma4:e4b
nohup uvx --from browser-use[cli] browser-use --mcp --port 8001 > /a0/usr/workdir/tmp/mcp_server.log 2>&1 &
sleep 3
ps aux | grep -v grep | grep "browser-use.*mcp" && echo "MCP RUNNING" || echo "MCP NOT FOUND"
```

**Report**: "✅ ORDER 2: MCP running" or "❌ ORDER 2: FAILED — [error]" by editing this file.

---

## 🔴 ORDER 3: Run Vision TSK-04 (UPDATED PORT)

Save as `/a0/usr/workdir/scripts/vision_tsk04.py`:

```python
import asyncio
from browser_use import Agent, Browser

async def test_obs_workflow():
    browser = Browser(headless=False)
    agent = Agent(
        task="""
        1. Navigate to http://localhost:8599
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

## 🔴 ORDER 4: Run Vision TSK-06 (UPDATED PORT)

Save as `/a0/usr/workdir/scripts/vision_tsk06.py` (AFTER Order 3):

```python
import asyncio
from browser_use import Agent, Browser

async def test_adversarial():
    browser = Browser(headless=False)
    agent = Agent(
        task="""
        1. Navigate to http://localhost:8599, log in admin@turtledb.com / admin123
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

---

## 📋 Summary

| Order | Task | Status |
|-------|------|--------|
| 1 | Start Streamlit | ✅ COMPLETE (port 8599) |
| 2 | Start MCP server on 8001 | 🔴 EXECUTE NOW |
| 3 | TSK-04 Observations Workflow | 🔴 AFTER 2 |
| 4 | TSK-06 Adversarial Tests | 🔴 AFTER 3 |

---

**Execute ORDER 2 now. Update this file with results.**

— M6800 Team Lead
