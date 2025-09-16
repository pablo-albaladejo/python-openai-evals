import json
import pandas as pd
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base import Dataset


class DatasetLoader:
    @staticmethod
    def load_from_json(file_path: str) -> Dataset:
        path = Path(file_path)
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        if isinstance(data, dict):
            name = data.get('name', path.stem)
            description = data.get('description', '')
            dataset_items = data.get('data', [])
        else:
            name = path.stem
            description = ''
            dataset_items = data

        return Dataset(
            name=name,
            data=dataset_items,
            description=description
        )

    @staticmethod
    def load_from_csv(file_path: str, input_column: str = 'input',
                     expected_column: str = 'expected') -> Dataset:
        path = Path(file_path)
        df = pd.read_csv(path)

        data = []
        for _, row in df.iterrows():
            item = {
                'input': row[input_column],
                'expected': row[expected_column]
            }
            for col in df.columns:
                if col not in [input_column, expected_column]:
                    item[col] = row[col]
            data.append(item)

        return Dataset(
            name=path.stem,
            data=data,
            description=f'Dataset loaded from CSV: {file_path}'
        )

    @staticmethod
    def create_from_list(name: str, data: List[Dict[str, Any]],
                        description: str = "") -> Dataset:
        return Dataset(
            name=name,
            data=data,
            description=description
        )

    @staticmethod
    def save_to_json(dataset: Dataset, file_path: str):
        data = {
            'name': dataset.name,
            'description': dataset.description,
            'data': dataset.data
        }

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)


class DatasetValidator:
    @staticmethod
    def validate_dataset(dataset: Dataset, required_fields: Optional[List[str]] = None) -> List[str]:
        errors = []
        required_fields = required_fields or ['input', 'expected']

        if not dataset.data:
            errors.append("Dataset is empty")
            return errors

        for i, item in enumerate(dataset.data):
            if not isinstance(item, dict):
                errors.append(f"Item {i} is not a dictionary")
                continue

            for field in required_fields:
                if field not in item:
                    errors.append(f"Item {i} missing required field: {field}")

        return errors