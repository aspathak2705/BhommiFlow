# 06. Feature to Judge Matrix

## SIH Evaluation Criteria Mapping (100 Marks Total)

### 1. Prototype Demo / Working Solution (50 Marks)
* **Core Functionality & Working Features (15 Marks)**:
  * *Demonstrated via*: Full citizen intake, document extraction, evidence graph, D5 prediction, risk explanation, D4 procedure retrieval, officer decision, and notification simulation.
* **Live Demonstration & Stability (10 Marks)**:
  * *Demonstrated via*: Zero background jobs/timers, clean single-threaded deterministic DB queries, 100% test pass rate (`tests/test_final_integration.py`).
* **Feature Completeness (10 Marks)**:
  * *Demonstrated via*: End-to-end flow connecting Citizen Intake → Evidence Intelligence → Delay Model → Human Decision → Citizen Notification.
* **Accuracy / Effectiveness (5 Marks)**:
  * *Demonstrated via*: Dataset 5 held-out test ROC-AUC = `0.6905`, Brier Score = `0.2223`, calibrated risk probabilities.
* **Technology Integration (5 Marks)**:
  * *Demonstrated via*: FastAPI, React, PostgreSQL/PostGIS, Scikit-learn, Vector RAG.
* **UX / Usability (5 Marks)**:
  * *Demonstrated via*: Clear dashboard indicators, evidence breadcrumbs, "Why Risky?" drawer, one-click officer intervention approval.

### 2. Novelty & Innovation (10 Marks)
* **Key Innovation**: Moving from reactive document digitization to proactive delay prediction, unifying multi-source evidence (D1-D3) with legal procedure grounding (D4) and human-in-the-loop governance.

### 3. Design & Architecture (10 Marks)
* **Key Strengths**: Strict 4-plane separation (Experience, Evidence, Intelligence, Decision), project-isolated vector RAG, zero target leakage in ML pipelines.

### 4. Technical Skill & Depth (10 Marks)
* **Key Capabilities**: Calibrated Scikit-Learn pipelines, SQL-level vector filters, state machine decision transitions, high-fidelity offline notification simulation.

### 5. Pitching & Presentation (10 Marks)
* **Key Structure**: 5-minute timed script focusing on problem, evidence connection, early risk detection, procedure grounding, and auditable action.

### 6. Q&A Handling (10 Marks)
* **Key Resource**: Master Q&A document covering 40 technical, architectural, and security questions.
