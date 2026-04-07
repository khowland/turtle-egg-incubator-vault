# WINC Incubator Vault - Requirements & Specifications
Version: 6.3.7 - Enterprise Edition
Lead Biologist: Elisa Fosco

## 1. Session Architecture
- **Session Gate:** Splash screen forcing identity selection before app access.
- **Persistence:** Observer identity sticks for the duration of the browser session.
- **Environment Gate:** Observations require a mandatory Temp/Humidity sync once per session.

## 2. Field Operations
- **New Intake Wizard (4-Step):**
  - Step 1: Mother Identity (Species, Name, Condition).
  - Step 2: Bin Setup (Substrate, Bin Label).
  - Step 3: Egg Quantity (The 'Burst' Entry).
  - Step 4: Biological Review & Atomic Commit.
- **Observation Engine:**
  - Integrated Environment Gate.
  - Multi-select egg grid for batch health logging.

## 3. Technical Stack
- Backend: Supabase (PostgreSQL + Management API).
- Frontend: Streamlit (v1.31+ Navigation API).
- Charts: Plotly Express.
=============================================================================
