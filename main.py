#!/usr/bin/env python3
import asyncio
import click
from pathlib import Path

from prompt_evaluator.core.config import ConfigLoader
from prompt_evaluator.core.dataset import DatasetLoader
from prompt_evaluator.core.evaluator import PromptEvaluator
from prompt_evaluator.evaluators.basic import (
    ExactMatchEvaluator, ContainsEvaluator, SimilarityEvaluator
)
from prompt_evaluator.reports.generator import ReportGenerator


@click.command()
@click.option('--config', '-c', required=True, help='Path to configuration YAML file')
@click.option('--output', '-o', default='results', help='Output directory for results')
@click.option('--report-name', '-n', help='Name for the generated report')
def main(config: str, output: str, report_name: str):
    """
    Run prompt evaluation based on configuration file.

    Example:
        python main.py -c examples/example_config.yaml -o results
    """
    try:
        # Load configuration
        print(f"Loading configuration from: {config}")
        eval_config = ConfigLoader.load_from_yaml(config)

        # Load dataset
        print(f"Loading dataset from: {eval_config.dataset_path}")
        dataset = DatasetLoader.load_from_json(eval_config.dataset_path)
        print(f"Dataset loaded: {len(dataset.data)} items")

        # Initialize evaluator
        evaluator = PromptEvaluator(eval_config)

        # Register default evaluators
        evaluator.register_evaluator(ExactMatchEvaluator())
        evaluator.register_evaluator(ContainsEvaluator())
        evaluator.register_evaluator(SimilarityEvaluator())

        # Run evaluation
        print("Starting evaluation...")
        results = asyncio.run(evaluator.run_evaluation(dataset))

        # Generate reports
        print("Generating reports...")
        report_gen = ReportGenerator(output)
        report_path = report_gen.generate_comparison_report(results, report_name)

        print(f"\nEvaluation completed!")
        print(f"Reports generated in: {output}")
        print(f"Main report: {report_path}")

    except Exception as e:
        print(f"Error during evaluation: {str(e)}")
        raise click.ClickException(str(e))


if __name__ == '__main__':
    main()