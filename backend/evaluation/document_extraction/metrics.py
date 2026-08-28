from typing import List, Dict, Any

class ExtractionMetricsCalculator:
    @staticmethod
    def calculate(evaluation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(evaluation_results)
        
        metrics = {
            "issue_date": {"total": total, "evaluable": 0, "correct": 0, "missing": 0, "incorrect": 0, "partial": 0, "accuracy": 0.0},
            "registration_number": {"total": total, "evaluable": 0, "correct": 0, "missing": 0, "incorrect": 0, "partial": 0, "accuracy": 0.0},
            "survey_number": {"total": total, "evaluable": 0, "correct": 0, "missing": 0, "incorrect": 0, "partial": 0, "accuracy": 0.0},
            "district": {"total": total, "evaluable": 0, "correct": 0, "missing": 0, "incorrect": 0, "partial": 0, "accuracy": 0.0},
            "taluka": {"total": total, "evaluable": 0, "correct": 0, "missing": 0, "incorrect": 0, "partial": 0, "accuracy": 0.0},
            "village": {"total": total, "evaluable": 0, "correct": 0, "missing": 0, "incorrect": 0, "partial": 0, "accuracy": 0.0}
        }

        error_analysis = []

        for res in evaluation_results:
            doc_id = res["document_id"]
            for field in ["issue_date", "registration_number", "survey_number"]:
                f_data = res[field]
                if f_data["evaluable"]:
                    metrics[field]["evaluable"] += 1
                    if f_data["correct"]:
                        metrics[field]["correct"] += 1
                    else:
                        if not f_data["predicted"]:
                            metrics[field]["missing"] += 1
                            cat = "MISSING"
                        else:
                            metrics[field]["incorrect"] += 1
                            cat = "INCORRECT"
                            
                        error_analysis.append({
                            "document_id": doc_id,
                            "field": field,
                            "expected": f_data["expected"],
                            "predicted": f_data["predicted"],
                            "error_category": cat
                        })
                else:
                    metrics[field]["missing"] += 1 # Not present/evaluable in ground truth

        # Calculate accuracies
        for field, stats in metrics.items():
            if stats["evaluable"] > 0:
                stats["accuracy"] = round(stats["correct"] / stats["evaluable"], 4)

        return {
            "total_records": total,
            "field_metrics": metrics,
            "error_analysis": error_analysis
        }
