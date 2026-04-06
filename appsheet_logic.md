# DEPRECATED: AppSheet UX & Automation Logic

> **This file is DEPRECATED.** The project no longer uses AppSheet.
> All UI logic has been migrated to the web application (see `Requirements.md` and `app.py`).
> This file is retained for historical reference only.

---

_Original content below (for reference):_

## 1. Health Indicator Expressions (Now implemented in UI guardrails)

### Chalking Level
- `chalking = 0` + age > 10 days → Warning flag
- `chalking = 1` → Developing indicator
- `chalking = 2` → Established indicator

### Vascularity
- `vascularity = TRUE` → ❤️ Strong Health
- `vascularity = FALSE` + age > 15 days → Infertility Risk flag

### Critical Health
- `molding = TRUE` → 🍄 Isolation alert
- `leaking = TRUE` → 💧 Critical alert

## 2. Automation Logic (Now implemented in SystemLog)
- Session initiation → SystemLog entry
- Mature stage watch → Dashboard guardrail alert
