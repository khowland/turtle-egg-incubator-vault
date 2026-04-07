# 🐢 VAULT ELITE: Master Requirements (v6.0 — The Biologist's Edition)

## 1. MISSION & PERSONA
**The Biologist:** Expert Wisconsin Turtle Biologist managing a salvage-to-hatch program for at-risk species (Blanding's, Wood, Ornate Box).  
**The App:** A high-performance, mobile-first web application for tracking life-cycles from traumatic harvest (DOA/Injured mothers) through incubation to release. Must also support **living mothers** who lay eggs over a period of days.

---

## 2. BIOLOGICAL ARCHITECTURE (SCHEMA)

### **A. Mother Metadata (The Source)**
| Column | Type | Required | Notes |
|---|---|---|---|
| `mother_id` | TEXT PK | Auto | Clue Chain: `[Name]_[Species]_[YYYYMMDD]` |
| `mother_name` | TEXT | ✅ | Origin identifier (e.g., "Shelly") |
| `species_id` | TEXT FK | ✅ | References `species` table |
| `condition` | TEXT | ✅ | Enum: `Healthy`, `Injured`, `DOA`, `Post-Mortem Harvest` |
| `intake_date` | DATE | ✅ | Default: today |
| `harvest_location` | TEXT | ❌ | GPS or description (e.g., "Hwy 12 & Cty P") |
| `gps_lat` | NUMERIC | ❌ | Latitude if GPS available |
| `gps_lon` | NUMERIC | ❌ | Longitude if GPS available |
| `clinical_notes` | TEXT | ❌ | Injury details, cause of death, vet observations |
| `notes` | TEXT | ❌ | General notes |
| `created_by_session` | TEXT FK | Auto | Session that created this record |
| `updated_by_session` | TEXT FK | Auto | Session that last updated |
| `is_deleted` | BOOLEAN | Auto | Soft delete flag, default FALSE |

### **B. Bin Metadata (Egg Container)**
One mother may have **multiple bins** (eggs laid on different days, or overflow container).

| Column | Type | Required | Notes |
|---|---|---|---|
| `bin_id` | TEXT PK | Auto | Clue Chain: `[MotherID]_B[N]` |
| `mother_id` | TEXT FK | ✅ | References `mother` |
| `harvest_date` | DATE | ✅ | Default: today |
| `total_eggs` | INTEGER | ✅ | Max 300 |
| `substrate` | TEXT | ❌ | `Vermiculite`, `Perlite`, `Sphagnum Moss`, `Sand Mix` |
| `bin_label` | TEXT | ❌ | Physical label on the container |
| `created_by_session` | TEXT FK | Auto | |
| `updated_by_session` | TEXT FK | Auto | |
| `is_deleted` | BOOLEAN | Auto | Default FALSE |

### **C. Egg Record**
| Column | Type | Required | Notes |
|---|---|---|---|
| `egg_id` | TEXT PK | Auto | Clue Chain: `[BinID]_E[N]` |
| `bin_id` | TEXT FK | ✅ | References `bin` |
| `physical_mark` | INTEGER | ❌ | Number written on egg shell |
| `mark_description` | TEXT | ❌ | "Top dot", "X on left" |
| `current_stage` | TEXT | Auto | Default: `Intake`. Enum: see Life Stages below |
| `status` | TEXT | Auto | Default: `Active`. Enum: `Active`, `Dead`, `Hatched` |
| `created_by_session` | TEXT FK | Auto | |
| `updated_by_session` | TEXT FK | Auto | |
| `is_deleted` | BOOLEAN | Auto | Default FALSE |

**Life Stages (ordered):** `Intake` → `Developing` → `Vascular` → `Mature` → `Pipping` → `Hatched` → `Released`

### **D. Egg Observation (Append-Only History)**
Each observation is a snapshot in time. Never overwritten — new rows are appended.

| Column | Type | Required | Notes |
|---|---|---|---|
| `detail_id` | BIGINT PK | Auto | Identity column |
| `session_id` | TEXT FK | Auto | Current session |
| `egg_id` | TEXT FK | ✅ | Which egg |
| `observer_id` | TEXT FK | Auto | Who observed |
| `timestamp` | TIMESTAMPTZ | Auto | Default: NOW() |
| `chalking` | INTEGER | ❌ | 0=None, 1=Partial, 2=Full |
| `vascularity` | BOOLEAN | ❌ | TRUE = veins visible via candling |
| `molding` | BOOLEAN | ❌ | Fungal growth detected |
| `leaking` | BOOLEAN | ❌ | Fluid escaping shell |
| `dented` | BOOLEAN | ❌ | Shell dent detected |
| `discolored` | BOOLEAN | ❌ | Abnormal coloring |
| `stage_at_observation` | TEXT | ❌ | Stage at time of observation |
| `notes` | TEXT | ❌ | Free text |
| `is_deleted` | BOOLEAN | Auto | Default FALSE |

### **E. Incubator Observation (Environment Telemetry)**
| Column | Type | Required | Notes |
|---|---|---|---|
| `obs_id` | TEXT PK | Auto | `[SessionID]_ENV_[HHMMSS]` |
| `session_id` | TEXT FK | Auto | |
| `bin_id` | TEXT FK | ❌ | Optional specific bin |
| `observer_id` | TEXT FK | Auto | |
| `timestamp` | TIMESTAMPTZ | Auto | Default: NOW() |
| `ambient_temp` | NUMERIC | ✅ | Temperature in °F |
| `humidity` | NUMERIC | ✅ | Humidity in % |
| `notes` | TEXT | ❌ | |
| `is_deleted` | BOOLEAN | Auto | Default FALSE |

### **F. Observer Registry (Lookup Table)**
| Column | Type | Required | Notes |
|---|---|---|---|
| `observer_id` | TEXT PK | Manual | Short slug: "elisa", "kevin" |
| `display_name` | TEXT | ✅ | "Elisa Rodriguez" |
| `role` | TEXT | ✅ | `Lead`, `Staff`, `Volunteer` |
| `email` | TEXT | ❌ | |
| `phone` | TEXT | ❌ | |
| `is_active` | BOOLEAN | Auto | Default TRUE |
| `is_deleted` | BOOLEAN | Auto | Default FALSE |
| `created_at` | TIMESTAMPTZ | Auto | Default NOW() |

| Column | Type | Required | Notes |
|---|---|---|---|
| `species_id` | TEXT PK | Manual | "Blandings", "Wood", "Ornate" |
| `common_name` | TEXT | ✅ | Unique |
| `scientific_name` | TEXT | ✅ | Unique |
| `incubation_min_days` | INTEGER | ❌ | |
| `incubation_max_days` | INTEGER | ❌ | |
| `optimal_temp_low` | NUMERIC | ❌ | °F |
| `optimal_temp_high` | NUMERIC | ❌ | °F |
| `vulnerability_status` | TEXT | ❌ | "Common", "Threatened (WI)", "Endangered (WI)" |

### **I. Session & Audit Tables**
**SessionLog:**
| Column | Type | Notes |
|---|---|---|
| `session_id` | TEXT PK | `[observer_id]_[YYYYMMDDHHMMSS]` |
| `user_name` | TEXT | Observer display name |
| `login_timestamp` | TIMESTAMPTZ | Default NOW() |
| `user_agent` | TEXT | Browser/device info |

**SystemLog:**
| Column | Type | Notes |
|---|---|---|
| `log_id` | BIGINT PK | Auto identity |
| `session_id` | TEXT FK | References SessionLog |
| `event_type` | TEXT | See Event Types table below |
| `event_message` | TEXT | Human-readable description |
| `payload` | JSONB | Structured event data |
| `timestamp` | TIMESTAMPTZ | Default NOW() |

**SystemLog Event Types:**
| `event_type` | Trigger | `payload` contents |
|---|---|---|
| `SESSION_START` | Observer selected in sidebar | `{observer_id, user_agent}` |
| `INTAKE_COMPLETE` | Burst intake saved | `{mother_id, bin_id, egg_count}` |
| `OBSERVATION_BATCH` | Batch observation saved | `{egg_ids: [...], changes: {...}}` |
| `ENV_LOG` | Environment reading saved | `{incubator_label, temp, humidity}` |
| `STAGE_CHANGE` | Egg stage transition | `{egg_id, from_stage, to_stage}` |
| `CRUD_CREATE` | Lookup record created | `{table, record_id}` |
| `CRUD_UPDATE` | Lookup record updated | `{table, record_id, changes}` |
| `CRUD_DELETE` | Soft delete performed | `{table, record_id}` |
| `ALERT_TRIGGERED` | Biological guardrail fired | `{alert_type, egg_id, details}` |
| `EXPORT` | Data exported | `{format, row_count}` |
| `ERROR` | Any operation failure | `{operation, error_message}` |

### **J. Clue Chain Triggers**
All primary keys are auto-generated via PostgreSQL `BEFORE INSERT` triggers:
- **Mother:** `[Name]_[Species]_[YYYYMMDD]` → e.g., `Shelly_Blandings_20260406`
- **Bin:** `[MotherID]_B[N]` → e.g., `Shelly_Blandings_20260406_B1`
- **Egg:** `[BinID]_E[N]` → e.g., `Shelly_Blandings_20260406_B1_E1`
- **Observation:** `[SessionID]_ENV_[HHMMSS]`

---

## 3. UI/UX DESIGN SYSTEM: "BENTO-GLASS 2026"

### 3.1 Design Tokens
```
COLOR PALETTE
─────────────────────────────────────
Background:       #020617   (Deep Space Navy)
Surface:          #0F172A   (Dark Slate)
Card Glass:       rgba(30, 41, 59, 0.45) + blur(20px)
Primary Accent:   #10B981   (Emerald)
Primary Hover:    #34D399   (Light Emerald)
Danger:           #EF4444   (Red)
Warning:          #F59E0B   (Amber)
Info:             #3B82F6   (Blue)
Text Primary:     #FFFFFF   (Titanium White)
Text Muted:       #94A3B8   (Slate 400)

TYPOGRAPHY
─────────────────────────────────────
Font:         Inter (Google Fonts)
H1:           2.5rem / 900 weight
H2:           1.8rem / 800 weight
Body:         1.1rem / 400 weight
Labels:       1.0rem / 700 weight
Buttons:      1.2rem / 900 weight

SPACING & TOUCH TARGETS
─────────────────────────────────────
Button Height: 65–75px (Wet-Hand Touch Targets)
Card Padding:  24px
Card Radius:   20px
Input Radius:  12px
Gap:           16px
```

### 3.2 Glass Card Component
Every major content block is wrapped in a glass card:
```css
.glass-card {
    background: rgba(30, 41, 59, 0.45);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
```

### 3.3 Emergency Pulse Animation
For critical health alerts (Molding, Leaking):
```css
@keyframes pulse-danger {
    0%, 100% { box-shadow: 0 0 8px rgba(239, 68, 68, 0.4); }
    50% { box-shadow: 0 0 24px rgba(239, 68, 68, 0.8); }
}
.alert-critical {
    animation: pulse-danger 1.5s ease-in-out infinite;
    border: 2px solid #EF4444;
}
```

### 3.4 Mobile-First Rules
- All layouts must work on phone screens (360px width minimum) with gloved, wet hands.
- Use dropdowns (`selectbox`) over text input wherever possible to reduce keyboard use.
- Minimum touch target: 65px height on all interactive elements.
- Sidebar collapses on mobile — observer name shown in header as fallback.
- Egg card grid: 2 columns on mobile, 3–4 on desktop.

---

## 4. NAVIGATION & LAYOUT

### Sidebar (Persistent on All Pages)
```
┌──────────────────────────┐
│   🐢 VAULT ELITE PRO    │
│   BUILD: v5.0            │
│                          │
│   [Lottie Turtle Anim]   │
│                          │
│   👤 Observer: [Dropdown] │  ← PERSISTENT — drives all audit
│   ────────────────────── │
│                          │
│   📊 DASHBOARD           │
│   🐣 NEW INTAKE          │
│   🔍 OBSERVATIONS        │
│   🌡️ ENVIRONMENT LOG     │
│   🛠️ ADMIN REGISTRY      │
│   📈 ANALYTICS           │
│                          │
│   [🔄 NEURAL REFRESH]    │
│   Session: elisa_2026... │
└──────────────────────────┘
```

**Observer Dropdown Behavior:**
- Populated from `observer` table where `is_active = TRUE`.
- On selection: generates `session_id` = `{observer_id}_{YYYYMMDDHHMMSS}`, inserts `SessionLog` row, stores in session state.
- If no observer selected: **all write operations are blocked** — pages render in read-only mode with a warning banner: _"⚠️ Please select an observer to enable data entry."_
- Persists across page navigations via session state.

---

## 5. CORE WORKFLOWS

### W1: MOTHER INTAKE + EGG BATCH REGISTRATION

#### User Stories
> _"I just received a DOA Blanding's from Hwy 12. I harvested 14 eggs. I need to register the mother and all eggs in under 2 minutes with gloves on."_

> _"Maple (Wood Turtle) arrived injured 3 days ago. She laid 6 eggs yesterday and 4 more today. I need to add a second bin under the same mother."_

#### Two Scenarios

| Scenario | Mother Status | Sessions | Bin Behavior |
|---|---|---|---|
| **A: DOA / Post-Mortem** | Deceased — one harvest | 1 session | One bin, all eggs at once |
| **B: Living Mother** | Alive, laying over days | Multiple sessions | New bin per laying event, same mother |

#### Step 1 — Mother Registration / Lookup

```
┌────────────────────────────────────────────────────────────────┐
│  🐣 NEW INTAKE — Step 1 of 4: MOTHER                          │
│  ──────────────────────────────────────────────────────────────│
│                                                                │
│  ┌─ GLASS CARD ──────────────────────────────────────────────│
│  │                                                            │
│  │  Mother Name (Origin ID)     Species Class                 │
│  │  ┌────────────────────┐      ┌──────────────────────────┐ │
│  │  │ e.g. "Shelly"      │      │ ▼ Blanding's Turtle      │ │
│  │  └────────────────────┘      └──────────────────────────┘ │
│  │                                                            │
│  │  Condition                   Intake Date                   │
│  │  ┌──────────────────────┐    ┌──────────────────────────┐ │
│  │  │ ▼ DOA                │    │ 📅 2026-04-06 [auto]     │ │
│  │  └──────────────────────┘    └──────────────────────────┘ │
│  │                                                            │
│  │  Harvest Location (GPS or Description)                     │
│  │  ┌────────────────────────────────────────────────────── │
│  │  │ e.g. "Hwy 12 & Cty P, near culvert"                  │ │
│  │  └────────────────────────────────────────────────────── │
│  │                                                            │
│  │  Clinical Notes                                            │
│  │  ┌────────────────────────────────────────────────────── │
│  │  │ e.g. "Severe carapace fracture, eggs visible."        │ │
│  │  └────────────────────────────────────────────────────── │
│  │                                                            │
│  │  ┌────────────────────────────────────────────────────── │
│  │  │          ▶ NEXT: ASSIGN BIN & INCUBATOR               │ │
│  │  └────────────────────────────────────────────────────── │
│  └────────────────────────────────────────────────────────── │
└────────────────────────────────────────────────────────────────┘
```

**Field Definitions:**
| Field | Input Type | Required | Default | Validation |
|---|---|---|---|---|
| Mother Name | `text_input` | ✅ | — | Min 2 chars |
| Species | `selectbox` | ✅ | — | From `species` table |
| Condition | `selectbox` | ✅ | — | `Healthy`, `Injured`, `DOA`, `Post-Mortem Harvest` |
| Intake Date | `date_input` | ✅ | Today | Cannot be future date |
| Harvest Location | `text_input` | ❌ | — | — |
| Clinical Notes | `text_area` | ❌ | — | — |

**Identity Check Logic (runs when Name + Species are entered):**
```
Query: SELECT * FROM mother WHERE mother_name ILIKE ? AND species_id = ?
If found:
  ┌─ WARNING CARD (amber border) ─────────────────────────────┐
  │  ⚠️ A mother named "Maple" (Wood Turtle) already exists.  │
  │  Intake Date: 2026-04-03  │  Condition: Injured            │
  │  Current Bins: 1  │  Total Eggs: 6                        │
  │                                                            │
  │  [✅ Use Existing — Add New Bin]    [✏️ Create New Mother] │
  └────────────────────────────────────────────────────────────┘
  
  If "Use Existing" → skip to Step 2 with existing mother_id
  If "Create New" → continue (trigger generates unique ID via date)
```

#### Step 2 — Bin Assignment

```
┌────────────────────────────────────────────────────────────────┐
│  🐣 NEW INTAKE — Step 2 of 4: BIN SETUP                       │
│  ──────────────────────────────────────────────────────────────│
│                                                                │
│  ┌─ GLASS CARD ──────────────────────────────────────────────│
│  │  Mother: Shelly (Blanding's Turtle) — DOA                 │
│  │  Clue Chain Preview: Shelly_Blandings_20260406             │
│  │  ─────────────────────────────────────────────            │
│  │                                                            │
│  │  Harvest Date              Incubator                  │
│  │  ┌─────────────────────┐   ┌──────────────────────────┐  │
│  │  │ 📅 2026-04-06       │   │ ▼ INC-01: Incubator Alpha│  │
│  │  └─────────────────────┘   └──────────────────────────┘  │
│  │                                                            │
│  │  Substrate Type             Bin Label (Physical)           │
│  │  ┌─────────────────────┐   ┌──────────────────────────┐  │
│  │  │ ▼ Vermiculite       │   │ e.g. "Shelf A, Bin 3"    │  │
│  │  └─────────────────────┘   └──────────────────────────┘  │
│  │                                                            │
│  │  Egg Count                                                 │
│  │  ┌───────────────────────────────────────────┐            │
│  │  │  [  -  ]     15     [  +  ]               │            │
│  │  └───────────────────────────────────────────┘            │
│  │                                                            │
│  │  ⚡ System will generate 15 tracked egg records            │
│  │                                                            │
│  │  ┌──────────────────┐  ┌──────────────────────────────┐  │
│  │  │  ◀ BACK: MOTHER  │  │  ▶ NEXT: REVIEW & CONFIRM   │  │
│  │  └──────────────────┘  └──────────────────────────────┘  │
│  └────────────────────────────────────────────────────────── │
└────────────────────────────────────────────────────────────────┘
```

**Field Definitions:**
| Field | Input Type | Required | Default | Validation |
|---|---|---|---|---|
| Harvest Date | `date_input` | ✅ | Today | Cannot be future |
| Incubator | `selectbox` | ✅ | — | From `incubator` table (active only) |
| Substrate | `selectbox` | ❌ | Vermiculite | `Vermiculite`, `Perlite`, `Sphagnum Moss`, `Sand Mix` |
| Bin Label | `text_input` | ❌ | — | Physical label text |
| Egg Count | `number_input` | ✅ | 10 | Min 1, Max 100, Step 1 |

**Live Preview:**
```
Clue Chain: Shelly_Blandings_20260406_B1 → Eggs: E1 through E15
```

#### Step 3 — Egg Generation (Automatic)
No user input. The system shows what will be created:
```
⚡ Ready to generate:
  • 15 egg records: Shelly_Blandings_20260406_B1_E1 through _E15
  • All set to Stage: Intake, Status: Active
```

#### Step 4 — Confirmation & Save

```
┌────────────────────────────────────────────────────────────────┐
│  🐣 NEW INTAKE — Step 4 of 4: CONFIRM                         │
│  ──────────────────────────────────────────────────────────────│
│                                                                │
│  ┌─ SUMMARY CARD (glass) ───────────────────────────────────│
│  │  🐢 Mother:      Shelly (Blanding's Turtle)               │
│  │  📍 Location:    Hwy 12 & Cty P                           │
│  │  🩺 Condition:   DOA                                      │
│  │  📦 Incubator:   Main Unit                  │
│  │  🧪 Substrate:   Vermiculite                              │
│  │  🥚 Eggs:        15                                       │
│  │  🔗 Bin ID:      Shelly_Blandings_20260406_B1             │
│  │  📅 Harvested:   2026-04-06                               │
│  │  👤 Logged by:   Elisa Rodriguez                          │
│  └────────────────────────────────────────────────────────── │
│                                                                │
│  ┌────────────────────────────────────────────────────────── │
│  │       🚀 SAVE INTAKE & REGISTER 15 EGGS                   │
│  └────────────────────────────────────────────────────────── │
└────────────────────────────────────────────────────────────────┘
```

**Atomic Transaction on Save:**
1. Insert `mother` (if new) → trigger generates `mother_id`
2. Insert `bin` → trigger generates `bin_id`
3. Batch insert N `egg` records → trigger generates each `egg_id`
4. Insert `SystemLog` → `event_type: INTAKE_COMPLETE`, payload: `{mother_id, bin_id, egg_count}`
5. Display success message + celebration animation

**Session State Keys for Wizard:**
```python
st.session_state['intake_step'] = 1       # 1, 2, 3, or 4
st.session_state['intake_mother'] = {}     # name, species, condition, location, notes
st.session_state['intake_existing_mother_id'] = None  # set if using existing mother
st.session_state['intake_bin'] = {}        # harvest_date, incubator_label, substrate, egg_count
```

#### Edge Cases
| Case | Handling |
|---|---|
| Living mother returns days later | User searches existing mother → "Use Existing" → creates new bin (Step 2) only |
| Same name, different species | Clue Chain differentiates: `Maple_Wood_20260406` vs `Maple_Painted_20260406` |
| Same mother, same day, overflow | Bin counter auto-increments: `_B1`, `_B2`, `_B3` |
| Zero eggs entered | Validation rejects — minimum 1 |
| Network failure mid-save | Transaction fails atomically — no partial data. User retries. |
| User clicks BACK | Form state preserved in session state; no data lost |

---

### W2: RAPID OBSERVATION LOGGING

#### User Stories
> _"I candled all 14 eggs in Shelly's bin. Eight show vascularity and chalking level 2. I need to select those 8 and record the observation in one action."_

> _"Egg E5 has mold. I need to flag it separately as critical."_

#### Flow
```
1. FILTER    → Select Mother / Bin / Stage to narrow the view
2. VIEW      → Egg card grid showing current state of each egg
3. SELECT    → Multi-select eggs via checkboxes
4. OBSERVE   → Batch observation panel appears below
5. SAVE      → One EggObservation row per selected egg
6. REPEAT    → Grid refreshes; select different eggs if needed
```

#### Filter Bar
```
┌─────────────────────────────────────────────────────────────────┐
│  Mother: [▼ All / Shelly / Maple]   Bin: [▼ All / B1 / B2]    │
│  Stage:  [▼ All / Developing / Mature]   Status: [▼ Active]   │
└─────────────────────────────────────────────────────────────────┘
```
- Bin dropdown cascades from Mother selection (shows only bins for that mother).
- Status defaults to "Active" — hides Dead/Hatched eggs by default.
- A "Select All Visible" checkbox at the top of the grid.

#### Egg Card Grid
Each egg renders as a compact **bento card** showing its latest known state:
```
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ ☑ E1            │   │ ☑ E2            │   │ ☐ E3            │
│ ──────────────  │   │ ──────────────  │   │ ──────────────  │
│ Stage: Developing│   │ Stage: Vascular │   │ Stage: Mature   │
│ Chalk: ●○  (1)  │   │ Chalk: ●●  (2)  │   │ Chalk: ●●  (2)  │
│ Vasc:  ❤️  YES   │   │ Vasc:  ❤️  YES   │   │ Vasc:  ❤️  YES   │
│ Day 18          │   │ Day 18          │   │ Day 45          │
│ ✅ Healthy       │   │ ✅ Healthy       │   │ ⚠️ Pipping Watch │
└─────────────────┘   └─────────────────┘   └─────────────────┘

┌─────────────────┐   ┌═════════════════┐
│ ☐ E4            │   ║ ☐ E5  🍄💧      ║  ← PULSING RED BORDER
│ ──────────────  │   ║ ═══════════════ ║     (.alert-critical CSS)
│ Stage: Intake   │   ║ Stage: Develop  ║
│ Chalk: ○○  (0)  │   ║ MOLDING + LEAK  ║
│ Vasc:  ⚪  NO    │   ║ ⛔ ISOLATE NOW  ║
│ Day 4           │   ║ Day 22          ║
│ ✅ Normal        │   ║ 🚨 CRITICAL     ║
└─────────────────┘   └═════════════════┘
```

**Card Data Sources:**
- **Stage/Status:** `egg.current_stage`, `egg.status`
- **Chalk/Vasc/Health:** Most recent `EggObservation` row for this egg
- **Day count:** `TODAY() - bin.harvest_date`
- **Alert badges:** Computed from Guardrail Rules (see Section 7)

**Card Visual Rules:**
| Condition | Border | Badge |
|---|---|---|
| Healthy, no alerts | Default glass border | ✅ Healthy |
| Age > 10 days, chalking = 0 | Amber border | ⚠️ Check Chalking |
| Age > 15 days, no vascularity | Amber border | ⚠️ Infertility Risk |
| Molding or Leaking detected | Pulsing red border | 🚨 CRITICAL |
| Stage = Mature past max incubation | Amber border | ⚠️ Pipping Watch |
| Status = Dead | Dimmed card, unselectable | ☠️ Dead |
| Status = Hatched | Green border, unselectable | 🎉 Hatched |

**Grid Layout:**
- 2 columns on mobile (< 640px)
- 3 columns on tablet (640–1024px)
- 4 columns on desktop (> 1024px)

#### Batch Observation Panel
Appears below the grid when **≥ 1 egg is selected**:

```
┌─────────────────────────────────────────────────────────────────┐
│  📝 BATCH OBSERVATION — 3 eggs selected: E1, E2, E7           │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Chalking           Vascularity                                 │
│  ┌───────────────┐  ┌───────────────────────────────┐          │
│  │ ▼ — (skip)    │  │ ▼ — (skip) / YES ❤️ / NO ⚪   │          │
│  └───────────────┘  └───────────────────────────────┘          │
│                                                                 │
│  Health Flags (toggle ON to flag):                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ 🍄 Mold  │ │ 💧 Leak  │ │ ⚠️ Dent  │ │ 🟡 Disc. │          │
│  │ [ OFF ]  │ │ [ OFF ]  │ │ [ OFF ]  │ │ [ OFF ]  │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│                                                                 │
│  Stage Transition          Status Update                        │
│  ┌───────────────────┐     ┌──────────────────────────┐        │
│  │ ▼ — (keep current)│     │ ▼ — (keep current)       │        │
│  └───────────────────┘     └──────────────────────────┘        │
│  Options: Developing,      Options: Active, Dead, Hatched       │
│  Vascular, Mature,                                              │
│  Pipping, Hatched                                               │
│                                                                 │
│  Notes                                                          │
│  ┌─────────────────────────────────────────────────────────── │
│  │                                                             │ │
│  └─────────────────────────────────────────────────────────── │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────── │
│  │        💾 SAVE OBSERVATION FOR 3 EGGS                       │
│  └─────────────────────────────────────────────────────────── │
└─────────────────────────────────────────────────────────────────┘
```

**Field Definitions:**
| Field | Input Type | Values | Behavior |
|---|---|---|---|
| Chalking | Dropdown | `— (skip)`, `0: None`, `1: Partial`, `2: Full` | Skip = not recorded |
| Vascularity | Dropdown | `— (skip)`, `YES`, `NO` | Skip = not recorded |
| Molding | Toggle | `OFF` / `ON` | Default OFF |
| Leaking | Toggle | `OFF` / `ON` | Default OFF |
| Dented | Toggle | `OFF` / `ON` | Default OFF |
| Discolored | Toggle | `OFF` / `ON` | Default OFF |
| Stage | Dropdown | `— (keep current)`, plus all stages | If changed → also UPDATEs `egg.current_stage` |
| Status | Dropdown | `— (keep current)`, `Active`, `Dead`, `Hatched` | If changed → UPDATEs `egg.status` |
| Notes | Text area | Free text | Same note applied to all selected |

**Data Written on Save:**
For **each selected egg**, insert one row:
```sql
INSERT INTO EggObservation 
  (session_id, egg_id, observer_id, chalking, vascularity, 
   molding, leaking, dented, discolored, stage_at_observation, notes)
VALUES (...);
```
If **stage changed**, also:
```sql
UPDATE egg SET current_stage = ?, updated_by_session = ? WHERE egg_id = ?;
```
If **status changed**, also:
```sql
UPDATE egg SET status = ?, updated_by_session = ? WHERE egg_id = ?;
```
Then insert `SystemLog`: `event_type = 'OBSERVATION_BATCH'`, payload = `{egg_ids, changes}`.

#### Observation History (Per-Egg Expandable)
Each egg card, when clicked/tapped, expands to show its chronological observation timeline:
```
📋 Observation History — E1
───────────────────────────────────────────────────────
Apr 06, 2:15 PM  │ Elisa  │ Chalk: 2, Vasc: YES, Stage → Mature
Apr 03, 10:30 AM │ Kevin  │ Chalk: 1, Vasc: YES, Stage → Developing
Apr 01, 9:00 AM  │ Elisa  │ Chalk: 0, Vasc: NO, Stage: Intake (initial)
```

#### Edge Cases
| Case | Handling |
|---|---|
| Select all eggs | "☑ Select All Visible" checkbox above grid |
| Mixed stages in selection | Stage dropdown shows "— (mixed)" as default, not a specific stage |
| Observation on Dead/Hatched egg | Blocked — those cards are dimmed and checkbox is disabled |
| Single egg observation | Works identically — just select one |
| Large bin (30+ eggs) | Scroll within grid; use stage/status filter to narrow |
| Skip observation fields | `— (skip)` means that field is NULL in the inserted row (not overwriting) |

---

### W3: ENVIRONMENT TELEMETRY LOGGING

#### User Story
> _"Morning check — I need to record temp and humidity for the incubator in under 30 seconds each."_

#### UI Layout
```
┌────────────────────────────────────────────────────────────────┐
│  🌡️ ENVIRONMENT LOG                                            │
│  ──────────────────────────────────────────────────────────────│
│                                                                │
│  ┌─ QUICK LOG FORM (glass card) ────────────────────────────│
│  │  Incubator: [Internal Unit]                   │
│  │                                                            │
│  │  Temperature (°F)          Humidity (%)                    │
│  │  ┌─────────────────┐       ┌─────────────────┐            │
│  │  │  82.0            │       │  78              │            │
│  │  └─────────────────┘       └─────────────────┘            │
│  │                                                            │
│  │  ⚠️ Target for Blanding's: 80–84°F / 70–90% Humidity      │
│  │  ✅ Reading WITHIN safe range                               │
│  │                                                            │
│  │  Notes: [________________________________]                 │
│  │                                                            │
│  │  ┌────────────────────────────────────────────────────── │
│  │  │        💾 LOG ENVIRONMENT READING                      │
│  │  └────────────────────────────────────────────────────── │
│  └────────────────────────────────────────────────────────── │
│                                                                │
│  ┌─ RECENT READINGS (table) ─────────────────────────────── │
│  │  | Timestamp       | Incubator | Temp  | Humid | Observer │
│  │  |─────────────────|───────────|───────|───────|──────────│
│  │  | 04/06 08:30 AM  | INC-01    | 82.1  | 79%   | Elisa   │
│  │  | 04/06 08:30 AM  | INC-02    | 81.5  | 77%   | Elisa   │
│  │  | 04/05 04:15 PM  | INC-01    | 82.3  | 80%   | Kevin   │
│  └────────────────────────────────────────────────────────── │
└────────────────────────────────────────────────────────────────┘
```

**Field Definitions:**
| Field | Input Type | Required | Default | Validation |
|---|---|---|---|---|
| Incubator | Dropdown | ✅ | — | From `incubator` table (active) |
| Temperature | Number | ✅ | — | Range: 60–100°F |
| Humidity | Number | ✅ | — | Range: 30–100% |
| Notes | Text | ❌ | — | — |

**Real-Time Validation:**
When incubator is selected, the system:
1. Finds all bins assigned to that incubator
2. Determines the primary species in those bins
3. Looks up `species.optimal_temp_low` and `species.optimal_temp_high`
4. Displays target range and color-codes the current reading:
   - **GREEN (✅):** Within range
   - **AMBER (⚠️):** Within ±2°F of boundary
   - **RED (🚨):** Outside range

---

### W4: ADMINISTRATIVE CRUD (LOOKUP TABLES)

#### Purpose
Manage the three lookup tables that feed dropdowns across the entire application.

#### UI Pattern (Same for All Three Tables)
Each table gets an expandable section with:
1. **Data table** showing all active records
2. **Add button** → reveals inline form
3. **Edit button** → populates form with selected row
4. **Deactivate button** → soft deletes (sets `is_active = FALSE` or `is_deleted = TRUE`)

```
┌────────────────────────────────────────────────────────────────┐
│  🛠️ ADMIN REGISTRY                                             │
│  ──────────────────────────────────────────────────────────────│
│                                                                │
│  ┌─ 🐢 SPECIES ─────────────────────────────── [▼ expand] ──│
│  │  | ID      | Common Name     | Sci Name     | Temp  | Stat │
│  │  |---------|-----------------|--------------|-------|------│
│  │  | Blandings| Blanding's     | E. blandingii| 80-84 | Endg │
│  │  | Wood     | Wood Turtle    | G. insculpta | 78-82 | Thrt │
│  │                                                            │
│  │  [➕ ADD]   [✏️ EDIT SELECTED]   [🗑️ SOFT DELETE]          │
│  │                                                            │
│  │  ┌─ Form (when adding/editing) ─────────────────────────│
│  │  │  Common Name: [__________]  Scientific: [__________]  │
│  │  │  Min Days: [__]  Max Days: [__]                       │
│  │  │  Temp Low: [__]  Temp High: [__]                      │
│  │  │  Status: [▼ Common / Threatened / Endangered]          │
│  │  │  [💾 SAVE]                                             │
│  │  └──────────────────────────────────────────────────────│
│  └────────────────────────────────────────────────────────── │
│                                                                │
│  ┌─ 👤 OBSERVERS ───────────────────────────── [▼ expand] ──│
│  │  | ID    | Name            | Role      | Active           │
│  │  |-------|-----------------|-----------|------------------│
│  │  | elisa | Elisa Rodriguez | Lead      | ✅               │
│  │  | kevin | Kevin Howland   | Staff     | ✅               │
│  │                                                            │
│  │  [➕ ADD]   [✏️ EDIT]   [🗑️ DEACTIVATE]                   │
│  └────────────────────────────────────────────────────────── │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**CRUD Rules:**
| Action | Behavior | Audit |
|---|---|---|
| **Create** | Inline form, validates uniqueness | `SystemLog: CRUD_CREATE` |
| **Read** | Filtered to `is_deleted = FALSE` and `is_active = TRUE` | — |
| **Update** | Populate form → save → writes `updated_by_session` | `SystemLog: CRUD_UPDATE` |
| **Delete** | Soft delete only. `is_deleted = TRUE` or `is_active = FALSE` | `SystemLog: CRUD_DELETE` |

**Validation per table:**
| Table | Unique Constraints | Cannot Delete If |
|---|---|---|
| Species | `common_name`, `scientific_name` | Mothers reference this species |
| Observers | `display_name` | Observer is currently selected in sidebar |
| Incubators | `label` | Active bins assigned to this incubator |

---

### W5: DASHBOARD & BIOLOGICAL GUARDRAILS

#### KPI Cards (Top Row)
```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐
│ 🥚 ACTIVE    │  │ 🐣 PIPPING   │  │ 🎉 HATCHED   │  │ ☠️ LOST  │
│     47       │  │      3       │  │     12       │  │    5     │
│  specimens   │  │  imminent    │  │  this season │  │ failures │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────┘
```

| Card | Query | Accent Color |
|---|---|---|
| Active | `COUNT(egg) WHERE status = 'Active'` | Emerald |
| Pipping | `COUNT(egg) WHERE current_stage = 'Pipping'` | Amber (pulsing) |
| Hatched | `COUNT(egg) WHERE status = 'Hatched'` | Blue |
| Lost | `COUNT(egg) WHERE status = 'Dead'` | Red |

#### Charts
- **Hatch Rate by Species** — horizontal bar chart
- **Stage Distribution** — stacked bar: how many eggs at each stage
- **24-Hour Environment** — line chart of temp/humidity for the incubator with threshold bands

#### Biological Guardrail Rules Engine
These rules run on **every dashboard load** and surface alerts:

| Rule | Condition | Severity | UI |
|---|---|---|---|
| **G1: No Chalking** | Egg age > 10 days AND latest `chalking = 0` | ⚠️ Warning | Amber alert card |
| **G2: No Vascularity** | Egg age > 15 days AND latest `vascularity = FALSE` | ⚠️ Warning | Amber + "Infertility Risk" |
| **G3: Molding** | Latest observation `molding = TRUE` | 🚨 Critical | Pulsing red alert |
| **G4: Leaking** | Latest observation `leaking = TRUE` | 🚨 Critical | Pulsing red alert |
| **G5: Overdue Mature** | Stage = Mature AND age > `species.incubation_max_days` | ⚠️ Warning | Amber + "Pipping Watch" |
| **G6: Temp Out of Range** | Latest temp outside `species.optimal_temp_low/high` | 🚨 Critical | Red environment alert |
| **G7: Humidity OOR** | Latest humidity outside 70–90% | ⚠️ Warning | Amber environment alert |

---

### W6: ANALYTICS & EXPORT

#### Season Stats
| Metric | Calculation |
|---|---|
| Total Mothers | Count distinct mothers this season |
| Total Eggs | Count all eggs this season |
| Overall Hatch Rate | `hatched / (hatched + dead)` × 100 |
| Avg Incubation Period | Mean days harvest-to-hatch (hatched eggs only) |
| Endangered Species Saved | Count hatched where `vulnerability_status ≠ 'Common'` |

#### Charts
- Hatch rate over time (line)
- Stage distribution (bar)
- Failure analysis (pie: Infertile, Molding, Leaking, Unknown)

#### Export
- **CSV Download** — one-click export filtered by species, mother, date range
- Includes all egg data with latest observation values

---

## 6. CROSS-CUTTING: OBSERVER SESSION MANAGEMENT

```
App Loads → Observer Selected? 
  NO  → ⚠️ "Please Select Observer" — all writes BLOCKED (read-only mode)
  YES → Generate session_id: {observer_id}_{YYYYMMDDHHMMSS}
      → Insert SessionLog row
      → All pages enabled, every write tagged with session_id + observer_id
```

- Observer dropdown is in the **sidebar**, persists across all page navigations.
- On selection change: new `session_id` generated, new `SessionLog` row inserted.
- Every database write includes `created_by_session` or `updated_by_session`.

---

## 6.5 APPLICATION LOGGING (DIAGNOSTICS)
In addition to the database Audit Trail, the system must use Python standard `logging` for runtime diagnostics:
- **Level INFO:** App startup, successful connections, session transitions.
- **Level WARNING:** Cache clears, missing optional data, connectivity retries.
- **Level ERROR:** Database crashes, unhandled exceptions, schema mismatches.

## 7. CROSS-CUTTING: AUDIT LOGGING PATTERN

Every write operation must be wrapped in a logging helper:
```python
def logged_write(supabase, session_id, event_type, payload_dict, db_operations_fn):
    """Execute db_operations_fn and log the result to SystemLog."""
    try:
        result = db_operations_fn()
        supabase.table("SystemLog").insert({
            "session_id": session_id,
            "event_type": event_type,
            "event_message": f"{event_type} completed",
            "payload": payload_dict,
        }).execute()
        return result
    except Exception as e:
        supabase.table("SystemLog").insert({
            "session_id": session_id,
            "event_type": "ERROR",
            "event_message": str(e),
            "payload": payload_dict,
        }).execute()
        raise
```

---

## 8. CROSS-CUTTING: ERROR HANDLING

| Error Type | Behavior |
|---|---|
| **Network error** | Show retry button, preserve all form state in session |
| **Validation error** | Inline red text below the offending field, do NOT clear the form |
| **Database error** | Show user-friendly error message, log full error to `SystemLog` |
| **Duplicate key** | Show warning: "This record already exists. Use existing?" |

---

## 9. TECHNICAL STACK

- **Frontend:** Streamlit (Python) — locked in as the production framework.
- **Backend:** Supabase (PostgreSQL) with relational logic (Egg → Bin → Mother).
- **Security:** Natural Keys (Clue-Chain) + Soft Deletes for all records. No hard deletes.
- **Audit Trail:** Every write operation logged to `SystemLog` with observer, session, and timestamp.
- **Multi-User:** Multiple observers can use the system concurrently.
- **Mobile-First:** All UI must be usable on phone screens with wet, gloved hands.
- **Hosting:** Streamlit Cloud (free tier) with auto-deploy from GitHub.

### 9.1 Why Streamlit (Decision Record)
This app will be **handed off to non-technical staff** at a wildlife non-profit. Streamlit was chosen because:
1. **Lowest "bus factor" risk** — if the original developer is unavailable, any Python-literate person (biology grad student, data science intern, volunteer) can read and modify the code. React/Next.js would require a web developer.
2. **Single language** — Python for UI, database queries, and business logic. No JavaScript, no build toolchain, no JSX.
3. **Free hosting** — Streamlit Cloud auto-deploys from the GitHub repo. Non-technical staff just open a URL in their browser or phone. No server management.
4. **Minimal codebase** — ~6 Python files vs ~20+ files for a React app.
5. **All "maintenance" is in-app** — Adding observers, species, and incubators happens through the Admin CRUD pages, not by editing code.

### 9.2 Python Dependencies
```
streamlit
supabase
python-dotenv
requests
pandas
streamlit-lottie
streamlit-aggrid          # Interactive grid with checkbox multi-select for Observation page
```

- **`streamlit-aggrid`** solves the multi-select observation grid requirement (W2). It provides native checkbox selection, column sorting, and filtering within a Streamlit-compatible data grid.

### 9.3 Universal Soft-Delete Query Rule
**EVERY `SELECT` query in the application MUST include `WHERE is_deleted = FALSE`** (or `WHERE is_active = TRUE` for lookup tables). No exceptions. This applies to:
- All dropdown population queries
- All grid/table display queries
- All dashboard metric queries
- All analytics queries
- All identity check / duplicate detection queries

Failure to filter soft-deleted records will surface "ghost" data to users and corrupt analytics.

---

## 10. TARGET FILE STRUCTURE

```
turtle-db/
├── .env                              # Secrets (gitignored)
├── .streamlit/config.toml            # Streamlit config
├── app.py                            # Main entry point + navigation
├── pages/
│   ├── 1_📊_Dashboard.py             # W5: Dashboard + guardrails
│   ├── 2_🐣_New_Intake.py            # W1: Intake wizard
│   ├── 3_🔍_Observations.py          # W2: Observation logger
│   ├── 4_🌡️_Environment.py           # W3: Environment telemetry
│   ├── 5_🛠️_Admin_Registry.py        # W4: CRUD for lookups
│   └── 6_📈_Analytics.py             # W6: Season intelligence
├── utils/
│   ├── db.py                         # Supabase client + helpers
│   ├── session.py                    # Observer/session management
│   ├── logging.py                    # SystemLog wrapper
│   ├── guardrails.py                 # Biological alert rules
│   └── css.py                        # Design system CSS strings
├── supabase_db/
│   └── migrations/
│       ├── 20260405_initial_schema.sql
│       └── 20260406_schema_v2.sql    # New tables + ALTER scripts
├── requirements.txt
├── Requirements.md                   # THIS FILE
└── README.md
```

---

## 11. BUILD PHASES (Implementation Order)

The following phases are **ordered by field impact** — the workflow used most frequently is built first.

### Phase A: The Observation Engine (BUILD FIRST)
**Why first:** Staff use observations **daily**. This is where 80% of field time is spent. Delivering this first provides immediate operational value.

**Deliverables:**
1. `EggObservation` table fully operational (append-only)
2. Multi-select egg grid with bento cards showing current state
3. Batch observation panel (chalking, vascularity, health flags, stage transitions)
4. Per-egg observation history (expandable timeline)
5. Observer dropdown in sidebar with session lock (required for all writes)
6. `SystemLog` integration for observation events

### Phase B: The 4-Step Intake Wizard
**Why second:** New mothers arrive periodically (not daily), but the workflow must be rock-solid when they do.

**Deliverables:**
1. 4-step wizard with session-state navigation (Mother → Bin → Eggs → Confirm)
2. Identity check logic — detect existing mothers and offer "Use Existing" flow
3. Living mother support — add new bins to existing mother records
4. Atomic transaction with full audit logging
5. Clue Chain preview showing generated IDs before save

### Phase C: The Environment & Admin Hub
**Why third:** Supporting infrastructure that enables guardrails and lookup management.

**Deliverables:**
1. Environment Telemetry page — temp/humidity logging with species-specific validation
2. Admin Registry — full CRUD for Species, Observers, Incubators
3. Dashboard KPI cards + biological guardrail rules engine (G1–G7)
4. Analytics page with season stats and CSV export
5. `observer` and `incubator` table creation (schema migration v2)
