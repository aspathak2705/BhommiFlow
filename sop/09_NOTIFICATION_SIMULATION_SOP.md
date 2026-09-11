# 09. Notification Simulation SOP

## High-Fidelity Notification Simulation

To ensure 100% demo stability without internet connectivity or external API credentials, BhoomiSakha includes a provider-independent notification simulation.

### Architecture
```
Officer Action
 → NotificationService
 → In-Memory Event Dispatch
 → Simulated Status Transitions
 → UI State Update
```

### Channel State Machines

#### 1. SMS Simulation
* **ID Format**: `SIM-SMS-YYYYMMDD-XXXXX`
* **Lifecycle**: `QUEUED` → `SENT` → `DELIVERED`
* **Status Details**: Marked with `[DEMO SIMULATION]`.

#### 2. WhatsApp Simulation
* **ID Format**: `SIM-WA-YYYYMMDD-XXXXX`
* **Lifecycle**: `QUEUED` → `SENT` → `DELIVERED` → `READ`
* **Status Details**: Full read timestamp generation with UI badge `[DEMO SIMULATION]`.

### Supported Demo Events
1. `CASE_SUBMITTED`: Citizen submits new acquisition case.
2. `EVIDENCE_REQUESTED`: Officer requests additional documents.
3. `ACTION_INITIATED`: Officer approves recommended intervention.
4. `RISK_ESCALATED`: Project risk level transitions to `HIGH` or `CRITICAL`.
5. `CASE_RESOLVED`: Land dispute resolved.
