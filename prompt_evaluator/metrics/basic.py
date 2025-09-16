import numpy as np
from typing import Dict, List
from collections import Counter

from ..core.base import BaseMetric, EvaluationResult


class AverageScoreMetric(BaseMetric):
    def __init__(self):
        super().__init__(
            name="average_score",
            description="Calculates the average score across all evaluations"
        )

    def calculate(self, results: List[EvaluationResult]) -> Dict[str, float]:
        if not results:
            return {"average_score": 0.0}

        scores = [r.score for r in results]
        return {"average_score": np.mean(scores)}


class ScoreDistributionMetric(BaseMetric):
    def __init__(self):
        super().__init__(
            name="score_distribution",
            description="Provides distribution statistics for scores"
        )

    def calculate(self, results: List[EvaluationResult]) -> Dict[str, float]:
        if not results:
            return {}

        scores = [r.score for r in results]
        return {
            "mean": np.mean(scores),
            "std": np.std(scores),
            "min": np.min(scores),
            "max": np.max(scores),
            "median": np.median(scores),
            "percentile_25": np.percentile(scores, 25),
            "percentile_75": np.percentile(scores, 75)
        }


class SuccessRateMetric(BaseMetric):
    def __init__(self, threshold: float = 0.8):
        super().__init__(
            name="success_rate",
            description=f"Calculates percentage of results above threshold {threshold}"
        )
        self.threshold = threshold

    def calculate(self, results: List[EvaluationResult]) -> Dict[str, float]:
        if not results:
            return {"success_rate": 0.0}

        successful = sum(1 for r in results if r.score >= self.threshold)
        success_rate = successful / len(results)
        return {
            "success_rate": success_rate,
            "successful_count": successful,
            "total_count": len(results)
        }


class ConsistencyMetric(BaseMetric):
    def __init__(self):
        super().__init__(
            name="consistency",
            description="Measures consistency of performance across evaluations"
        )

    def calculate(self, results: List[EvaluationResult]) -> Dict[str, float]:
        if not results:
            return {"consistency": 0.0}

        scores = [r.score for r in results]
        consistency = 1.0 - (np.std(scores) / np.mean(scores)) if np.mean(scores) > 0 else 0.0
        return {"consistency": max(0.0, consistency)}


class ComparisonMetric(BaseMetric):
    def __init__(self):
        super().__init__(
            name="comparison",
            description="Compares performance between different prompt versions"
        )

    def calculate_comparison(self, results_dict: Dict[str, List[EvaluationResult]]) -> Dict[str, Dict[str, float]]:
        comparison = {}

        for version_name, results in results_dict.items():
            if not results:
                comparison[version_name] = {"average_score": 0.0, "count": 0}
                continue

            scores = [r.score for r in results]
            comparison[version_name] = {
                "average_score": np.mean(scores),
                "std": np.std(scores),
                "count": len(results),
                "min": np.min(scores),
                "max": np.max(scores)
            }

        # Add relative performance comparisons
        avg_scores = {v: metrics["average_score"] for v, metrics in comparison.items()}
        if avg_scores:
            best_version = max(avg_scores.keys(), key=lambda k: avg_scores[k])
            best_score = avg_scores[best_version]

            for version_name in comparison:
                current_score = avg_scores[version_name]
                relative_performance = (current_score / best_score) if best_score > 0 else 0.0
                comparison[version_name]["relative_performance"] = relative_performance
                comparison[version_name]["is_best"] = (version_name == best_version)

        return comparison

    def calculate(self, results: List[EvaluationResult]) -> Dict[str, float]:
        # This is a placeholder - the main functionality is in calculate_comparison
        return {"note": "Use calculate_comparison method for full comparison analysis"}