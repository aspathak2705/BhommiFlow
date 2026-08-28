# Test Documents Manifest

This directory contains synthetic text artifacts designed to test the metadata extraction and document comparison features of BhoomiFlow without using real or sensitive government data.

## Document List

1. **[synthetic_clean_deed.txt](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/test_documents/synthetic_clean_deed.txt)**
   * **Purpose**: Citizen primary upload simulating clean baseline records.
   * **Expected Extraction**: 
     * Issue Date: `2026-04-12`
     * Registration Number: `REG-2026-1001`
     * Survey Number: `123/4A`
   * **Expected Comparison**: Clean matching with no conflict flags when compared with a matching counterpart.

2. **[synthetic_discrepant_deed.txt](file:///c:/Users/athar/OneDrive/Documents/projects/BhommiFlow/sop/test_documents/synthetic_discrepant_deed.txt)**
   * **Purpose**: Simulates a modified or mismatching official counterpart to test conflict triggers.
   * **Expected Extraction**:
     * Issue Date: `2026-04-12`
     * Registration Number: `REG-2026-9999`
     * Survey Number: `123/4B`
   * **Expected Comparison**: Highlighting comparison discrepancies (mismatching registration and survey values).
