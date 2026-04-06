# AppSheet UX & Automation Logic (Incubator Vault v2.0)

## 1. Health Indicator Expressions (Format Rules / Display)

### Chalking Level
- **Color Code:** 
  - `[chalking] = 0`: Gray/Neutral
  - `[chalking] = 1`: Light Blue (Developing)
  - `[chalking] = 2`: Bright White (Established)
- **Warning Icon:** 
  - Expression: `AND(HOUR(TODAY() - [egg_id].[created_at]) > 240, [chalking] = 0)`
  - Description: Flag if egg is > 10 days old with no chalking.

### Vascularity
- **Icon:** 
  - `[vascularity] = TRUE`: ❤️ (Strong Health)
  - `[vascularity] = FALSE`: ⚪ (Pending/Infertility Risk)
- **Infertility Risk Rule:** 
  - Expression: `AND(HOUR(TODAY() - [egg_id].[created_at]) > 360, [vascularity] = FALSE)`
  - Description: Risk flag if > 15 days with no vascularity.

### Critical Health (Molding/Leaking)
- **Molding:** 
  - `[molding] = TRUE`: 🍄 (Warning, isolation recommended)
- **Leaking:** 
  - `[leaking] = TRUE`: 💧 (Critical Alert)

---

## 2. Automation Bots & Workflows

### A. SystemLog Entry (Session Initiation)
- **Trigger:** On `SessionLog` [INSERT].
- **Action:** Add a row to `SystemLog` with:
  - `event_type`: 'SESSION_START'
  - `event_message`: 'User ' & [user_name] & ' initiated a new incubation session.'
  - `session_id`: [_THISROW].[session_id]

### B. Stage Alert (Mature Pipping Watch)
- **Trigger:** Every 24 hours (Scheduled Bot).
- **Filter:** `AND([current_stage] = 'Mature', HOUR(TODAY() - [updated_at]) > 1440)`
- **Action:** Send a notification to the observer: "Egg [egg_id] has been in the Mature stage for over 60 days. Switch to Pipping Watch!"

---

## 3. Quick Edit Toggles (UX Optimization)
- **Columns:** `vascularity`, `molding`, `leaking`, `current_stage`
- **Implementation:** Enable 'Quick Edit' on these columns in the Detail view of the `egg` table for rapid field entry.
