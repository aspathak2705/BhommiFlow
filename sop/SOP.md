# BhoomiFlow — Final Judge Testing SOP

Standard Operating Procedure for testing the end-to-end MVP features of BhoomiFlow from both Citizen and Officer perspectives.

---

## 1. Prerequisites & Environment Setup
Before starting the test, ensure the application is running:
* **Backend API**: Accessible at `http://localhost:8000` (FastAPI)
* **Frontend UI**: Accessible at `http://localhost:5173` (React/Vite dev server)
* **Database**: Configured database connection active with migrations applied to the latest version.
* **Knowledge base**: Verify that Dataset 4 procedures are loaded into `knowledge_sources` tables.

---

## 2. Test Scenarios & Manifest

We provide two synthetic documents in the `sop/test_documents/` folder. Load these during the document upload testing phases:
* **[synthetic_clean_deed.txt](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/test_documents/synthetic_clean_deed.txt)**: Clean baseline land deed record.
* **[synthetic_discrepant_deed.txt](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/test_documents/synthetic_discrepant_deed.txt)**: Modified deed with conflicting values (registration & survey numbers).

> [!IMPORTANT]
> **Strict Data Integrity Boundary**:
> * Evaluation datasets (Datasets 1, 2, and 3) must **never** be imported into production PostgreSQL tables.
> * Synthetic test records must be created manually using the actual registration/upload UI steps documented below.

---

## 3. Citizen Testing Workflow

### Step 1: Account Registration & Login
1. Open the BhoomiFlow portal at `http://localhost:5173/login`.
2. Select **Register**, fill in unique credentials, set role to **citizen**, and click **Submit**.
3. Toggle back to **Sign In**, log in with the registered user, and confirm redirection to the **Citizen Dashboard**.

### Step 2: Create Land Case
1. On the Citizen Dashboard, click the **Create New Case** button.
2. Complete the multi-step intake form:
   * Title: `Test Case Mutation Shrigonda`
   * Location: Village `Vitthalwadi`, Taluka `Shrigonda`, District `Ahmednagar`
   * Category: `7/12 / Land Record`
   * Description: `Filing inheritance mutation claim for agricultural land parcel.`
3. Click **Submit Case**. Verify the case appears in your dashboard queue with a status of `SUBMITTED`.

### Step 3: Upload Evidence
1. Click on the newly created case to open the **Case Detail** workspace view.
2. Under the **Attach Document / Evidence** panel, select **Browse/Select File** and pick `synthetic_clean_deed.txt`.
3. Set the Category selector to `Sale Deed` and click **Upload Evidence**.
4. Verify the document is added under the **Case Evidence & Documents** section, showing a server-side SHA-256 hash identity and extracted rule metadata.

---

## 4. Officer Testing Workflow

### Step 1: Login & Workspace Navigation
1. Sign out of the Citizen account.
2. Register and log in using an **officer** account profile with jurisdiction Taluka `Shrigonda` and District `Ahmednagar`.
3. Confirm redirection to the **Officer Workspace** dashboard queue.

### Step 2: Open Case Queue
1. Verify the citizen-submitted case `Test Case Mutation Shrigonda` is listed in your queue.
2. Open the case detail view. Verify you can view:
   * Logical **Case Graph** projection (Persons, Parcels, Documents, Events).
   * Verifiable **Timeline Activity** history.
   * Grounded **Government Procedure Guidance** search engine.

### Step 3: Conflict Identification & Guidance
1. Query the grounded search box: *"How do I view online Satbara Utara?"*
2. Verify the system responds with an authoritative explanation citing sources such as `https://bhulekh.mahabhumi.gov.in/`.
3. Enter an unsupported query like *"RandomTextNoTopic"* and check if it safely triggers the fallback response.

### Step 4: Evidence Request Workflow
1. In the **Status Workflow** panel, change the status to `ACTION_REQUIRED` and write an request note: *"Please upload official mutation deed counterpart for verification."*
2. Click **Update Workflow Status**.
3. Sign back in as the Citizen and confirm the case displays the updated request timeline and action banners.

---

## 5. Security & Verification Tests
* **Case Isolation**: Ensure Citizen A cannot access Citizen B's dashboard entries or view another case's timeline hashes.
* **Officer Assignment Boundaries**: Officers cannot view or resolve case files outside their assigned Taluka/District jurisdiction.

---

## 6. Technical Verification
To confirm codebase regression coverage and compilation packaging are active:
* **Run Python Backend Suite**:
  ```bash
  python -m pytest
  ```
* **Verify Frontend Builds**:
  ```bash
  npm run build
  ```

---

# Final Judge Test Report Template

* **Test Date**: `________________________`
* **Target Environment**: `FastAPI 0.110.0 + React 18`

| Task ID | Component | Action | Expected Result | Status (PASS / FAIL) |
|---|---|---|---|---|
| T-01 | Auth | Citizen Registration & Sign In | Token generated, loads dashboard | |
| T-02 | Case | Create new intake claim | Validated ID generated, status SUBMITTED | |
| T-03 | File | Upload `synthetic_clean_deed.txt` | SHA-256 computed, metadata extracted | |
| T-04 | Logic | Check relationship graph | Person, parcel, and document nodes visible | |
| T-05 | RAG | Request online Satbara guidance | Response displays official government URL | |
| T-06 | Admin | Workflow status transition | State maps correctly, timeline appends hash | |
| T-07 | Security | Citizen cross-case query | Return 401 / 403 access denied | |
| T-08 | RAG | Query unsupported procedures | Triggers "No relevant guidance available" | |

**Final Readiness Verdict**:
* `[ ]` **READY FOR FINAL DEMO** (No blocking issues present)
* `[ ]` **READY WITH KNOWN ISSUES** (Document details in comments)
* `[ ]` **NOT READY**
