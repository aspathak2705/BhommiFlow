# End-to-End Connectivity Report

```
CITIZEN INTAKE
  ↓ [POST /api/v1/projects]
CANONICAL PROJECT & CASE CREATED
  ↓ [POST /api/v1/projects/{id}/documents]
DOCUMENT OCR & EXTRACTION (D2)
  ↓ [POST /api/v1/rag/query]
EVIDENCE RAG INDEXING (D1 + D2 + D3)
  ↓ [GET /api/v1/projects/{id}/conflicts]
MISMATCH & DISCREPANCY DETECTION (D3)
  ↓ [GET /api/v1/projects/{id}/graph]
GRAPH & BOTTLENECK EVALUATION
  ↓ [POST /api/v1/projects/{id}/predict]
D5 CALIBRATED ML DELAY PREDICTION (Risk Prob & Level)
  ↓ [GET /api/v1/projects/{id}/explanation]
EVIDENCE-BACKED RISK EXPLANATION
  ↓ [POST /api/v1/rag/query (Mode: PROCEDURE_QUESTION)]
D4 PROCEDURE RAG GUIDANCE RETRIEVAL
  ↓ [GET /api/v1/projects/{id}/interventions]
INTERVENTION CANDIDATE RANKING
  ↓ [POST /api/v1/decisions]
OFFICER DECISION WORKFLOW (Human-in-the-Loop)
  ↓ [POST /api/v1/decisions/{id}/action]
ACTION INITIATION & REALTIME NOTIFICATION SIMULATION
  ↓ [GET /api/v1/projects/{id}/audit-trail]
IMMUTABLE AUDIT TRAIL RECORDING
```

## Bidirectional Flow Validation
1. **Citizen → Officer**: Citizen case submission & uploaded document records automatically generate relational DB rows and vector chunks accessible on the officer dashboard.
2. **Officer → Citizen**: Officer decision state updates (`ACTION_INITIATED`) automatically trigger simulated SMS/WhatsApp notifications and update citizen-facing status trackers.
