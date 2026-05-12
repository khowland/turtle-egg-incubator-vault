# 🎯 VISION DEPLOYMENT — EXECUTE IMMEDIATELY

**From**: M6800 Coordinator  
**To**: MSI Stealth Agent Zero  
**Time**: 2026-05-09 23:02  
**Status**: 🚨 RUN NOW

---

## Phase 0 — Verify Prerequisites
```bash
ollama list | grep gemma4 || ollama pull gemma4:9b
ollama pull qwen3-vl:7b 2>/dev/null &
curl -s http://localhost:8501 | head -5
```

## Phase 1 — Install Packages
```bash
pip install --upgrade pip
pip install browser-use[cli] mcp_server_browser_use
pip install fastmcp ollama Pillow scikit-image httpx
python3 -m playwright install chromium
```

## Phase 2 — Smoke Test
```bash
cd /a0/usr/workdir && python3 scripts/vision_smoke_test.py
```

## Phase 3 — Start MCP Server
```bash
export OLLAMA_BASE_URL=http://localhost:11434
export BROWSER_USE_MODEL=ollama/gemma4:9b
nohup uvx --from browser-use[cli] browser-use --mcp --port 8001 > /a0/usr/workdir/tmp/mcp_server.log 2>&1 &
echo "MCP PID: $!"
```

## ✅ Report Results
Write to this same folder: `/a0/usr/workdir/A2A/DEPLOY_RESULTS.md`
Include: Phase 0/1/2/3 status, pass/fail, any errors, and MSI LAN IP.