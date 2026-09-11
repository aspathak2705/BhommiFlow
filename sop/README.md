# BhoomiSakha SOP Directory

Predictive analytics and decision intelligence system for early detection of land acquisition delays.

## Core Pipeline Architecture

```
Case
 → Evidence (D1/D2/D3)
 → Parcel
 → Timeline
 → Graph & Bottlenecks
 → Feature Engine
 → D5 Delay Model (Prediction: Probability & Level)
 → Explainability (Contributing Factors & Supporting Evidence)
 → D4 Procedure RAG (Grounded Government Rules)
 → Intervention Recommendation
 → Officer Decision (Human-in-the-loop)
 → Action
 → Realtime Notification Simulation (SMS & WhatsApp)
 → Immutable Audit Trail
```

## Data Architecture
* **D1 (Case Data) + D2 (Document Data) + D3 (Comparison/Conflict Data)**: Ingested into **Evidence RAG** for structured context retrieval, OCR analysis, and document mismatch detection.
* **D4 (Procedure Knowledge)**: Ingested into **Procedure RAG** for grounding interventions in actual government regulations.
* **D5 (Prediction Model)**: Trained Scikit-Learn Calibrated Classifier (`delay-model-calibrated.joblib` + `preprocessor.joblib`). **D5 is NOT RAG.**

---

## SOP Master Document Map

1. **[01_DEMO_MASTER_RUNBOOK.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/01_DEMO_MASTER_RUNBOOK.md)**: Click-by-click live demonstration guide across all 11 UI screens.
2. **[02_5_MINUTE_DEMO_SCRIPT.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/02_5_MINUTE_DEMO_SCRIPT.md)**: Word-for-word 5-minute presentation script timed to exact demo moments.
3. **[03_DEMO_DATA_AND_CASES.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/03_DEMO_DATA_AND_CASES.md)**: Primary (`PRJ-TEST-INTEG-001`) and backup deterministic demo data fixtures.
4. **[04_SYSTEM_ARCHITECTURE.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/04_SYSTEM_ARCHITECTURE.md)**: Complete 4-plane technical architecture specifications (Experience, Evidence, Intelligence, Decision).
5. **[05_END_TO_END_DATA_FLOW.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/05_END_TO_END_DATA_FLOW.md)**: Exact data transformation flow from citizen submission to immutable audit logging.
6. **[06_FEATURE_TO_JUDGE_MATRIX.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/06_FEATURE_TO_JUDGE_MATRIX.md)**: 100-mark SIH evaluation criteria mapping with application proof points.
7. **[07_API_TESTING_SOP.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/07_API_TESTING_SOP.md)**: Comprehensive FastAPI endpoint testing procedures and schemas.
8. **[08_SECURITY_TESTING_SOP.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/08_SECURITY_TESTING_SOP.md)**: RBAC, IDOR, SQLi, XSS, and project isolation security test protocols.
9. **[09_NOTIFICATION_SIMULATION_SOP.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/09_NOTIFICATION_SIMULATION_SOP.md)**: High-fidelity SMS & WhatsApp delivery simulation specifications.
10. **[10_D5_MODEL_SOP.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/10_D5_MODEL_SOP.md)**: Dataset 5 calibrated ML model loading, feature schemas, zero leakage policy, and metrics.
11. **[11_RAG_EVIDENCE_SOP.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/11_RAG_EVIDENCE_SOP.md)**: Unified Evidence RAG and D4 Procedure RAG retrieval modes and metadata filtering.
12. **[12_OFFICER_WORKFLOW_SOP.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/12_OFFICER_WORKFLOW_SOP.md)**: Officer decision lifecycle, state transitions, intervention options, and governance.
13. **[13_TROUBLESHOOTING_AND_RECOVERY.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/13_TROUBLESHOOTING_AND_RECOVERY.md)**: System diagnostic procedures and issue fixes for all failure modes.
14. **[14_DEMO_DAY_CHECKLIST.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/14_DEMO_DAY_CHECKLIST.md)**: Operational T-24h to T-1m readiness and environment verification steps.
15. **[15_JUDGE_QA_MASTER.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/15_JUDGE_QA_MASTER.md)**: Defensible technical answers to 40 probable judge questions.
16. **[16_PITCH_MASTER_SCRIPT.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/16_PITCH_MASTER_SCRIPT.md)**: Timed pitches (30s, 60s, 3m, 5m) focusing on evidence connection and delay prevention.
17. **[17_TECHNICAL_DEEP_DIVE.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/17_TECHNICAL_DEEP_DIVE.md)**: Deep technical breakdown of graph intelligence, vector search, calibration, and RBAC.
18. **[18_DATA_PROVENANCE_AND_TRUST.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/18_DATA_PROVENANCE_AND_TRUST.md)**: Data origin tracking, source hierarchy, and synthetic benchmark integrity rules.
19. **[19_DEMO_FAILURE_RECOVERY.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/19_DEMO_FAILURE_RECOVERY.md)**: Emergency live demo contingency plans during technical glitches.
20. **[20_FINAL_SYSTEM_STATUS.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/20_FINAL_SYSTEM_STATUS.md)**: Complete system readiness status matrix across all modules.
