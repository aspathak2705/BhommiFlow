# BhoomiFlow Judge Testing Package

This directory contains standard operating procedures (SOPs) and synthetic test materials to guide judges and technical evaluators in executing complete end-to-end acceptance tests of the BhoomiFlow MVP.

## Folder Contents
* **[SOP.md](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/SOP.md)**: Main Standard Operating Procedure document with step-by-step citizen/officer testing scripts and the final acceptance verification matrix.
* **[test_documents/](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/test_documents)**: Synthetic document artifacts used during document upload, metadata extraction, and conflict validation tests.

> [!IMPORTANT]
> **Strict Data Integrity Rule**:
> * All files in this folder are **synthetic artifacts**. They must never be inserted into production PostgreSQL database tables.
> * Existing production runtime tables remain isolated and receive data solely from the live user/officer flows.
