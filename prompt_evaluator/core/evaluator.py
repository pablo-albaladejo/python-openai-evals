import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import openai
from jinja2 import Template
import os
from dotenv import load_dotenv

from .base import EvaluationResult, PromptVersion, Dataset, BaseEvaluator
from .config import EvaluationConfig

load_dotenv()


class PromptEvaluator:
    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.evaluators = {}
        self.results = []

    def register_evaluator(self, evaluator: BaseEvaluator):
        self.evaluators[evaluator.name] = evaluator

    async def evaluate_prompt_version(self, prompt_version: PromptVersion,
                                    dataset: Dataset) -> List[EvaluationResult]:
        results = []
        template = Template(prompt_version.template)

        for item in dataset.data:
            try:
                rendered_prompt = template.render(**item)

                response = self.client.chat.completions.create(
                    model=self.config.openai_model,
                    messages=[
                        {"role": "user", "content": rendered_prompt}
                    ],
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )

                output = response.choices[0].message.content

                scores = {}
                for evaluator_name in self.config.evaluators:
                    if evaluator_name in self.evaluators:
                        evaluator = self.evaluators[evaluator_name]
                        score = evaluator.evaluate(
                            prompt_output=output,
                            expected_output=item.get('expected', ''),
                            input_data=item
                        )
                        scores[evaluator_name] = score

                avg_score = sum(scores.values()) / len(scores) if scores else 0.0

                result = EvaluationResult(
                    prompt_version=prompt_version.name,
                    input_data=item,
                    output=output,
                    score=avg_score,
                    metadata={
                        'scores': scores,
                        'model': self.config.openai_model,
                        'temperature': self.config.temperature,
                        'max_tokens': self.config.max_tokens
                    },
                    timestamp=datetime.now()
                )

                results.append(result)

            except Exception as e:
                print(f"Error evaluating prompt {prompt_version.name}: {str(e)}")
                continue

        return results

    async def run_evaluation(self, dataset: Dataset) -> Dict[str, List[EvaluationResult]]:
        all_results = {}

        for prompt_version in self.config.prompt_versions:
            print(f"Evaluating prompt version: {prompt_version.name}")
            results = await self.evaluate_prompt_version(prompt_version, dataset)
            all_results[prompt_version.name] = results
            self.results.extend(results)

        return all_results

    def get_results_by_version(self, version_name: str) -> List[EvaluationResult]:
        return [r for r in self.results if r.prompt_version == version_name]

    def get_all_results(self) -> List[EvaluationResult]:
        return self.results