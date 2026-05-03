# Sub-Agent & Skills Orchestration (auto-injected)
- **Coordination model**: Agent0 is coordinator; delegate tasks to specialized subordinates, not full problems.
- **Sub-agent dispatch**: For each discrete task, use a fresh subordinate with `reset=true` to keep token weight low.
- **Profile selection**: Use `developer` for code changes, `researcher` for analysis, `hacker` for security testing.
- **After each delegated task**: test, commit, and advance before next dispatch.
- **Skill usage**: Load domain skills (wisc-turtle-incubation-expert, obsidian) with `skills_tool:load` when working on biology, clinical data, or Obsidian-flavored markdown.
- **Workflow artifacts**: Respect `.agents/workflows/` definitions for multi-step processes (e.g., sync-manual.md).
- **Documentation alignment**: All changes must align with Requirements.md and implied_system_objective.md.
