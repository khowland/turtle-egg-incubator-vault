# EXPERT SKILL: WISCONSIN TURTLE BIOLOGIST (INCUBATION)

This skill provides the **Biological Soul** of the Incubator Vault. Use these constants for database seeding, data validation, and AppSheet health alerts.

---

## 🐢 1. NATIVE WISCONSIN SPECIES (CORE CONSTANTS)
These are the primary assets tracked at the Wildlife In Need Center (WINC).

| Common Name | Scientific Name | Incubation Range (Days) | Optimal Temp (°F) | Vulnerability Status |
| :--- | :--- | :--- | :--- | :--- |
| **Blanding’s Turtle** | *Emydoidea blandingii* | 65–90 | 80–84 | **Endangered (WI)** |
| **Wood Turtle** | *Glyptemys insculpta* | 60–80 | 78–82 | **Threatened (WI)** |
| **Ornate Box Turtle** | *Terrapene ornata* | 60–75 | 80–85 | **Endangered (WI)** |
| **Painted Turtle** | *Chrysemys picta* | 50–80 | 75–82 | Common |
| **Snapping Turtle** | *Chelydra serpentina* | 80–90 | 75–82 | Common |
| **Grape Turtle** | *Graptemys geographica* | 55–75 | 80–83 | Common |

---

## 🥚 2. BIOLOGICAL OBSERVATION MARKERS (HEALTH)
Use these to build the **AppSheet High-Contrast Alerts**.

### **A. Chalking (0–2 Scale)**
- **0 - None:** Fresh egg, not yet established.
- **1 - Partial:** A white band appears (Sign of life/development).
- **2 - Full:** The entire egg is opaque white (Healthy development).
*   **Logic Rule:** If an egg is > 10 days old and Chalking = 0, flag for investigation.

### **B. Vascularity (TRUE/FALSE)**
- **TRUE:** Red veins visible under "Candling" (Strong health indicator).
- **FALSE:** No veins visible (Potential "Dead" or "Infertility" state if > 15 days).

### **C. Health Warnings (Critical)**
- **Molding:** Presence of fungal growth. (Needs immediate care/isolation).
- **Leaking:** Fluid escaping the shell. (High risk of failure).

---

## 🌡️ 3. INCUBATOR ENVIRONMENT (INVARIANTS)
Ensure all telemetry logs fall within these safe zones:
*   **Temperature:** 75°F to 85°F (Dependent on Sex-Determination goals).
*   **Humidity:** 70% to 90% (Critical for shell development).

### **EXPERT GUIDANCE:** 
If an egg reaches **Day 60** in the `Mature` stage, Agent Zero should ensure the AppSheet UI highlights it for **"Pipping Watch."**
