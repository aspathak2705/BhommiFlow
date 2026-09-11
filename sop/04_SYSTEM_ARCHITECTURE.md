# 04. System Architecture

```
                    BHOOMISAKHA
                         |
        +----------------+----------------+
        |                |                |
        ↓                ↓                ↓
       D1               D2               D3
     CASE            DOCUMENT         COMPARISON
     DATA             DATA             /CONFLICT
        |                |                |
        +----------------+----------------+
                         ↓
                  EVIDENCE RAG
                         ↓
             EVIDENCE INTELLIGENCE
                         ↓
                  FEATURE ENGINE
                         ↓
                        D5
                  DELAY MODEL
                         ↓
                RISK PROBABILITY
                         ↓
             +-----------+-----------+
             ↓           ↓           ↓
          PREDICT     EXPLAIN    INTERVENE
                         |           |
                         +-----+-----+
                               ↓
                         D4 PROCEDURE
                              RAG
                               ↓
                       OFFICER DECISION
                               ↓
                           ACTION
                               ↓
                     NOTIFICATION SIM
                               ↓
                            AUDIT
                               ↓
                           OUTCOME
```

## Architectural Planes

### 1. Experience Plane
* **Technology**: React, Vite, TailwindCSS
* **Target Users**: Citizens, Nodal Officers, Project Managers
* **Features**: Case Intake, Evidence Viewer, Officer Dashboard, Decision Context, Realtime Notifications.

### 2. Evidence Plane
* **Datasets**: D1 (Cases), D2 (Documents), D3 (Comparisons)
* **Storage**: PostgreSQL (Relational metadata), Unified Knowledge Chunks (Vector RAG)
* **Services**: `UnifiedIngestionService`, `EvidenceIntelligenceService`, `RAGService`
* **Provenance**: Immutable chunk IDs (`D1:<id>:01`, `D2:<id>:01`, `D3:<id>:01`) with case/project isolation.

### 3. Intelligence Plane
* **Services**: `FeatureEngineeringService`, `DelayPredictionService`, `ExplainabilityService`
* **D5 Machine Learning Model**: `CalibratedClassifierCV` wrapping `GradientBoostingClassifier` with `ColumnTransformer` preprocessor.
* **Leakage Protection**: Strict exclusion of future outcome columns (`future_delay`, `delay_days`, etc.).

### 4. Decision & Governance Plane
* **Datasets**: D4 (Government Procedure Knowledge)
* **Services**: `ProcedureRAGService`, `InterventionService`, `DecisionIntelligenceService`, `NotificationService`
* **Workflow**: Human-in-the-loop decision state machine (`RECOMMENDED` → `REVIEWED` → `ACCEPTED` → `ACTION_INITIATED` → `RESOLVED`) + Immutable Audit Trail.
