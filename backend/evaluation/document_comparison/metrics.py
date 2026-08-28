from typing import List, Dict, Any

class EvaluationMetricsCalculator:
    @staticmethod
    def calculate(ground_truth: List[Dict[str, Any]], predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(ground_truth)
        evaluable = total
        non_evaluable = 0

        # Exact, content, and review required counts
        matches_exact_gt = sum(1 for r in ground_truth if r["comparison_payload"]["byte_identical"])
        matches_exact_pred = sum(1 for p in predictions if p["byte_identical"])
        
        matches_content_gt = sum(1 for r in ground_truth if r["comparison_payload"]["content_match"])
        matches_content_pred = sum(1 for p in predictions if p["content_match"])

        # Calculate TP, FP, FN, TN for review_required flag
        tp = 0
        fp = 0
        fn = 0
        tn = 0

        category_stats = {}

        for gt, pred in zip(ground_truth, predictions):
            gt_payload = gt["comparison_payload"]
            gt_review = gt_payload["expected_review"]
            pred_review = pred["review_required"]

            if gt_review and pred_review:
                tp += 1
            elif not gt_review and pred_review:
                fp += 1
            elif gt_review and not pred_review:
                fn += 1
            else:
                tn += 1

            # Categorize by scenario
            scenario = gt["comparison_scenario"]
            if scenario not in category_stats:
                category_stats[scenario] = {"total": 0, "correct": 0}
            category_stats[scenario]["total"] += 1
            
            # Match prediction of review required to ground truth
            if gt_review == pred_review:
                category_stats[scenario]["correct"] += 1

        # Precision, Recall, F1 for review_required
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Rule Consistency is the percentage of logical matches to expected review flags
        logical_matches = sum(1 for gt, pred in zip(ground_truth, predictions) if gt["comparison_payload"]["expected_review"] == pred["review_required"])
        rule_consistency = round(logical_matches / total, 4) if total > 0 else 0.0

        return {
            "total_records": total,
            "evaluable_records": evaluable,
            "non_evaluable_records": non_evaluable,
            "exact_matches_gt": matches_exact_gt,
            "exact_matches_pred": matches_exact_pred,
            "content_matches_gt": matches_content_gt,
            "content_matches_pred": matches_content_pred,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "rule_consistency": rule_consistency,
            "category_breakdown": category_stats
        }
