# 🐢 WINC Project Handover Manifest (v7.3.0)

## 1. Credentials Checklist
Transfer ownership of the following to `tech@wildlifeinneed.org`:
- [ ] **GitHub Repository**: (Transfer via Settings -> Danger Zone)
- [ ] **Supabase Project**: (Invite the new email as 'Owner')
- [ ] **Google Cloud Console**: (Enable Billing & Non-profit status)

## 2. Infrastructure Specs
- **Database**: Supabase PostgreSQL 15+ (Free Tier)
- **Application**: Google Cloud Run (Containerized Streamlit)
- **Heartbeat**: Google Cloud Function (Daily Ping via Cloud Scheduler)

## 3. Production Initialization (The "Clean Slate")
1. Connect to the NEW Supabase project.
2. Run `v7_3_0_FULL_SCHEMA.sql`.
3. Seed the `observer` table with the official Staff Registry in the Settings screen.

## 4. Maintenance & "Stay-Alive"
**The 7-Day Rule**: Supabase pauses projects after 7 days of inactivity.
- **Automated Solution**: The "Heartbeat" script must run daily.
- **Manual Restore**: If the heart stops, a Staff Member must log into `database.supabase.com` and click "Resume Project".

## 5. Security Protocol
- **Service Role Keys**: These keys are "Master Keys." They must NEVER be shared in emails or commit logs. They belong exclusively in the Google Secret Manager.
- **Mid-Season Lock**: Remind Staff that the Registry is immutable while eggs are active to ensure research integrity.

---
*Signed, Antigravity (Sovereign Sprint Agent)*
