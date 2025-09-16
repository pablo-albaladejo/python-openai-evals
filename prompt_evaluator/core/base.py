from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class EvaluationResult:
    prompt_version: str
    input_data: Dict[str, Any]
    output: str
    score: float
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class PromptVersion:
    name: str
    template: str
    variables: List[str]
    description: Optional[str] = None


@dataclass
class Dataset:
    name: str
    data: List[Dict[str, Any]]
    description: Optional[str] = None


class BaseEvaluator(ABC):
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    def evaluate(self, prompt_output: str, expected_output: str, **kwargs) -> float:
        pass


class BaseMetric(ABC):
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    def calculate(self, results: List[EvaluationResult]) -> Dict[str, float]:
        pass