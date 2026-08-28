import re
from typing import Optional, Dict, Any

# Matches DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
DATE_PATTERN = re.compile(r"\b(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})\b")

# Matches Registration/Document numbers e.g., Reg No. 12345/2026 or No: 98765
REG_PATTERN = re.compile(r"(?:reg(?:istration)?\.?\s*(?:no)?\.?\s*|document\s*no\.?\s*|no:?\s*)(\d+[\w\/\-]*)", re.IGNORECASE)

# Matches Land survey numbers e.g., Survey No: 41/2A or S.No 12
SURVEY_PATTERN = re.compile(r"(?:survey\s*(?:no)?\.?:?|s\.?\s*no\.?:?)\s*(\d+[\w\/\-]*)", re.IGNORECASE)

def normalize_date(day: str, month: str, year: str) -> str:
    d = day.zfill(2)
    m = month.zfill(2)
    return f"{year}-{m}-{d}"

def extract_metadata_from_text(text: str) -> Dict[str, Any]:
    extracted = {}
    
    # Date extraction
    date_match = DATE_PATTERN.search(text)
    if date_match:
        day, month, year = date_match.groups()
        extracted["issue_date"] = {
            "value": normalize_date(day, month, year),
            "source": "regex_date_pattern"
        }
    
    # Registration number
    reg_match = REG_PATTERN.search(text)
    if reg_match:
        extracted["registration_number"] = {
            "value": reg_match.group(1),
            "source": "regex_reg_pattern"
        }

    # Survey number
    survey_match = SURVEY_PATTERN.search(text)
    if survey_match:
        extracted["survey_number"] = {
            "value": survey_match.group(1),
            "source": "regex_survey_pattern"
        }

    return extracted
