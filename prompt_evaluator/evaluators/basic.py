import re
from typing import Dict, Any
from difflib import SequenceMatcher

from ..core.base import BaseEvaluator


class ExactMatchEvaluator(BaseEvaluator):
    def __init__(self):
        super().__init__(
            name="exact_match",
            description="Evaluates if the output exactly matches the expected result"
        )

    def evaluate(self, prompt_output: str, expected_output: str, **kwargs) -> float:
        return 1.0 if prompt_output.strip() == expected_output.strip() else 0.0


class ContainsEvaluator(BaseEvaluator):
    def __init__(self):
        super().__init__(
            name="contains",
            description="Evaluates if the output contains the expected result"
        )

    def evaluate(self, prompt_output: str, expected_output: str, **kwargs) -> float:
        return 1.0 if expected_output.lower() in prompt_output.lower() else 0.0


class SimilarityEvaluator(BaseEvaluator):
    def __init__(self, threshold: float = 0.8):
        super().__init__(
            name="similarity",
            description=f"Evaluates similarity between output and expected (threshold: {threshold})"
        )
        self.threshold = threshold

    def evaluate(self, prompt_output: str, expected_output: str, **kwargs) -> float:
        similarity = SequenceMatcher(None, prompt_output.strip(), expected_output.strip()).ratio()
        return similarity


class RegexEvaluator(BaseEvaluator):
    def __init__(self, pattern: str):
        super().__init__(
            name="regex",
            description=f"Evaluates if output matches regex pattern: {pattern}"
        )
        self.pattern = re.compile(pattern)

    def evaluate(self, prompt_output: str, expected_output: str, **kwargs) -> float:
        return 1.0 if self.pattern.search(prompt_output) else 0.0


class LengthEvaluator(BaseEvaluator):
    def __init__(self, min_length: int = 0, max_length: int = float('inf')):
        super().__init__(
            name="length",
            description=f"Evaluates if output length is between {min_length} and {max_length}"
        )
        self.min_length = min_length
        self.max_length = max_length

    def evaluate(self, prompt_output: str, expected_output: str, **kwargs) -> float:
        length = len(prompt_output)
        if self.min_length <= length <= self.max_length:
            return 1.0
        return 0.0


class JSONValidityEvaluator(BaseEvaluator):
    def __init__(self):
        super().__init__(
            name="json_validity",
            description="Evaluates if the output is valid JSON"
        )

    def evaluate(self, prompt_output: str, expected_output: str, **kwargs) -> float:
        import json
        try:
            json.loads(prompt_output)
            return 1.0
        except json.JSONDecodeError:
            return 0.0