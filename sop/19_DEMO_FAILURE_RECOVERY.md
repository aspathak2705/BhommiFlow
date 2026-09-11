# 19. Demo Failure Recovery

## Emergency Live Contingency Playbook

### Scenario A: Live File Upload / OCR Slow
* **Action**: Do not wait for live upload. Click `Load Sample Document Fixture (712_wagholi.pdf)`.
* **Script**: *"We will load our pre-extracted sample 7/12 extract to demonstrate immediate field parsing."*

### Scenario B: Database Connection Reset
* **Action**: Restart uvicorn server in terminal using pre-saved command:
  ```powershell
  python -m uvicorn app.main:app --reload --port 8000
  ```
* **Script**: *"Refreshing local database session."*

### Scenario C: UI Renders Empty Risk Drawer
* **Action**: Navigate to backup project fixture `PRJ-TEST-INTEG-002`.
* **Script**: *"Let's switch to our secondary active corridor project to view the decision context."*

### Scenario D: Browser Freezes / Console Exception
* **Action**: Hard refresh page (`Ctrl + Shift + R`). All states are persisted in PostgreSQL.
