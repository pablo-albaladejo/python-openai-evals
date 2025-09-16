"""
Utility class to capture and save output to both console and file
"""
import sys
from pathlib import Path


class TeeOutput:
    """Class that writes to both stdout and a file simultaneously"""

    def __init__(self, file_path, mode='w'):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file = open(self.file_path, mode, encoding='utf-8')
        self.stdout = sys.stdout

    def write(self, message):
        self.stdout.write(message)
        self.file.write(message)
        self.file.flush()  # Ensure immediate write

    def flush(self):
        self.stdout.flush()
        self.file.flush()

    def close(self):
        if hasattr(self, 'file') and self.file:
            self.file.close()

    def __enter__(self):
        sys.stdout = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.stdout
        self.close()