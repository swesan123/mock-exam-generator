"""Generate LaTeX exam documents."""
import logging
from pathlib import Path
from typing import List

from .models import Problem

logger = logging.getLogger(__name__)


class ExamGenerator:
    """Generates LaTeX exam documents from selected problems."""

    def __init__(self, template_path: Path) -> None:
        """
        Initialize the generator with a template path.

        Args:
            template_path: Path to the LaTeX template file.
        """
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")

    def generate_exam(self, problems: List[Problem], shuffle: bool = True) -> str:
        """
        Generate a LaTeX exam document from selected problems.

        Args:
            problems: List of Problem objects to include in the exam.
            shuffle: Whether to shuffle the order of problems.

        Returns:
            Complete LaTeX document as a string.
        """
        if not problems:
            raise ValueError("Cannot generate exam with no problems")

        # Shuffle if requested
        if shuffle:
            import random
            problems = problems.copy()
            random.Random().shuffle(problems)
            logger.info("Shuffled problem order")

        # Load template
        template = self._load_template()

        # Generate problem body
        body = self._generate_problem_body(problems)

        # Replace placeholder in template
        exam_content = template.replace("{{BODY}}", body)

        logger.info(f"Generated exam LaTeX with {len(problems)} problems")
        return exam_content

    def _load_template(self) -> str:
        """Load the LaTeX template file."""
        try:
            return self.template_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to load template: {e}")
            raise

    def _generate_problem_body(self, problems: List[Problem]) -> str:
        """
        Generate the body section with all problems.

        Args:
            problems: List of Problem objects.

        Returns:
            LaTeX-formatted problem body.
        """
        import re
        body_parts: List[str] = []

        for i, problem in enumerate(problems, start=1):
            problem_text = problem.text.strip()
            
            # Check if problem already has a subsection header
            has_subsection = re.search(r'\\subsection\*\{[^}]+\}', problem_text)
            
            if has_subsection:
                # Problem already has its own header, use it as-is
                problem_section = f"{problem_text}\n\n"
            else:
                # Add subsection header and topic
                problem_section = f"\\subsection*{{Problem {i}}}\n"
                problem_section += f"\\textbf{{Topic:}} {problem.topic}\n\n"
                problem_section += f"{problem_text}\n\n"
            
            body_parts.append(problem_section)

        return "\n".join(body_parts)

