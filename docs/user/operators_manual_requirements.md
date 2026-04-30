# Requirements for the WINC Clinical Operator Manual Overhaul

## 1. OBJECTIVE

Produce a high-fidelity, comprehensive operator manual that empowers volunteer clinicians to manage turtle subjects with 100% accuracy. The manual must follow the **"Professional-Simplicity"** mandate: Enterprise-grade structure combined with 5th-grade level clarity and extensive visual logic. This version targets **Best-in-Class** institutional standards for the 2026 season.

---

## 2. AESTHETIC & STRUCTURAL STANDARDS

### A. Cover Page (Institutional Excellence)

- **Requirement**: Use the asset **operators_manual_cover_page.png**.
- **Branding**: Must include "Kevin Howland" as the lead developer/author in the PDF metadata.

### B. Graphical Placeholders (Mandatory)

- **Rule**: Every chapter must contain at least one high-impact graphical placeholder.
- **Asset**: Use `PLACEHOLDER_SCREENSHOT.png` (featuring a big, bold red "PLACEHOLDER" overlay) for all uncaptured UI elements.
- **Figure Identification**: Every image, diagram, and screenshot must be assigned a unique **Figure #** (e.g., *Figure 1: Title*).
- **Cross-Referencing**: The main body text must explicitly reference the graphic (e.g., "*...as shown in Figure 4*").
- **Captions**: Every figure must have a centered, italicized caption below the image.

### C. Controls & Navigation

- **Clickable TOC**: Must allow users to find any task in under 5 seconds.
- **Micro-Copy Alignment**: Every instruction must use the **EXACT** text found on the screen buttons (e.g., "Establishing Case," "START," "SAVE").

---

## 3. THE CLINICAL PROTOCOL (BIOLOGICAL BREADTH)

### A. The "Maternal Assessment" Guide

- **Requirement**: Detailed instructions for Carapace Measurement (mm) and Weight (g).
- **Visual**: **[PLACEHOLDER: CARAPACE MEASUREMENT TECHNIQUE DIAGRAM]**.

### B. The "Never Rotate" Biological Mandate

- **Requirement**: Full cross-section diagram explaining embryonic drowning and oxygen exchange.
- **Goal**: Move from "A rule to follow" to "A principle understood."

### C. Hatchling Vitality Scoring (0-5)

- **Requirement**: A visual rubric for movement strength and yolk sac absorption.
- **Visual**: **[PLACEHOLDER: HATCHLING VITALITY INDICATORS CHART]**.

---

## 4. SYSTEMS ANALYSIS & GOVERNANCE

### A. Vault Security (Sign-In)

- **Focus**: Detail the "Shift Rotation" process (how observers hand over the single workstation) and the "1-Hour Inactivity Rule."
- **Visual**: **[PLACEHOLDER: LOGIN SCREEN WITH OBSERVER SELECTOR]**.

### B. Forensic Reconciliation (Admin)

- **Focus**: Step-by-step CRUD (Create, Read, Update, Delete) for the Species Registry and Observer List.
- **Ghost Data**: Explain how to reconcile "Orphaned Eggs" using the Resurrection Vault.
- **Visual**: **[PLACEHOLDER: RESURRECTION VAULT - GHOST DATA ALERT VIEW]**.

### C. Analytical Interpretation (Reports)

- **Focus**: Decoding the Mortality Heatmap. Distinguishing between "Incubator Hotspots" (clustered failures) and "Genetic Failures" (singular failures).
- **WormD Governance**: Detailed field mapping for export packages.
- **Visual**: **[PLACEHOLDER: ANALYTICS DASHBOARD - MORTALITY HEATMAP OVERVIEW]**.

### D. Clinical Naming & Backdating Standards (§4.D)

- **Event-Based Architecture**: To align with clinical standards, the system must use "Action" naming for primary tables.
- **Primary Renaming Mandates**:
  - `mother` table → **`intake`**
  - `mother_id` → **`intake_id`**
  - `bin_date` → **`bin_date`**
