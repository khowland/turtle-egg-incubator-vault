# v9.0.0 UI Selector Map
**For Playwright E2E Tests**
**Generated:** 2026-05-03 | **Basis:** Source code audit of vault_views/*.py

---

## Page Headings (use `page.get_by_role("heading", name="...")`)

| Page | View File | Heading Text | Notes |
|---|---|---|---|
| Login / Splash | 0_Login.py | (no heading — custom HTML h1: "🐢 Welcome!") | Button label: "START" |
| Dashboard | 1_Dashboard.py | `📊 Today's Summary` | Post-login landing page |
| Intake | 2_New_Intake.py | `🛡️ New Intake` | SAVE with label "SAVE" redirects to Observations via `st.switch_page` |
| Observations | 3_Observations.py | `🔬 Observations` | Weight gate uses key `wt_gate`; SAVE buttons: `.first` = weight gate, `.last` = matrix |
| Settings | 5_Settings.py | `⚙️ Settings` | Vault Admin section contains WIPE controls |
| Reports | 6_Reports.py | `🛡️ Reports` | Read-only; sidebar filters |
| Diagnostic | 7_Diagnostic.py | (verify) | |
| Help | 8_Help.py | (verify) | |

## Navigation Links

| Link Text | Selector Pattern |
|---|---|
| Dashboard | `a:has-text('Dashboard')` or `a:has-text('Summary')` |
| Intake | `a:has-text('Intake')` |
| Observations | `a:has-text('Observations')` |
| Settings | `a:has-text('Settings')` |
| Reports | `a:has-text('Reports')` |

## Key Buttons

| Label | Location | Playwright Locator |
|---|---|---|
| START | Login form | `page.get_by_role('button', name='START', exact=True)` |
| SAVE (intake) | 2_New_Intake.py | `page.get_by_role('button', name='SAVE')` — single SAVE on intake |
| SAVE (weight gate) | 3_Observations.py hydration gate | `page.get_by_role('button', name='SAVE').first` |
| SAVE (observation matrix) | 3_Observations.py property matrix | `page.get_by_role('button', name='SAVE').last` |
| START (select all eggs) | 3_Observations.py grid | `page.get_by_role('button', name='START')` |
| WIPE & SET CLEAN START | 5_Settings.py Vault Admin | Requires text input "OBLITERATE CURRENT DATA" first |

## Critical Input Keys

| Purpose | Key | Selector |
|---|---|---|
| Weight gate (bin mass) | `wt_gate` | `page.locator("[data-testid='stNumberInput'] input").first` |
| Water added | (auto-keyed) | 2nd `stNumberInput` |
| Incubator temp | `obs_temp` | 3rd `stNumberInput` |
| Finder name | (aria-label) | `page.locator("input[aria-label='Finder']")` |
| WINC Case # | (aria-label) | `page.locator("input[aria-label='WINC Case #']")` |
| Egg count (data editor) | (stDataEditor) | `page.locator("[data-testid='stDataEditor'] input[type='number']").all()[0]` |
| Observation notes | (stTextArea) | `page.locator("[data-testid='stTextArea'] textarea").first` |
| Backdate obs | `backdate_obs` | `page.locator("[data-testid='stDateInput'] input").all()[0]` |

## Workbench & Multiselect

| Element | Selector |
|---|---|
| Workbench multiselect | `page.locator("[data-testid='stMultiSelect']").first` |
| Dropdown option | `f"[data-testid='stMultiSelectDropdown'] li:has-text('{bin_id}')"` |

## Selectboxes

| Label Pattern | Selector |
|---|---|
| Stage | `page.locator("[data-testid='stSelectbox']:has-text('Stage')")` |
| Status | `page.locator("[data-testid='stSelectbox']:has-text('Status')")` |
| Chalking | `page.locator("[data-testid='stSelectbox']:has-text('Chalking')")` |
| Molding | `page.locator("[data-testid='stSelectbox']:has-text('Molding')")` |
| Leaking | `page.locator("[data-testid='stSelectbox']:has-text('Leaking')")` |
| Denting | `page.locator("[data-testid='stSelectbox']:has-text('Denting')")` |
| Dropdown options | `"[data-testid='stSelectboxVirtualDropdown'] li:has-text('{option}')"` |

## Correction Mode Toggle

| Element | Selector |
|---|---|
| Toggle label | `"🛠️ Correction Mode"` — `page.locator("[data-testid='stToggle']").last` as fallback |

## Grid Elements

| Element | Selector |
|---|---|
| Biological Grid heading | `page.get_by_text("Biological Grid")` |
| Egg checkboxes | `page.locator(f"[data-testid='stCheckbox']:has-text('{egg_id}')")` |
| START button | `page.get_by_role("button", name="START")` |

## Post-Intake SAVE Behavior
- `st.switch_page("vault_views/3_Observations.py")` is called after successful intake SAVE
- The page URL does NOT change (Streamlit SPA navigation)
- The Observations heading (`🔬 Observations`) should appear after rerun completes
- Tests should wait for the Observations heading with a 30s timeout, then explicitly click the Observations nav link to ensure correct state

## Dashboard Post-Login
- After clicking START on login form, Streamlit reruns and shows `📊 Today's Summary` heading
- Session may be resumed if a recent session exists for the same observer
- `st.rerun()` is called at end of login handler (session.py line 200)
