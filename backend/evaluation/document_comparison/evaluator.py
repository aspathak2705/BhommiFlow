from typing import Dict, Any

class DocumentComparisonEvaluator:
    @staticmethod
    def evaluate_scenario(record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Grounded evaluation comparing scenario variables.
        Since original source document files are not available, it maps summaries/descriptions
        and evaluates rule logic.
        """
        payload = record["comparison_payload"]
        
        # 1. Exact match / Byte identity check
        predicted_byte_identical = payload.get("byte_identical", False)
        
        # 2. Content equality check
        # We verify if comparison scenario has differences or if summaries are identical
        scenario = record["comparison_scenario"].lower()
        predicted_content_match = True
        
        # Scenario check to replicate comparison engine triggers
        if any(diff in scenario for diff in ["difference", "discrepancy", "mismatch", "variation"]):
            predicted_content_match = False
            
        # 3. Discrepancy flags check
        has_name_diff = "name" in scenario
        has_date_diff = "date" in scenario
        has_number_diff = "number" in scenario or "price" in scenario or "area" in scenario
        has_address_diff = "address" in scenario or "location" in scenario
        has_page_diff = "page" in scenario
        has_format_diff = "format" in scenario or "formatting" in scenario

        # 4. Review Required Decision (Matches Phase 2 engine logic)
        # If hashes differ, and content mismatch is detected or content comparison is unavailable/fails, review is required.
        predicted_review_required = not predicted_content_match or not predicted_byte_identical

        # Overwrite format differences: format changes alone do not require review if content matches
        if has_format_diff and predicted_content_match:
            predicted_review_required = False

        return {
            "comparison_id": record["comparison_id"],
            "byte_identical": predicted_byte_identical,
            "content_match": predicted_content_match,
            "name_difference": has_name_diff,
            "date_difference": has_date_diff,
            "number_difference": has_number_diff,
            "address_difference": has_address_diff,
            "page_difference": has_page_diff,
            "format_difference": has_format_diff,
            "review_required": predicted_review_required
        }
