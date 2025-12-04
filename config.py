"""Configuration settings for the exam generator."""
from pathlib import Path
from typing import Optional
import logging

# Directory paths (relative to project root)
PROBLEM_DIR: Path = Path("problems")
OUTPUT_DIR: Path = Path("output")
LOGS_DIR: Path = Path("logs")
TEMPLATE_DIR: Path = Path("latex")
TEMPLATE_FILE: Path = TEMPLATE_DIR / "template.tex"
TRACKER_FILE: Path = Path(".problem_tracker.json")

# LaTeX compilation settings
LATEX_COMPILER: str = "latexmk"  # or "pdflatex"
LATEX_OPTIONS: list[str] = ["-pdf", "-interaction=nonstopmode"]

# Logging configuration
LOG_LEVEL: int = logging.INFO
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# CLI settings
DEFAULT_NUM_QUESTIONS: int = 5
MAX_QUESTIONS: int = 50


def setup_logging(level: Optional[int] = None) -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=level or LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
        ]
    )

