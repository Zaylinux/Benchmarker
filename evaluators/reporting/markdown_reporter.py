"""
Markdown report generation for evaluation results.

This module provides the MarkdownReporter class for generating markdown format
reports with tables from evaluation results.
"""

from pathlib import Path
from typing import Any, Dict, List, Union


class MarkdownReporter:
    """
    Generates markdown format reports from evaluation results.
    
    This class handles the generation of markdown tables and formatted reports
    for model comparison and evaluation results.
    """
    
    def __init__(self) -> None:
        """Initialize the markdown reporter."""
        pass
    
    def generate_comparison_table(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate a markdown comparison table from multiple model results.
        
        Args:
            results: List of evaluation results, each containing model performance data
        
        Returns:
            Markdown formatted string with comparison tables
        """
        lines = []
        lines.append("# Model Comparison Report\n")
        lines.append("| Model | Composite | Quality | Perf | Gen Speed (tok/s) | Prefill (tok/s) | Load (ms) |")
        lines.append("|-------|-----------|---------|------|-------------------|-----------------|-----------|")
        
        for result in results:
            if "error" in result:
                model = result["model"]
                lines.append(f"| {model} | ERROR | - | - | - | - | - |")
                continue
            
            model = result["model"]
            composite = result.get("composite_score", 0)
            quality = result.get("quality", {}).get("overall_score", 0)
            perf_score = result.get("scoring_breakdown", {}).get("performance_score", 0)
            
            perf_metrics = result.get("performance", {}).get("aggregated_metrics", {})
            gen_speed = perf_metrics.get("avg_generate_tokens_per_sec", 0)
            prefill_speed = perf_metrics.get("avg_prefill_tokens_per_sec", 0)
            load_time = perf_metrics.get("avg_load_time_ms", 0)
            
            lines.append(
                f"| {model} | {composite:.3f} | {quality:.3f} | {perf_score:.3f} | "
                f"{gen_speed:.1f} | {prefill_speed:.1f} | {load_time:.1f} |"
            )
        
        # Add category breakdown section
        lines.append("\n## Category Breakdown\n")
        lines.extend(self._generate_category_breakdown(results))
        
        # Add performance targets section
        lines.append("\n## Performance Targets\n")
        lines.extend(self._generate_performance_targets(results))
        
        return "\n".join(lines)
    
    def _generate_category_breakdown(self, results: List[Dict[str, Any]]) -> List[str]:
        """
        Generate category breakdown table rows.
        
        Args:
            results: List of evaluation results
        
        Returns:
            List of markdown table lines for category breakdown
        """
        lines = []
        
        # Get all categories
        categories = set()
        for result in results:
            if "error" not in result:
                cats = result.get("quality", {}).get("by_category", {})
                categories.update(cats.keys())
        
        if categories:
            cat_list = sorted(categories)
            header = "| Model | " + " | ".join(cat_list) + " |"
            separator = "|-------|" + "|".join(["-------"] * len(cat_list)) + "|"
            lines.append(header)
            lines.append(separator)
            
            for result in results:
                if "error" in result:
                    continue
                model = result["model"]
                cats = result.get("quality", {}).get("by_category", {})
                scores = [f"{cats.get(cat, 0):.3f}" for cat in cat_list]
                lines.append(f"| {model} | " + " | ".join(scores) + " |")
        
        return lines
    
    def _generate_performance_targets(self, results: List[Dict[str, Any]]) -> List[str]:
        """
        Generate performance targets section.
        
        Args:
            results: List of evaluation results
        
        Returns:
            List of markdown lines for performance targets
        """
        lines = []
        
        for result in results:
            if "error" in result:
                continue
            
            model = result["model"]
            checks = result.get("performance", {}).get("performance_checks", {})
            
            if checks:
                lines.append(f"\n### {model}")
                for metric, check in checks.items():
                    status = "✓" if check.get("meets_target") else "✗"
                    actual = check.get("actual", check.get("estimated", 0))
                    target = check.get("target", 0)
                    lines.append(f"- {status} {metric}: {actual:.2f} (target: {target})")
        
        return lines
    
    def generate_report(
        self,
        results: List[Dict[str, Any]],
        output_path: Union[str, Path]
    ) -> None:
        """
        Generate a markdown report and save it to a file.
        
        Args:
            results: List of evaluation results to include in the report
            output_path: Path where the markdown report should be saved
        
        Raises:
            IOError: If the file cannot be written
        """
        output_path = Path(output_path)
        
        # Ensure the output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate the markdown content
        markdown = self.generate_comparison_table(results)
        
        # Write the markdown report
        with open(output_path, "w") as f:
            f.write(markdown)
    
    def generate_single_model_report(self, result: Dict[str, Any]) -> str:
        """
        Generate a markdown report for a single model evaluation.
        
        Args:
            result: Single model evaluation result
        
        Returns:
            Markdown formatted string with model evaluation details
        """
        lines = []
        
        model = result.get("model", "Unknown")
        lines.append(f"# Evaluation Report: {model}\n")
        
        if "error" in result:
            lines.append(f"**Error**: {result['error']}\n")
            return "\n".join(lines)
        
        # Overall scores
        lines.append("## Overall Scores\n")
        composite = result.get("composite_score", 0)
        quality = result.get("quality", {}).get("overall_score", 0)
        perf_score = result.get("scoring_breakdown", {}).get("performance_score", 0)
        
        lines.append(f"- **Composite Score**: {composite:.3f}")
        lines.append(f"- **Quality Score**: {quality:.3f}")
        lines.append(f"- **Performance Score**: {perf_score:.3f}\n")
        
        # Category scores
        lines.append("## Category Scores\n")
        cats = result.get("quality", {}).get("by_category", {})
        for category, score in sorted(cats.items()):
            lines.append(f"- **{category}**: {score:.3f}")
        
        # Performance metrics
        lines.append("\n## Performance Metrics\n")
        perf_metrics = result.get("performance", {}).get("aggregated_metrics", {})
        if perf_metrics:
            gen_speed = perf_metrics.get("avg_generate_tokens_per_sec", 0)
            prefill_speed = perf_metrics.get("avg_prefill_tokens_per_sec", 0)
            load_time = perf_metrics.get("avg_load_time_ms", 0)
            
            lines.append(f"- **Generation Speed**: {gen_speed:.1f} tokens/sec")
            lines.append(f"- **Prefill Speed**: {prefill_speed:.1f} tokens/sec")
            lines.append(f"- **Load Time**: {load_time:.1f} ms")
        
        # Performance targets
        checks = result.get("performance", {}).get("performance_checks", {})
        if checks:
            lines.append("\n## Performance Targets\n")
            for metric, check in checks.items():
                status = "✓" if check.get("meets_target") else "✗"
                actual = check.get("actual", check.get("estimated", 0))
                target = check.get("target", 0)
                lines.append(f"- {status} **{metric}**: {actual:.2f} (target: {target})")
        
        return "\n".join(lines)