- **Table-Specific Date Convention (Backdateable)**:
  - `intake_date` (In the `intake` table)
  - `bin_date` (In the `bin` table)
  - `bin_observation_date` (In the `bin_observation` table)
  - `egg_observation_date` (In the `egg_observation` table)
- **Requirement**: These dates must be editable to support retrospective data entry from paper logs.

---

## 5. RESILIENCE: THE "CATCH-UP" WORKFLOW (CRISIS)

### A. The Double-Witness Sync

- **Protocol**: When the internet returns, paper logs must be transcribed.
- **Requirement**: A separate validation step where a "Witness" verifies the Subject ID typing.
- **Visual**: **[PLACEHOLDER: PAPER LOG FORM MOCKUP V2026]**.

### B. Data Reconciliation Flowchart

- **Goal**: Visualize the path from offline data entry back to "Database Synced" status.

---

## 6. WORKFLOW EXPANSION (DETAILED STEPS)

### A. Supplemental Intake (CR-20260429-210932)

#### Bin Code Anatomy

Bin codes are deterministically auto-generated at intake time using the formula:

```
{species_code}{intake_number}-{finder_clean}-{bin_num}
```

| Component | Source | Example |
|-----------|--------|---------|
| `species_code` | `species.species_code` — alphabetic abbreviation | `BL` (Blanding's), `MK` (Stinkpot) |
| `intake_number` | `species.intake_count + 1` at time of intake | `1`, `2`, `3` |
| `finder_clean` | Finder name → UPPERCASED → non-alphanumeric stripped | `"6e6e"` → `6E6E` |
| `bin_num` | Sequential bin within this intake (1, 2, 3…) | `1`, `2`, `3` |

**Example sequence for Blanding's, intake #1, finder "6e6e":**
- Initial Bin 1 → `BL1-6E6E-1`
- Initial Bin 2 → `BL1-6E6E-2`
- Supplemental Bin → `BL1-6E6E-3` *(auto-incremented)*

#### Supplemental Bin Entry Requirements

- **Auto-Increment**: When an operator selects an Intake in the "Add Bin to Intake" expander, the system **must** auto-derive the next bin code by querying existing bins for that intake, parsing the trailing `bin_num`, and incrementing by 1. The operator confirms — they do not retype.
- **Form Parity**: The supplemental bin form must match the initial Intake bin entry format:
  - Read-only auto-populated **Bin Code** preview
  - **Bulk Egg Count** field (number input)
  - **Egg Intake Date** field
  - **SAVE** button
- **Data Integrity**: On save, egg records must be bulk-inserted matching the initial intake behavior (one egg record per egg, with `intake_date`, `bin_id`, observer metadata).
- **Visual**: **[PLACEHOLDER: ADD BIN TO INTAKE — SUPPLEMENTAL FORM WITH AUTO-INCREMENT PREVIEW]**


### B. The Hydration Recalibration

- Guidance on what to do when "Current Mass" is wildly different from "Last Recorded Weight" (substrate leak vs. simple evaporation).

---

## 7. STAGE STANDARDIZATION & BIOSECURITY GATES

### A. The Milestone-Substage Architecture

- **Requirement**: The manual must reflect the "Split-Stage" model (Milestone S1-S6 + Diagnostic Markers).
- **Granularity**: Detailed definitions for S2 (Spot/Band/Full), S4 (C-Stage/Term/Motion), and S6 (YA1/YA2/YA3).
- **Rationale**: Explain that milestones ensure reporting consistency while sub-stages track biological velocity during long developmental plateaus.

### B. The YA-3 Biosecurity Gate (Mandatory)

- **Requirement**: Explicit warning that **WormD Export** and system retirement are software-locked until **S6-YA3 (Fully Absorbed)** is achieved.
- **Clinical Warning**: Highlight the risk of fatal sepsis if subjects are released pre-absorption.
- **Configurability**: Mention that the specific "Min-Export Stage" is a system-wide setting managed by the Lab Director.

---

**Protocol Authority: khowland/turtle-egg-incubator-vault © 2026**
**Lead Systems Analyst: Senior Panel Audit v10.6.0**
