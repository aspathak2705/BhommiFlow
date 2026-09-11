# 17. Technical Deep Dive

## Deep Technical Specifications

### 1. Unified RAG & SQL Filtering Engine
* **File**: `backend/app/services/rag_service.py`
* **Implementation**: Uses PostgreSQL string indexing and vector similarity search with forced `WHERE project_id = :project_id` filters. Avoids slow in-memory chunk processing by executing JOINs directly in database execution plans.

### 2. D5 Calibrated Inference Pipeline
* **File**: `backend/app/services/prediction_service.py`
* **Artifacts**: `delay-model-calibrated.joblib` (`CalibratedClassifierCV` wrapper) and `preprocessor.joblib` (`ColumnTransformer`).
* **Feature Transformer**: Encodes string categorical features (`project_type`, `state`, `district`) and scales numeric features (`land_required_area`, `affected_families`, `affected_landholders`).

### 3. Human-in-the-Loop State Machine
* **File**: `backend/app/services/decision_intelligence_service.py`
* **Transitions**: Validates exact allowed state transitions:
  * `RECOMMENDED` → `['REVIEWED', 'ACCEPTED', 'REJECTED', 'DEFERRED']`
  * `ACCEPTED` → `['ACTION_INITIATED', 'DEFERRED']`
  * `ACTION_INITIATED` → `['AWAITING_OUTCOME', 'RESOLVED']`
