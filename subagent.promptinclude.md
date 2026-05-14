# Sub-Agent & Skills Orchestration (auto-injected)
- **Coordination model**: Agent0 is coordinator; delegate tasks to specialized subordinates, not full problems.
- **Sub-agent dispatch**: For each discrete task, use a fresh subordinate with `reset=true` to keep token weight low.
- **Profile selection**: Use `developer` for code changes, `researcher` for analysis, `hacker` for security testing.
- **After each delegated task**: test, commit, and advance before next dispatch.
- **Skill usage**: Load domain skills (wisc-turtle-incubation-expert, obsidian) with `skills_tool:load` when working on biology, clinical data, or Obsidian-flavored markdown.
- **Workflow artifacts**: Respect `.agents/workflows/` definitions for multi-step processes (e.g., sync-manual.md).
**🚫 No MSI Stealth / A2A**: MSI Stealth workstation removed from stack permanently. All A2A communication is disabled. All work is 100% local on M6800. Vision QA uses built-in browser tool + vision_load + deepseek_pro MCP (NOT browser_use, NOT Ollama, NOT A2A). The A2A/ folder is deleted. VISION_DEPLOYMENT_PLAN_MSI_STEALTH.md is deprecated.
- **Documentation alignment**: All changes must align with Requirements.md and implied_system_objective.md.
