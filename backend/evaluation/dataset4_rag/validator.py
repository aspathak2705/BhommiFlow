import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Dataset4Validator:
    @staticmethod
    def validate_and_repair() -> Dict[str, Any]:
        """
        Verify the structure of dataset4_government_procedure_rag.json.
        Performs deterministic formatting check and writes to a .validated.json target.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        source_path = os.path.join(base_dir, "datasets", "dataset4_rag", "dataset4_government_procedure_rag.json")
        validated_path = os.path.join(base_dir, "datasets", "dataset4_rag", "dataset4_government_procedure_rag.validated.json")

        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Dataset 4 original corpus not found at: {source_path}")

        # 1. Deterministic JSON Syntax Check & Parse
        try:
            with open(source_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            parse_status = "SUCCESS"
            issue_detected = "None - JSON is syntactically valid."
        except json.JSONDecodeError as jde:
            parse_status = "MALFORMED"
            issue_detected = f"JSON syntax error: {jde.msg} at line {jde.lineno} col {jde.colno}"
            logger.error(issue_detected)
            # Try basic recovery (e.g. trailing comma or bracket corrections) if deterministic
            raise ValueError(f"MALFORMED JSON: {issue_detected}. Aborting ingestion to prevent data corruption.")

        # 2. Structural Schema Verification
        documents = data.get("documents", [])
        valid_records = []
        skipped_records = []

        for idx, doc in enumerate(documents):
            required = ["source_id", "title", "department", "document_type", "content"]
            missing_fields = [f for f in required if not doc.get(f)]
            if missing_fields:
                skipped_records.append({
                    "index": idx,
                    "source_id": doc.get("source_id", "UNKNOWN"),
                    "reason": f"Missing required fields: {missing_fields}"
                })
            else:
                valid_records.append(doc)

        # 3. Write validated output copy
        validated_data = {
            "dataset_name": data.get("dataset_name"),
            "scope": data.get("scope"),
            "actual_document_count": len(valid_records),
            "documents": valid_records
        }

        with open(validated_path, "w", encoding="utf-8") as f:
            json.dump(validated_data, f, indent=2, ensure_ascii=False)

        return {
            "original_parse_status": parse_status,
            "original_record_count": len(documents),
            "validated_record_count": len(valid_records),
            "skipped_records": skipped_records,
            "issue_detected": issue_detected,
            "repair_performed": "Format normalization and schema extraction only."
        }
