# 🐢 WINC Incubator Vault: Operator's Manual (v7.4.0)
Welcome to the Incubator Vault. This guide will help you use the app to track our turtle eggs from intake to hatching.

## 1. Getting Started (Clocking In)
1. **Launch the App**: Open the link on your tablet or computer.
2. **Identify Yourself**: Select your name from the dropdown list on the first screen. The app will remember who you are for the rest of your shift.
3. **Automatic Session Recovery**: If your browser crashes or you accidentally close the tab, don't worry! If you log back in within **4 hours**, the system will automatically recognize your shift and resume your session exactly where you left off, ensuring your signatures and audit history stay perfectly aligned.

## 2. The Daily Protocol (The "Weight-First" Rule)
Every day, we check the health of our turtle bins.
1. **Go to Observations**: Click "Observations" in the sidebar.
2. **Load Your Workbench**: Search for Bins or Cases you've pulled for testing and "Pin" them to your session.
3. **Check Your Progress Icons**:
    - `🟢` **Done**: All eggs in this bin have been checked today.
    - `🌓` **Partial**: Some eggs are done, but others are pending.
    - `⚪` **New**: No eggs have been checked yet this shift.
4. **The Weight-First Rule**: You must weigh the bin to unlock the egg grid. The app will calculate exactly how much water (ml) to add. 
5. **Batch Recording**: Tap the eggs in the grid that look the same. Check the **CSV Selection Bar** (e.g., `E1, E3, E7`) to confirm your selection, then set the Stage/Chalking and hit **Confirm & Save**.
6. **Supplemental Tools**: Use the sidebar to add extra bins to a case or add straggler eggs to an existing bin.

## 3. New Intake (Adding a Mother & Her Eggs)
When a mother turtle arrives, use the **single-page** Intake screen to record everything at once.

### Step A: The Clinical Origin
1. **Species Choice**: Select the turtle species from the list. It shows both the 2-letter code and the name (e.g., `BL - Blanding's`).
2. **WormD Case #**: Enter the official case number from the intake records.
3. **Finder/Turtle Name**: Enter the last name of the finder (this is used to create our unique Bin Codes).

### Step B: The Bin Setup (Dynamic Table)
Below the origin info, you will see the **Bin Setup** table.
1. **Automatic Codes**: The "Bin Code" is generated for you (e.g., `BL1-Smith-1`). This is what you should write on the physical bin label. *Note: The Bin Code will dynamically update in real-time as you change the Species or type the Finder's Name.*
2. **Multiple Bins**: If a turtle has so many eggs they won't fit in one bin, click the **"➕ Add Bin"** button. You can have up to 9 bins for one mother.
3. **Egg Counts**: Enter the exact number of eggs in each physical bin. You must tap inside the box and type the number (1-99) directly using your keyboard. There are no up/down arrows.
4. **Deleting Bins**: If you click the trash icon (🗑️), the other bins will automatically "re-number" themselves to stay in order.

## 4. The Daily Loop (Checking Eggs)
*Note: When you finalize a New Intake, the system will now automatically transition you to this Observation Screen, mapping your newly created first Bin for immediate verification.*

When checking eggs dynamically during the day:
1. **Hydration Check:** Enter current Bin Weight. The system will suggest exactly how much water to add.
2. **Top-Level Tracking:** A single progress bar above the egg grid guarantees you visually verify all eggs. Do not rely on individual egg colors, as color codes are explicitly reserved for severe Health Warnings (like Molding/Leaking). 
3. **Data Logging:** Select multiple eggs to apply the exact same observation properties (Stage, Chalking) at once. Historical traits will appear as highly condensed code strings (e.g., `[D4: S1-C0]`) so you don't scroll infinitely.
4. **Final Confirmation:** The summary page will always list eggs numerically. Please physically check this numerical list against your physical egg matrix before finalizing to avoid cross-contamination of biological traits.

## 5. What if an Egg Hatches? (The Neonate Pivot)
Our system uses automated transitions to handle hatched eggs.
1. **Change the Stage to S6**: Do not worry about manually changing statuses. Simply multi-select the hatching eggs and change their **Stage** to `S6`.
2. **Automated Transfer**: The system will warn you that the Neonate Pivot is triggering. Once you hit Save, the egg is locked out of the incubator grid and automatically marked as `Transferred`.
3. **The Ledger**: The system silently moves the turtle into the `Hatchling_Ledger` database, carrying the original Mother's ID with it.

## 6. Dashboards & Analytics
You are not just logging data; you can visualize it in real-time.
- **The Command Center (Dashboard)**: Click `Dashboard` to see live KPIs (Active Subjects vs Hatched) and the Mortality Heatmap, which automatically highlights which biological stage is suffering the most losses.
- **The Reports Hub**: Click `Reports` to use the **Expert Filter Carpentry**. On the left sidebar, you can filter the entire clinical history by specific Date Windows or Species (e.g., viewing trends exclusively for Blanding's Turtles). 

## 7. Pro-Tips for Success
- **In-App Help**: If you ever forget how a specific screen works, look for the **ℹ️ Screen Help** expander on the sidebar. It contains a rapid, step-by-step guide tailored specifically for that exact screen.
- **Look for the 🔒**: If you see a lock in Settings, it means we have active eggs. You cannot change biological lists (like species names) until the season is over.
- **Font Size**: If you are using a tablet in the field and the text is too small, go to **Settings** and use the **"Global Font Scale"** slider on the sidebar to make it bigger.
