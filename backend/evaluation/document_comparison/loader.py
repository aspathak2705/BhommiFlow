import os
import json
from typing import List, Dict, Any

class Dataset3Loader:
    @staticmethod
    def load_dataset() -> List[Dict[str, Any]]:
        # Expected path
        dataset_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "datasets",
            "dataset3_document_comparison",
            "bhoomiflow_dataset3_document_comparison_100.json"
        )
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset 3 JSON not found at path: {dataset_path}")

        with open(dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        validated_records = []
        for index, record in enumerate(data):
            # Validate required top-level schema fields
            required_keys = ["comparison_scenario", "document_type", "location", "comparison_id", "document_a_id", "document_b_id", "comparison_payload"]
            for rk in required_keys:
                if rk not in record:
                    raise ValueError(f"Malformed Record at index {index}: missing field '{rk}'")
            
            # Validate payload fields
            payload = record["comparison_payload"]
            payload_keys = ["same_document", "byte_identical", "expected_hash_match", "content_match", "expected_review"]
            for pk in payload_keys:
                if pk not in payload:
                    raise ValueError(f"Malformed payload in Record {record['comparison_id']}: missing '{pk}'")
            
            validated_records.append(record)
            
        return validated_records
