import json
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from ..core.base import EvaluationResult
from ..metrics.basic import ComparisonMetric, ScoreDistributionMetric, SuccessRateMetric


class ReportGenerator:
    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.console = Console()

    def generate_comparison_report(self, results_dict: Dict[str, List[EvaluationResult]],
                                 report_name: str = None) -> str:
        if not report_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"comparison_report_{timestamp}"

        comparison_metric = ComparisonMetric()
        comparison_data = comparison_metric.calculate_comparison(results_dict)

        # Generate console report
        self._print_console_report(comparison_data, results_dict)

        # Generate JSON report
        json_path = self.output_dir / f"{report_name}.json"
        self._generate_json_report(comparison_data, results_dict, str(json_path))

        # Generate CSV report
        csv_path = self.output_dir / f"{report_name}.csv"
        self._generate_csv_report(results_dict, str(csv_path))

        # Generate HTML report
        html_path = self.output_dir / f"{report_name}.html"
        self._generate_html_report(comparison_data, results_dict, str(html_path))

        return str(json_path)

    def _print_console_report(self, comparison_data: Dict, results_dict: Dict[str, List[EvaluationResult]]):
        # Create comparison table
        table = Table(title="Prompt Version Comparison", box=box.ROUNDED)
        table.add_column("Version", style="cyan", no_wrap=True)
        table.add_column("Avg Score", justify="right")
        table.add_column("Std Dev", justify="right")
        table.add_column("Count", justify="right")
        table.add_column("Min", justify="right")
        table.add_column("Max", justify="right")
        table.add_column("Relative Performance", justify="right")
        table.add_column("Status", justify="center")

        for version, metrics in comparison_data.items():
            status = "🏆 BEST" if metrics.get("is_best", False) else ""
            table.add_row(
                version,
                f"{metrics['average_score']:.3f}",
                f"{metrics['std']:.3f}",
                str(metrics['count']),
                f"{metrics['min']:.3f}",
                f"{metrics['max']:.3f}",
                f"{metrics['relative_performance']:.1%}",
                status
            )

        self.console.print(table)

        # Print detailed metrics for each version
        for version, results in results_dict.items():
            if not results:
                continue

            distribution_metric = ScoreDistributionMetric()
            success_metric = SuccessRateMetric()

            dist_stats = distribution_metric.calculate(results)
            success_stats = success_metric.calculate(results)

            panel_content = f"""
Average Score: {dist_stats['mean']:.3f}
Success Rate (≥0.8): {success_stats['success_rate']:.1%} ({success_stats['successful_count']}/{success_stats['total_count']})
Score Range: {dist_stats['min']:.3f} - {dist_stats['max']:.3f}
Median: {dist_stats['median']:.3f}
25th-75th Percentile: {dist_stats['percentile_25']:.3f} - {dist_stats['percentile_75']:.3f}
"""
            self.console.print(Panel(panel_content, title=f"Details: {version}", expand=False))

    def _generate_json_report(self, comparison_data: Dict, results_dict: Dict[str, List[EvaluationResult]],
                            file_path: str):
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "comparison": comparison_data,
            "detailed_results": {}
        }

        for version, results in results_dict.items():
            report_data["detailed_results"][version] = [
                {
                    "input": result.input_data,
                    "output": result.output,
                    "score": result.score,
                    "metadata": result.metadata,
                    "timestamp": result.timestamp.isoformat()
                }
                for result in results
            ]

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

    def _generate_csv_report(self, results_dict: Dict[str, List[EvaluationResult]], file_path: str):
        all_data = []
        for version, results in results_dict.items():
            for result in results:
                row = {
                    "prompt_version": result.prompt_version,
                    "score": result.score,
                    "output": result.output,
                    "timestamp": result.timestamp.isoformat(),
                    "model": result.metadata.get("model", ""),
                    "temperature": result.metadata.get("temperature", ""),
                }

                # Add input data fields
                for key, value in result.input_data.items():
                    row[f"input_{key}"] = value

                all_data.append(row)

        df = pd.DataFrame(all_data)
        df.to_csv(file_path, index=False)

    def _generate_html_report(self, comparison_data: Dict, results_dict: Dict[str, List[EvaluationResult]],
                            file_path: str):
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Prompt Evaluation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .best {{ background-color: #d4edda; }}
        .metrics {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>Prompt Evaluation Report</h1>
    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <h2>Comparison Summary</h2>
    <table>
        <tr>
            <th>Version</th>
            <th>Average Score</th>
            <th>Standard Deviation</th>
            <th>Count</th>
            <th>Min Score</th>
            <th>Max Score</th>
            <th>Relative Performance</th>
        </tr>
"""

        for version, metrics in comparison_data.items():
            row_class = "best" if metrics.get("is_best", False) else ""
            html_content += f"""
        <tr class="{row_class}">
            <td>{version}</td>
            <td>{metrics['average_score']:.3f}</td>
            <td>{metrics['std']:.3f}</td>
            <td>{metrics['count']}</td>
            <td>{metrics['min']:.3f}</td>
            <td>{metrics['max']:.3f}</td>
            <td>{metrics['relative_performance']:.1%}</td>
        </tr>
"""

        html_content += """
    </table>

    <h2>Detailed Results</h2>
"""

        for version, results in results_dict.items():
            if not results:
                continue

            html_content += f"""
    <h3>{version}</h3>
    <div class="metrics">
        <strong>Sample Results:</strong>
    </div>
    <table>
        <tr>
            <th>Input</th>
            <th>Output</th>
            <th>Score</th>
        </tr>
"""
            # Show first 5 results as examples
            for result in results[:5]:
                input_text = str(result.input_data.get('input', ''))[:100] + '...' if len(str(result.input_data.get('input', ''))) > 100 else str(result.input_data.get('input', ''))
                output_text = result.output[:100] + '...' if len(result.output) > 100 else result.output

                html_content += f"""
        <tr>
            <td>{input_text}</td>
            <td>{output_text}</td>
            <td>{result.score:.3f}</td>
        </tr>
"""

            html_content += """
    </table>
"""

        html_content += """
</body>
</html>
"""

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)