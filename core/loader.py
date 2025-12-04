"""Load LaTeX problems from directory structure."""
import logging
import re
from pathlib import Path
from typing import Dict, List

from .models import Problem

logger = logging.getLogger(__name__)


class ProblemLoader:
    """Loads LaTeX problems from the problems directory."""

    def __init__(self, base_dir: Path) -> None:
        """Initialize the loader with a base directory."""
        self.base_dir = Path(base_dir)
        if not self.base_dir.exists():
            raise FileNotFoundError(f"Problems directory not found: {self.base_dir}")

    def load_all_problems(self) -> Dict[str, List[Problem]]:
        """
        Load all problems from the problems directory (flat structure).

        Returns:
            Dictionary mapping topic names to lists of Problem objects.
            All problems are grouped under a single "problems" topic.
        """
        topics: Dict[str, List[Problem]] = {}
        default_topic = "problems"

        if not self.base_dir.exists():
            logger.warning(f"Base directory does not exist: {self.base_dir}")
            return topics

        # Find all .tex files directly in the problems directory
        tex_files = list(self.base_dir.glob("*.tex"))
        logger.info(f"Found {len(tex_files)} .tex files in problems directory")

        topics[default_topic] = []

        for tex_file in sorted(tex_files):
            try:
                problems = self._load_problems_from_file(default_topic, tex_file)
                topics[default_topic].extend(problems)
                if problems:
                    logger.debug(f"Loaded {len(problems)} problem(s) from {tex_file.name}")
            except Exception as e:
                logger.error(f"Error loading {tex_file}: {e}")

        total_problems = len(topics[default_topic])
        logger.info(f"Total problems loaded: {total_problems} from {len(tex_files)} files")
        return topics

    def _load_problems_from_file(self, topic: str, file_path: Path) -> List[Problem]:
        """
        Load problems from a LaTeX file.
        
        Supports both:
        - Single problem files (entire file is one problem)
        - Multi-problem files (problems separated by \subsection*{Problem X} or similar)

        Args:
            topic: The topic name for these problems.
            file_path: Path to the .tex file.

        Returns:
            List of Problem objects (may be empty or contain multiple problems).
        """
        try:
            text = file_path.read_text(encoding="utf-8").strip()
            if not text:
                logger.warning(f"Empty file: {file_path}")
                return []

            # Try to split by common problem markers
            problems = self._extract_multiple_problems(text, topic, file_path)
            
            # If no problems found with markers, treat entire file as one problem
            if not problems:
                return [Problem(
                    topic=topic,
                    text=text,
                    file_path=file_path
                )]
            
            return problems
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            raise

    def _extract_multiple_problems(
        self, 
        text: str, 
        topic: str, 
        file_path: Path
    ) -> List[Problem]:
        """
        Extract multiple problems from LaTeX text.
        
        Looks for patterns like:
        - \subsection*{Problem X}
        - \section*{Problem X}
        - \problem
        - \begin{problem}
        
        Args:
            text: LaTeX content
            topic: Topic name
            file_path: Source file path
            
        Returns:
            List of Problem objects
        """
        problems: List[Problem] = []
        
        # Pattern to match problem sections
        # Matches: \subsection*{Problem X}, \section*{Problem X}, etc.
        # Also handles variations like \subsection*{Problem 1 — Title}
        pattern = r'\\subsection\*\{[^}]+\}|\\section\*\{[^}]+\}|\\problem\b|\\begin\{problem\}'
        
        # Find all problem markers
        matches = list(re.finditer(pattern, text))
        
        if len(matches) <= 1:
            # Only one or no markers found, treat as single problem
            return []
        
        # Extract problems between markers
        for i, match in enumerate(matches):
            start_pos = match.start()
            
            # Find end position (start of next problem or end of text)
            if i + 1 < len(matches):
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(text)
            
            # Extract problem text
            problem_text = text[start_pos:end_pos].strip()
            
            if problem_text:
                problems.append(Problem(
                    topic=topic,
                    text=problem_text,
                    file_path=file_path
                ))
        
        return problems

