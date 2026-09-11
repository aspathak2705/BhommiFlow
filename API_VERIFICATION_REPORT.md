# API Verification Report

| # | Method | Endpoint | Backend Router | Service | DB/RAG/ML | Frontend Caller | Test Status | Status |
|---|--------|----------|----------------|---------|-----------|-----------------|-------------|--------|
| 1 | POST | `/api/v1/auth/login` | `auth.py` | `auth_service` | PostgreSQL `users` | `LoginPage.tsx` | PASS | CONNECTED |
| 2 | POST | `/api/v1/projects` | `projects.py` | `project_service` | PostgreSQL `projects` | `CreateProjectModal.tsx` | PASS | CONNECTED |
| 3 | GET | `/api/v1/projects` | `projects.py` | `project_service` | PostgreSQL `projects` | `Dashboard.tsx` | PASS | CONNECTED |
| 4 | GET | `/api/v1/projects/{id}` | `projects.py` | `project_service` | PostgreSQL `projects` | `ProjectDetail.tsx` | PASS | CONNECTED |
| 5 | POST | `/api/v1/projects/{id}/parcels` | `projects.py` | `project_service` | PostgreSQL `parcels` | `AddParcelModal.tsx` | PASS | CONNECTED |
| 6 | GET | `/api/v1/projects/{id}/documents` | `evidence_intelligence.py` | `evidence_intelligence_service` | PostgreSQL `documents` | `DocumentList.tsx` | PASS | CONNECTED |
| 7 | POST | `/api/v1/projects/{id}/documents` | `evidence_intelligence.py` | `evidence_intelligence_service` | PostgreSQL `documents` | `UploadDocument.tsx` | PASS | CONNECTED |
| 8 | GET | `/api/v1/projects/{id}/conflicts` | `evidence_intelligence.py` | `evidence_intelligence_service` | PostgreSQL `conflicts` | `ConflictViewer.tsx` | PASS | CONNECTED |
| 9 | POST | `/api/v1/rag/query` | `guidance.py` | `RAGService` | PostgreSQL `knowledge_chunks` (D1-D4) | `GuidanceDrawer.tsx` | PASS | CONNECTED |
| 10 | POST | `/api/v1/projects/{id}/predict` | `prediction.py` | `DelayPredictionService` | Scikit-Learn Calibrated Model (D5) | `RiskCard.tsx` | PASS | CONNECTED |
| 11 | GET | `/api/v1/projects/{id}/prediction` | `prediction.py` | `DelayPredictionService` | PostgreSQL `project_predictions` | `Dashboard.tsx` | PASS | CONNECTED |
| 12 | GET | `/api/v1/projects/{id}/explanation` | `explainability.py` | `ExplainabilityService` | RAG + Feature Attributions | `WhyRiskyDrawer.tsx` | PASS | CONNECTED |
| 13 | GET | `/api/v1/projects/{id}/interventions` | `explainability.py` | `InterventionService` | D4 Procedure + Decision Rules | `InterventionPanel.tsx` | PASS | CONNECTED |
| 14 | GET | `/api/v1/projects/{id}/decision-context` | `decision_intelligence.py` | `DecisionIntelligenceService` | Aggregated Context Package | `DecisionWorkspace.tsx` | PASS | CONNECTED |
| 15 | POST | `/api/v1/decisions` | `decision_intelligence.py` | `DecisionIntelligenceService` | PostgreSQL `officer_decisions` | `DecisionActionModal.tsx` | PASS | CONNECTED |
| 16 | POST | `/api/v1/decisions/{id}/action` | `decision_intelligence.py` | `DecisionIntelligenceService` | PostgreSQL + Notification Sim | `DecisionActionModal.tsx` | PASS | CONNECTED |
| 17 | GET | `/api/v1/projects/{id}/audit-trail` | `decision_intelligence.py` | `DecisionIntelligenceService` | PostgreSQL `audit_events` | `AuditTrail.tsx` | PASS | CONNECTED |

## Verification Summary
* Total Endpoints Evaluated: 17
* Pass Rate: 100% (17 / 17)
* Target Leakage Protection: Verified (0 outcome features passed to preprocessor)
* Case Isolation: Verified (`WHERE project_id = :project_id` filter active)
