PROJECT: TurtleEggDB (AppSheet/Mobile-First)
VERSION: 2.0 (Relational Pivot)
TARGET: AppSheet Native Mobile (iOS/Android)
[St] STORAGE: THE DATA VAULT (GOOGLE SHEETS)
ROOT: C:\Users\Kevin\TurtleEggDB

Persona: You are an expert Turtle Biologist in Wisconsin.
You run an egg harvesting program, by harvesting eggs from 
dead or injured mother turtles brought into Wildlife in Need Center (WINC)
and incubating them. Your goal is to track observations of the eggs 
on a very regular basis to asses the success of the program and provide biological analytics.
You will help fine tune these requirements from your perspective. If any specs look
like they might not work, or specs are missing, it's your job to speak up.
You will analyze these specs critically and offer ways to improve them, 
and be the advisor on developing this system innterface for use at the incubator during observations, 
most likely on a mobile phone, android or apple.

DB: Supabase. Need an auto unpause for Supabase if it has paused after 7 days of no use.
The "Auto-Unpause" UI Logic
The project may go dormant after 7 days or over the winter.
Include CheckDB code in the [Ac] Actuator layer (the Next.js frontend).
When the UI is engaged:
	- Check Health: The app sends a heartbeat request.
	- Handle 503/Timeout: If the DB is paused, Supabase returns a specific error or the connection times out.
	- Trigger Wake: You can use the Supabase Management API to programmatically "unpause" the project.
	- Loading State: The UI shows a "Waking up the Incubator Vault..." spinner for about 30–60 seconds.

SessionID
On opening the app at opening page, it will generate a sessionID derived from DateTime and the selected User.
This will be used to tag inserts, updates, and soft deletes in the system, as well as relating IncubatorObservations to EggObservations.

Logging
The system should also probably have a simple multi purpose log that can track different events, at least when a new user session is initiated, errors,etc.

Volume of data. 
This app is used during turtle breeding season.
The most number of eggs that have been in the incubatorat at one time, 
across many bins and from many mother turtles was 276 last year, on a single day. 
Not all eggs get a daily observation, but most do. If an egg shows no change from last observation, no observation is made.
In general observations are done every 3 days. 

Exports
The system should allow for export to google sheets (1 tab per table), or CSV. If other options for export are available, suggest.
Linking to google sheets would be ideal, but I don't want to over complicate the project. 

Reports and Analytics
This area to be filled out by TYurtle Expert

DB Schema (draft)
/* SECTION 1: SESSION & AUDIT INFRASTRUCTURE */

CREATE TABLE SessionLog (
    session_id TEXT PRIMARY KEY, /* [UserShortName]_[YYYYMMDDHHMMSS] */
    user_name TEXT NOT NULL,
    login_timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_agent TEXT
);

CREATE TABLE SystemLog (
    log_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id TEXT REFERENCES SessionLog(session_id),
    event_type TEXT NOT NULL, /* SESSION_START, ERROR, TRACE, AUTH, DELETE */
    event_message TEXT,
    payload JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

/* SECTION 2: BIOLOGICAL ASSETS */

CREATE TABLE mother (
    mother_id TEXT PRIMARY KEY, /* [MotherName]_[Species]_[YYYYMMDD] */
    mother_name TEXT NOT NULL,
    species TEXT NOT NULL,
    intake_date DATE NOT NULL,
    condition TEXT,
    notes TEXT,
    created_by_session TEXT REFERENCES SessionLog(session_id),
    updated_by_session TEXT REFERENCES SessionLog(session_id),
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_by_session TEXT REFERENCES SessionLog(session_id)
);

CREATE TABLE bin (
    bin_id TEXT PRIMARY KEY, /* [MotherID]_B[Number] */
    mother_id TEXT REFERENCES mother(mother_id),
    harvest_date DATE NOT NULL,
    total_eggs INTEGER CHECK (total_eggs <= 276),
    created_by_session TEXT REFERENCES SessionLog(session_id),
    updated_by_session TEXT REFERENCES SessionLog(session_id),
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_by_session TEXT REFERENCES SessionLog(session_id)
);

CREATE TABLE egg (
    egg_id TEXT PRIMARY KEY, /* [BinID]_E[Number] */
    bin_id TEXT REFERENCES bin(bin_id),
    physical_mark INTEGER,
    current_stage TEXT DEFAULT 'Intake', /* Intake, Developing, Established, Mature, Pipping, Hatched */
    status TEXT DEFAULT 'Active', /* Active, Dead, Hatched */
    created_by_session TEXT REFERENCES SessionLog(session_id),
    updated_by_session TEXT REFERENCES SessionLog(session_id),
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_by_session TEXT REFERENCES SessionLog(session_id)
);

/* SECTION 3: TELEMETRY & OBSERVATION (HEADER-DETAIL) */

CREATE TABLE IncubatorObservation (
    obs_id TEXT PRIMARY KEY, /* [SessionID]_ENV_[HHMMSS] */
    session_id TEXT REFERENCES SessionLog(session_id),
    bin_id TEXT REFERENCES bin(bin_id), /* Contextual link to specific bin being checked */
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    observer_name TEXT NOT NULL,
    ambient_temp NUMERIC,
    humidity NUMERIC,
    notes TEXT,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_by_session TEXT REFERENCES SessionLog(session_id)
);

CREATE TABLE EggObservation (
    detail_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id TEXT REFERENCES SessionLog(session_id),
    egg_id TEXT REFERENCES egg(egg_id),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    vascularity BOOLEAN,
    chalking INTEGER CHECK (chalking BETWEEN 0 AND 2),
    molding BOOLEAN,
    leaking BOOLEAN,
    notes TEXT,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_by_session TEXT REFERENCES SessionLog(session_id)
);




[Lo] LOGIC: BIOLOGICAL & SESSION INVARIANTS
CLUE CHAIN INTEGRITY: Mandatory natural keys for all records. No abstract UUIDs.
ACCOUNTABILITY HOOK: Top-of-page dropdown "Observations made by [StaffName]".
SESSION PERSISTENCE: Use USERSETTINGS in AppSheet to locally cache the Observer Name.
BIOLOGICAL LADDER: Intake -> Developing -> Established -> Mature -> Pipping -> Hatched.
[Ac] ACTUATOR: MOBILE FIELD UI (APPSHEET)
VERTICAL ORIENTATION: Single-column layouts optimized for field entry.
THE BINGO LIST: Inline View of the Egg table on the Bin Detail screen.
QUICK EDIT TOGGLES: Enable Quick Edit for Vascularity, Molding, and Stage columns.
OFFLINE SYNC: Mandatory native offline capability for incubator room dead-zones.
HANDOVER: UI labels in plain, non-technical English for staff/volunteers.
[T] TRANSFORMER: THE BURST INTAKE SCRIPT
Eggs must be able to be entered in batches, or individually. Observations against the eggs in a bin should allow for multi select of the eggs assigned to that bin for bulk observation
KEY GENERATION: Automatic concatenation of Clue Chain sequence to prevent user error.

Anticpated Workflow
Intake:
New Mother =  Mother Turtle , Bin, n number of eggs (user defined), and initial observations.
Existing Mother, New Eggs: Choose a mother, and then choose existing bin, or new bin, and add 1-n eggs 
These egg rows and observation rows will then be auto populated and related appropriately.
Every new egg will have at least one related observation row

Observation:
Choose a bin (Bin numbers have mother turtle name as part of key, so it's easy)
The eggs that exist for that bin will be available for multi selection. 
User can select 1 or multiple discreet eggs to make an observation.
Enter Observations for the selected egg(s)