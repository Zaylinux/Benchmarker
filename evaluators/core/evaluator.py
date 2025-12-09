"""
Core evaluation orchestration.

This module provides the main Evaluator class and evaluation function that
coordinates scoring across multiple task categories.
"""

from typing import Any, Dict, List, Optional

from evaluators.core.metrics import score_category


class Evaluator:
    """
    Orchestrates evaluation across multiple task categories.

    The Evaluator manages the evaluation workflow, applying category-specific
    scoring functions and computing weighted overall scores.

    Attributes:
        tasks: Dictionary mapping category names to lists of tasks
        weights: Dictionary mapping category names to weight values
    """

    def __init__(
        self, tasks: Dict[str, List[Dict]], weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize the Evaluator.

        Args:
            tasks: Dictionary mapping category names to task lists
            weights: Optional dictionary of category weights (defaults to equal weighting)
        """
        self.tasks = tasks
        self.weights = weights or self._default_weights()

    def _default_weights(self) -> Dict[str, float]:
        """
        Generate default equal weights for all categories.

        Returns:
            Dictionary with equal weights summing to 1.0
        """
        num_categories = len(self.tasks)
        if num_categories == 0:
            return {}
        weight = 1.0 / num_categories
        return {cat: weight for cat in self.tasks.keys()}

    def evaluate(self, outputs: Dict[str, str]) -> Dict[str, Any]:
        """
        Evaluate model outputs across all categories.

        Args:
            outputs: Dictionary mapping task IDs to model outputs

        Returns:
            Dictionary containing:
                - overall: Weighted overall score
                - by_category: Dictionary of scores per category
                - weights: Category weights used

        Examples:
            >>> evaluator = Evaluator(tasks, weights)
            >>> results = evaluator.evaluate(outputs)
            >>> 0.0 <= results["overall"] <= 1.0
            True
        """
        category_scores = {}
        total = 0.0
        weight_sum = 0.0

        for category, tasks in self.tasks.items():
            score = score_category(category, tasks, outputs)
            category_scores[category] = score

            weight = float(self.weights.get(category, 0.0))
            total += weight * score
            weight_sum += weight

        overall = total / weight_sum if weight_sum > 0 else 0.0

        return {
            "overall": overall,
            "by_category": category_scores,
            "weights": self.weights,
        }


def evaluate(
    outputs: Dict[str, str], tasks: Dict[str, List[Dict]], weights: Dict[str, float]
) -> Dict[str, Any]:
    """
    Convenience function to evaluate outputs without creating an Evaluator instance.

    Args:
        outputs: Dictionary mapping task IDs to model outputs
        tasks: Dictionary mapping category names to task lists
        weights: Dictionary mapping category names to weight values

    Returns:
        Dictionary containing overall score, category scores, and weights

    Examples:
        >>> result = evaluate(outputs, tasks, weights)
        >>> "overall" in result
        True
        >>> "by_category" in result
        True
    """
    evaluator = Evaluator(tasks, weights)
    return evaluator.evaluate(outputs)
