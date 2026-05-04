"""
Centralized Playwright Selectors for WINC Incubator v9.2.0
Generated from UI_SELECTOR_MAP_v9.0.0.md — source code audit of vault_views/*.py

Import this module in all E2E test files to ensure consistent selectors.
When the app version changes, update this file and UI_SELECTOR_MAP_v9.0.0.md together.
"""

# ---------------------------------------------------------------------------
# Page Headings (v9.2.0: emoji prefixes removed for E2E compatibility)
# ---------------------------------------------------------------------------
HEADING_DASHBOARD = "Today's Summary"
HEADING_INTAKE = "New Intake"
HEADING_OBSERVATIONS = "Observations"
HEADING_SETTINGS = "Settings"
HEADING_REPORTS = "Reports"

# ---------------------------------------------------------------------------
# Navigation Links
# ---------------------------------------------------------------------------
NAV_DASHBOARD = "a:has-text('Dashboard')"
NAV_INTAKE = "a:has-text('Intake')"
NAV_OBSERVATIONS = "a:has-text('Observations')"
NAV_SETTINGS = "a:has-text('Settings')"
NAV_REPORTS = "a:has-text('Reports')"

# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------
BTN_LOGIN_START = {"name": "START", "exact": True}
BTN_SAVE = "SAVE"  # Use .first for weight gate, .last for matrix, no qualifier for intake
BTN_START_ALL_EGGS = {"name": "START"}  # Selects all pending eggs in grid

# ---------------------------------------------------------------------------
# Input Keys (Playwright Locator objects or patterns)
# ---------------------------------------------------------------------------
INPUT_FINDER = "input[aria-label='Finder']"
INPUT_WINC_CASE = "input[aria-label='WINC Case #']"
INPUT_WEIGHT_GATE = {"selector": "[data-testid='stNumberInput'] input", "index": "first"}
INPUT_WATER_ADDED = {"selector": "[data-testid='stNumberInput'] input", "index": 1}  # 2nd number input
INPUT_INCUBATOR_TEMP = {"selector": "[data-testid='stNumberInput'] input", "index": 2}  # 3rd number input
INPUT_EGG_COUNT = {"selector": "[data-testid='stDataEditor'] input[type='number']", "index": "first"}
INPUT_BACKDATE_OBS = {"selector": "[data-testid='stDateInput'] input", "index": "first"}
INPUT_OBS_NOTES = {"selector": "[data-testid='stTextArea'] textarea", "index": "first"}

# ---------------------------------------------------------------------------
# Workbench & Multiselect
# ---------------------------------------------------------------------------
MULTISELECT_WORKBENCH = "[data-testid='stMultiSelect']"
MULTISELECT_DROPDOWN_OPTION = "[data-testid='stMultiSelectDropdown'] li:has-text('{bin_id}')"

# ---------------------------------------------------------------------------
# Selectboxes — label patterns and dropdown option template
# ---------------------------------------------------------------------------
SELECTBOX_STAGE = "[data-testid='stSelectbox']:has-text('Stage')"
SELECTBOX_STATUS = "[data-testid='stSelectbox']:has-text('Status')"
SELECTBOX_CHALKING = "[data-testid='stSelectbox']:has-text('Chalking')"
SELECTBOX_MOLDING = "[data-testid='stSelectbox']:has-text('Molding')"
SELECTBOX_LEAKING = "[data-testid='stSelectbox']:has-text('Leaking')"
SELECTBOX_DENTING = "[data-testid='stSelectbox']:has-text('Denting')"
SELECTBOX_DROPDOWN_OPTION = "[data-testid='stSelectboxVirtualDropdown'] li:has-text('{option}')"

# Fallback: any selectbox
SELECTBOX_ANY = "[data-testid='stSelectbox']"

# ---------------------------------------------------------------------------
# Correction Mode Toggle (v9.2.0: emoji prefix removed)
# ---------------------------------------------------------------------------
TOGGLE_CORRECTION_MODE = "Correction Mode"
TOGGLE_CORRECTION_FALLBACK = "[data-testid='stToggle']"

# ---------------------------------------------------------------------------
# Grid Elements
# ---------------------------------------------------------------------------
TEXT_BIOLOGICAL_GRID = "Biological Grid"
CHECKBOX_EGG_TEMPLATE = "[data-testid='stCheckbox']:has-text('{egg_id}')"
