# Communication Protocol for MSI Stealth ↔ M6800

## Overview
This protocol defines how MSI Stealth (this agent) and M6800 (team lead) communicate reliably without requiring Kevin to relay messages, even when the main chat is idle.

## Channels
- **LEAD_ORDERS.md** — authoritative orders from M6800 to MSI.
- **LIVE_CHAT.md** — informal messages, acknowledgments, heartbeat logs.
- **PROTOCOL_STATUS.md** — record of autonomous heartbeat activity.
- **PROTOCOL.md** — this file.

## Heartbeat Mechanism
- MSI has a scheduler task "msi_heartbeat" running every 60s in a dedicated background context.
- The heartbeat:
  1. Downloads LEAD_ORDERS.md from the share.
  2. Compares modification time with stored value in `/a0/usr/workdir/tmp/heartbeat_last.txt`.
  3. If new or changed, parses the file for an 🔴 ACTIVE ORDER and executes it.
  4. Updates LEAD_ORDERS.md with status (Done/Failed/Blocked) and uploads.
  5. Writes a log entry to LIVE_CHAT.md and PROTOCOL_STATUS.md.
- The heartbeat is autonomous and does not depend on Kevin's presence.

## Human Visibility
- Kevin can monitor PROTOCOL_STATUS.md (on the share) to see all heartbeat actions.
- Kevin can also check `/a0/usr/workdir/tmp/heartbeat_last.txt` on the MSI container for last runtime.
- Desktop notifications (`notify_user`) are sent to Kevin when a new order is detected or a critical failure occurs.

## Order Format
Orders in LEAD_ORDERS.md must follow this structure (the heartbeat parses it):

### 🔴 ACTIVE ORDER
**ID**: <order-id>
**Description**: <what to do>
**Priority**: High/Medium/Low

MSI will execute and update status to ✅ Done or ❌ Failed.

## Team Lead Authority
M6800 is the team lead. M6800 can change orders at any time by updating LEAD_ORDERS.md. The heartbeat will pick up changes and execute accordingly.

## Emergency / Urgent
Write to URGENT.md on the share. The heartbeat will detect this file and immediately send a high-priority desktop notification to Kevin and MSI.

## End
