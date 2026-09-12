# 25. Step-by-Step Demo Evidence Upload Guide

> **Purpose:** Practical guide for pitch operators to upload pre-validated demo documents during the live presentation.

---

## Upload Sequence & Expected Outcomes

### Document 1: Land Record (7/12 Extract)
- **File:** `docs/SOP/demo_pack/mock_documents/01_land_record.pdf`
- **Document Type:** `Record of Rights`
- **Why Upload:** Demonstrates baseline landholder extraction for Survey No. `104/A`, Sub-division `2`, Village Besa.
- **Expected Outcome:** System extracts `Rajesh Kumar Patil`, `1.45 Hectares`, and registers immutable document SHA-256 hash.
- **What to Say to Judge:** *"BhoomiSakha immediately digests the 7/12 extract, extracting landholder attributes and creating a cryptographic provenance hash."*

---

### Document 2: Ownership Record (Title Deed)
- **File:** `docs/SOP/demo_pack/mock_documents/02_ownership_record.pdf`
- **Document Type:** `Title Deed`
- **Why Upload:** Demonstrates title verification and joint ownership mapping.
- **Expected Outcome:** System links title deed to primary land parcel.
- **What to Say to Judge:** *"The system anchors the sale deed to the land parcel graph, mapping co-ownership relationships."*

---

### Document 3: Discrepancy Record (Objection Record)
- **File:** `docs/SOP/demo_pack/mock_documents/06_conflicting_record.pdf`
- **Document Type:** `Conflicting Record`
- **Why Upload:** Demonstrates D3 Cross-Record Comparison Engine.
- **Expected Outcome:** System flags a high-priority discrepancy between `Rajesh Kumar Patil` and `Rajesh K. Patil`.
- **What to Say to Judge:** *"Here, D3 compares legacy records against the objection filing, immediately surfacing a title spelling mismatch before it halts acquisition."*
