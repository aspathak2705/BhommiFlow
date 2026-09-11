# 08. Security Testing SOP

## Security Controls Overview

### 1. Authentication & RBAC
* **Mechanism**: JWT Token authentication via `get_current_user` dependency.
* **Roles**: `citizen`, `officer`, `admin`.
* **Enforcement**: Protected routes verify caller role before executing service logic.

### 2. IDOR & Project Isolation
* **Requirement**: User/Officer assigned to Project A must never retrieve data from Project B.
* **Verification**: `RAGService` enforces `WHERE project_id = :project_id` on all vector chunk queries. Cross-project query tests return zero chunks or `403 Forbidden`.

### 3. Input Validation & SQL Injection Prevention
* **Mechanism**: ORM parameterized queries via SQLAlchemy. Raw string concatenation is strictly prohibited in services.
* **Payload Validation**: Pydantic schemas enforce type constraints and regex validations on all API inputs.

### 4. File Security & MIME Validation
* **Allowed MIME Types**: `application/pdf`, `image/png`, `image/jpeg`.
* **Path Traversal Protection**: Uploaded files are saved using generated UUID filenames; original client filenames are sanitized.

### 5. Production Response Security Headers
* `X-Content-Type-Options: nosniff`
* `X-Frame-Options: DENY`
* `Referrer-Policy: strict-origin-when-cross-origin`
* `Strict-Transport-Security: max-age=31536000; includeSubDomains` (when `ENVIRONMENT=production`)
