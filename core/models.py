"""Data models for the exam generator."""
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class Problem:
    """Represents a single problem from a LaTeX file."""
    topic: str
    text: str
    file_path: Optional[Path] = None

    def __eq__(self, other: object) -> bool:
        """Check equality based on topic and text content."""
        if not isinstance(other, Problem):
            return False
        return self.topic == other.topic and self.text == other.text

    def __hash__(self) -> int:
        """Make Problem hashable for set operations."""
        return hash((self.topic, self.text))


@dataclass
class ExamConfig:
    """Configuration for exam generation."""
    num_questions: int
    shuffle: bool = True
    output_dir: Path = Path("output")
    template_path: Path = Path("latex/template.tex")
    problems_dir: Path = Path("problems")

