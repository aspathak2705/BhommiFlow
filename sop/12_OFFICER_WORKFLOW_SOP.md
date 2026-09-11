# 12. Officer Workflow SOP

## Officer Decision Lifecycle

BhoomiSakha strictly enforces human-in-the-loop governance. The AI system recommends interventions; the nodal officer retains final decision authority.

```
RECOMMENDED
    ↓
REVIEWED
    ↓
ACCEPTED / REJECTED / DEFERRED
    ↓
ACTION_INITIATED
    ↓
AWAITING_OUTCOME / RESOLVED
```

### Action Initiation Procedure
1. **Review Decision Context**: Officer views predicted risk probability, evidence citations, document mismatches, and procedure grounding.
2. **Select Decision State**:
   * **ACCEPT**: Officer approves recommended intervention.
   * **REJECT**: Officer overrides AI recommendation with mandatory written justification.
   * **DEFER**: Decision postponed pending missing evidence.
3. **Trigger Action**: System logs decision event, updates status to `ACTION_INITIATED`, and triggers realtime notification simulation.
4. **Audit Trail**: Action is recorded in `DecisionAuditEvent` with actor ID, timestamp, and previous/new states.
