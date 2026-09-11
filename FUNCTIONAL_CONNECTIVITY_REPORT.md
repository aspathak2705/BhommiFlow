# Functional Connectivity Report

| User Action | UI Component | API Endpoint | Service Layer | Data Source | UI Update | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Citizen Case Intake** | `CreateProjectModal.tsx` | `POST /api/v1/projects` | `project_service` | PostgreSQL `projects` | Appends new project card | **PASS** |
| **Document Upload & OCR**| `UploadDocument.tsx` | `POST /api/v1/projects/{id}/documents` | `evidence_intelligence_service` | PostgreSQL `documents` | Renders extracted metadata & status | **PASS** |
| **Conflict Mismatch View**| `ConflictViewer.tsx` | `GET /api/v1/projects/{id}/conflicts` | `evidence_intelligence_service` | PostgreSQL `conflicts` (D3) | Shows Document A vs B comparison | **PASS** |
| **D5 Delay Risk Check** | `RiskCard.tsx` | `POST /api/v1/projects/{id}/predict` | `DelayPredictionService` | D5 Machine Learning Model | Displays Risk Probability & Level | **PASS** |
| **"Why Risky?" Explanation**| `WhyRiskyDrawer.tsx` | `GET /api/v1/projects/{id}/explanation` | `ExplainabilityService` | Evidence + Graph Attributions | Renders evidence-backed factors | **PASS** |
| **D4 Procedure Retrieval** | `GuidanceDrawer.tsx` | `POST /api/v1/rag/query` | `RAGService` | PostgreSQL `knowledge_chunks` (D4) | Renders grounded RFCTLARR rules | **PASS** |
| **Intervention View** | `InterventionPanel.tsx` | `GET /api/v1/projects/{id}/interventions` | `InterventionService` | Rules Engine + D4 Guidance | Displays ranked officer actions | **PASS** |
| **Officer Action Approval**| `DecisionActionModal.tsx`| `POST /api/v1/decisions/{id}/action` | `DecisionIntelligenceService` | PostgreSQL `officer_decisions` | Transitions state & fires sim | **PASS** |
| **Notification Simulation**| `NotificationCenter.tsx`| Internal Service Dispatch | `NotificationService` | In-memory / PostgreSQL DB | Updates SMS & WhatsApp status | **PASS** |
| **Audit Log Display** | `AuditTrail.tsx` | `GET /api/v1/projects/{id}/audit-trail` | `DecisionIntelligenceService` | PostgreSQL `audit_events` | Renders immutable audit trail | **PASS** |

## Verification Conclusion
All 10 core user flows execute seamlessly from UI triggering to backend processing and state persistence.
