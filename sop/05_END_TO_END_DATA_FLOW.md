# 05. End-to-End Data Flow

| Stage | Input | Process | Output | Source of Truth |
| :--- | :--- | :--- | :--- | :--- |
| **1. Citizen Intake** | Case details, parcel numbers, raw files | API payload validation & project association | Canonical `Case` & `Project` DB records | PostgreSQL `projects` table |
| **2. Document OCR** | Uploaded PDF / Image | Document text extraction & metadata parsing | `BhoomiDocument` & `DocumentExtraction` | PostgreSQL `documents` table |
| **3. Mismatch Analysis**| Extracted field pairs | Field value comparison & severity calculation | `DocumentComparison` conflict record | PostgreSQL `conflicts` table |
| **4. RAG Indexing** | D1, D2, D3, D4 JSON artifacts | Chunking, deterministic ID generation, database insert | `KnowledgeChunk` records | PostgreSQL `knowledge_chunks` table |
| **5. Feature Engine** | Project & case metadata | Categorical & numeric preprocessing (zero target leakage) | Clean Feature Vector | `FeatureEngineeringService` |
| **6. D5 ML Inference** | Feature Vector | Scikit-Learn pipeline transform & calibrated predict_proba | `risk_probability` (0.0–1.0), `risk_level` | `delay-model-calibrated.joblib` |
| **7. Risk Explanation** | Risk level, case evidence, graph signals | Feature attribution & evidence linkage | `ExplanationResponse` | `ExplainabilityService` |
| **8. Procedure RAG** | Risk context & stage | Metadata-filtered RAG query on D4 chunks | `ProcedureGrounding` rules & citations | `RAGService` (Mode: `PROCEDURE_QUESTION`) |
| **9. Intervention** | Risk, bottleneck, procedure grounding | Rule evaluation & priority ranking | Prioritized `InterventionCandidate` list | `InterventionService` |
| **10. Officer Decision**| Selected intervention & reason | State machine validation (`RECOMMENDED` → `ACCEPTED`) | Updated `OfficerDecision` record | PostgreSQL `officer_decisions` table |
| **11. Action & Audit** | Approved decision | Audit log creation & status change | `DecisionAuditEvent` | PostgreSQL `audit_events` table |
| **12. Notification** | Action event & user target | Provider simulation (SMS / WhatsApp state transitions) | `Notification` record (`DELIVERED`/`READ`) | `NotificationService` |
