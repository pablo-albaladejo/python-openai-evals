import yaml
from typing import Dict, Any, List
from pathlib import Path
from dataclasses import dataclass, field

from .base import PromptVersion, Dataset


@dataclass
class EvaluationConfig:
    name: str
    description: str = ""
    prompt_versions: List[PromptVersion] = field(default_factory=list)
    dataset_path: str = ""
    evaluators: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    openai_model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    output_dir: str = "results"


class ConfigLoader:
    @staticmethod
    def load_from_yaml(config_path: str) -> EvaluationConfig:
        with open(config_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)

        prompt_versions = []
        for pv_data in data.get('prompt_versions', []):
            prompt_versions.append(PromptVersion(
                name=pv_data['name'],
                template=pv_data['template'],
                variables=pv_data.get('variables', []),
                description=pv_data.get('description')
            ))

        return EvaluationConfig(
            name=data['name'],
            description=data.get('description', ''),
            prompt_versions=prompt_versions,
            dataset_path=data.get('dataset_path', ''),
            evaluators=data.get('evaluators', []),
            metrics=data.get('metrics', []),
            openai_model=data.get('openai_model', 'gpt-3.5-turbo'),
            max_tokens=data.get('max_tokens', 1000),
            temperature=data.get('temperature', 0.7),
            output_dir=data.get('output_dir', 'results')
        )

    @staticmethod
    def save_to_yaml(config: EvaluationConfig, config_path: str):
        data = {
            'name': config.name,
            'description': config.description,
            'prompt_versions': [
                {
                    'name': pv.name,
                    'template': pv.template,
                    'variables': pv.variables,
                    'description': pv.description
                } for pv in config.prompt_versions
            ],
            'dataset_path': config.dataset_path,
            'evaluators': config.evaluators,
            'metrics': config.metrics,
            'openai_model': config.openai_model,
            'max_tokens': config.max_tokens,
            'temperature': config.temperature,
            'output_dir': config.output_dir
        }

        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, default_flow_style=False, allow_unicode=True)