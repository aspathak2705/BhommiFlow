from typing import Dict, Any
from app.services.extraction_service import extract_metadata_from_text

class DocumentExtractionEvaluator:
    @staticmethod
    def evaluate_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate BhoomiFlow production extraction logic against Dataset 2 ground-truth.
        We run the text extractor using the OCR content provided.
        """
        ocr_text = record.get("ocr_text", "")
        ground_truth = record.get("document_payload", {})
        
        # Run actual extraction pipeline
        predicted_metadata = extract_metadata_from_text(ocr_text)

        # Map extraction values
        predicted_issue_date = predicted_metadata.get("issue_date", {}).get("value")
        predicted_reg_no = predicted_metadata.get("registration_number", {}).get("value")
        predicted_survey_no = predicted_metadata.get("survey_number", {}).get("value")

        # Ground truth values
        gt_issue_date = ground_truth.get("issue_date")
        gt_reg_no = ground_truth.get("registration_number")
        gt_survey_no = ground_truth.get("survey_number")

        return {
            "document_id": record["document_id"],
            "issue_date": {
                "expected": gt_issue_date,
                "predicted": predicted_issue_date,
                "evaluable": gt_issue_date is not None,
                "correct": gt_issue_date == predicted_issue_date if gt_issue_date else False
            },
            "registration_number": {
                "expected": gt_reg_no,
                "predicted": predicted_reg_no,
                "evaluable": gt_reg_no is not None,
                "correct": gt_reg_no == predicted_reg_no if gt_reg_no else False
            },
            "survey_number": {
                "expected": gt_survey_no,
                "predicted": predicted_survey_no,
                "evaluable": gt_survey_no is not None,
                "correct": gt_survey_no == predicted_survey_no if gt_survey_no else False
            },
            # Mark other fields not evaluable from available regular expressions as NOT_EVALUABLE
            "district": {"evaluable": False, "status": "NOT_EVALUABLE_FROM_AVAILABLE_ARTIFACTS"},
            "taluka": {"evaluable": False, "status": "NOT_EVALUABLE_FROM_AVAILABLE_ARTIFACTS"},
            "village": {"evaluable": False, "status": "NOT_EVALUABLE_FROM_AVAILABLE_ARTIFACTS"}
        }
