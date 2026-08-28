import os
import json
import csv
from typing import List, Dict, Any

class Dataset2Loader:
    @staticmethod
    def load_json() -> List[Dict[str, Any]]:
        dataset_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "datasets",
            "dataset2_document_extraction",
            "bhoomiflow_dataset2_document_extraction_50.json"
        )
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset 2 JSON not found at: {dataset_path}")

        with open(dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        validated = []
        for index, record in enumerate(data):
            # Validate required schemas
            required = ["document_id", "document_type", "ocr_text", "document_payload"]
            for field in required:
                if field not in record:
                    raise ValueError(f"Malformed JSON at index {index}: missing '{field}'")
            validated.append(record)
        return validated

    @staticmethod
    def load_csv() -> List[Dict[str, Any]]:
        dataset_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "datasets",
            "dataset2_document_extraction",
            "bhoomiflow_dataset2_document_extraction_50.csv"
        )
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset 2 CSV not found at: {dataset_path}")

        records = []
        with open(dataset_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
        return records

    @staticmethod
    def check_consistency() -> Dict[str, Any]:
        json_data = Dataset2Loader.load_json()
        csv_data = Dataset2Loader.load_csv()

        discrepancies = []
        # Check counts
        if len(json_data) != len(csv_data):
            discrepancies.append(f"Count mismatch: JSON has {len(json_data)}, CSV has {len(csv_data)}")

        # Check document_id keys alignment
        json_ids = {r["document_id"] for r in json_data}
        csv_ids = {r["document_id"] for r in csv_data}

        if json_ids != csv_ids:
            discrepancies.append("Identifier sets differ between CSV and JSON files.")

        return {
            "json_count": len(json_data),
            "csv_count": len(csv_data),
            "consistent": len(discrepancies) == 0,
            "discrepancies": discrepancies
        }
