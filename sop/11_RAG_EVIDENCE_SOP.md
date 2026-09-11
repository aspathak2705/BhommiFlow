# 11. RAG Evidence SOP

## Dual RAG Pipeline Specifications

```
D1 Case Data ─────┐
D2 Document Data ─┼──► EVIDENCE RAG ──► Evidence Intelligence
D3 Comparison ────┘

D4 Procedure ───────► PROCEDURE RAG ──► Officer Decision Guidance
```

### Deterministic Ingestion & ID Rules
* **D1 Case Chunks**: `D1:<case_id>:01` (Dataset = `D1`, origin = `synthetic`)
* **D2 Document Chunks**: `D2:<doc_id>:01` (Dataset = `D2`, origin = `synthetic`)
* **D3 Comparison Chunks**: `D3:<comp_id>:01` (Dataset = `D3`, origin = `synthetic`)
* **D4 Procedure Chunks**: `D4:<proc_id>:01` (Dataset = `D4`, verified government manual)

### Retrieval Modes & Scope Filtering
1. `CASE_INVESTIGATION`: Queries D1 + D2 + D3 chunks filtered by `project_id`.
2. `DOCUMENT_INVESTIGATION`: Queries D2 + D3 extractions.
3. `CONFLICT_INVESTIGATION`: Queries D3 comparison mismatches.
4. `PROCEDURE_QUESTION`: Queries D4 procedure chunks only.
5. `OFFICER_INTERVENTION`: Queries D1 + D2 + D3 + D4 for holistic decision context.

### Case Isolation Guarantee
Vector retrieval uses SQL-level `WHERE project_id = :project_id` filters, guaranteeing zero cross-case data leakage.
