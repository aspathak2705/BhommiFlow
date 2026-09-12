# 03. Golden Demo Data & Case Specification

> **Canonical Demo Case ID:** `BF-CASE-000001`  
> **Canonical Demo Project ID:** `PROJ-FC0ACD7D132F` (Nagpur Bypass Link)  
> **Canonical Demo Parcel ID:** `PARCEL-EE11389A9F49`  

---

## 1. Golden Case Attributes

| Attribute Name | Value in Live Database | Notes / Purpose |
| :--- | :--- | :--- |
| **Project Code** | `PROJ-FC0ACD7D132F` | Primary highway bypass project |
| **Project Name** | `Nagpur Bypass Link` | Public infrastructure development |
| **State / District** | `Maharashtra` / `Nagpur` | Regional jurisdiction |
| **Taluka / Village** | `Nagpur Rural` / `Besa` | Local revenue village |
| **Survey Number** | `104/A` | Primary land survey identifier |
| **Subdivision Number**| `2` | Sub-parcel division |
| **Total Parcel Area** | `1.45 Hectares` | Agricultural Class-I land |
| **Primary Landholder** | `Rajesh Kumar Patil` | Registered citizen applicant |
| **Discrepancy Name** | `Rajesh K. Patil` | Third-party objection record name variation |
| **Acquisition Stage** | `OBJECTION_RESOLUTION` | Section 15 RFCTLARR Act 2013 stage |

---

## 2. Prepared Synthetic Documents (`demo_evidence_pack`)

All files are verified and located in `docs/SOP/demo_pack/mock_documents/`:

1. `01_land_record.pdf` - 7/12 Extract (Record of Rights for Survey 104/A/2).
2. `02_ownership_record.pdf` - Registered Sale Deed & Title Conveyance Certificate.
3. `03_applicant_document.pdf` - Identity & Residence Verification for Rajesh Kumar Patil.
4. `04_acquisition_notice.pdf` - Statutory Section 11 Preliminary Notification.
5. `05_compensation_record.pdf` - Land Valuation Award (Rs 16,31,250 award calculation).
6. `06_conflicting_record.pdf` - Third-party objection noting spelling mismatch ("Rajesh K. Patil").

> [!NOTE]  
> All files contain explicit header/footer watermarks: `"DEMO / SYNTHETIC DATA — NOT AN OFFICIAL GOVERNMENT DOCUMENT"`.
