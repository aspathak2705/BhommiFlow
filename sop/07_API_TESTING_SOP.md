# 07. API Testing SOP

## Core API Route Registry

### Phase 1: Projects & Parcels
* `POST /api/v1/projects`: Create land acquisition project.
* `GET /api/v1/projects`: List and filter projects.
* `GET /api/v1/projects/{project_id}`: Retrieve project details.
* `POST /api/v1/projects/{project_id}/parcels`: Attach land parcel to project.

### Phase 2: Evidence Intelligence
* `POST /api/v1/projects/{project_id}/documents`: Upload document record.
* `GET /api/v1/documents/{document_id}`: Retrieve document metadata and extractions.
* `GET /api/v1/projects/{project_id}/conflicts`: List detected document mismatches/conflicts.

### Phase 3: RAG Retrieval
* `POST /api/v1/rag/query`: Execute logical RAG query.
  * **Modes**: `CASE_INVESTIGATION`, `DOCUMENT_INVESTIGATION`, `CONFLICT_INVESTIGATION`, `PROCEDURE_QUESTION`, `OFFICER_INTERVENTION`.

### Phase 4: Delay Prediction (D5)
* `POST /api/v1/projects/{project_id}/predict`: Run ML inference and return risk probability + level.
* `GET /api/v1/projects/{project_id}/prediction`: Fetch latest cached project prediction.

### Phase 5: Explainability & Interventions
* `GET /api/v1/projects/{project_id}/explanation`: Retrieve risk factors and evidence citations.
* `GET /api/v1/projects/{project_id}/interventions`: Retrieve prioritized intervention candidates.

### Phase 6: Decision Intelligence & Audit
* `GET /api/v1/projects/{project_id}/decision-context`: Retrieve officer decision context package.
* `POST /api/v1/decisions`: Create or update officer decision state.
* `POST /api/v1/decisions/{decision_id}/action`: Initiate officer action & trigger notification simulation.
* `GET /api/v1/projects/{project_id}/audit-trail`: Retrieve immutable audit events.

## Test Validation Matrix
For every API endpoint, test script `tests/test_final_integration.py` verifies:
1. Valid Request payload → `200 OK` / `201 Created`
2. Nonexistent ID → `404 Not Found`
3. Invalid query parameters → `422 Unprocessable Entity`
4. Cross-project access → `403 Forbidden` / Empty isolated dataset
