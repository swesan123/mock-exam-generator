"""Persistent storage for tracking used problems."""
import json
import logging
from pathlib import Path
from typing import Set, List
from datetime import datetime

from .models import Problem

logger = logging.getLogger(__name__)


class ProblemTracker:
    """Tracks which problems have been used in exams."""

    def __init__(self, storage_path: Path = Path(".problem_tracker.json")) -> None:
        """
        Initialize the problem tracker.

        Args:
            storage_path: Path to the JSON file for storing tracking data.
        """
        self.storage_path = Path(storage_path)
        self._used_problems: Set[str] = set()
        self._load()

    def _load(self) -> None:
        """Load tracking data from storage file."""
        if not self.storage_path.exists():
            logger.debug(f"Tracking file not found: {self.storage_path}, starting fresh")
            return

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._used_problems = set(data.get("used_problems", []))
                logger.info(f"Loaded {len(self._used_problems)} used problems from tracking file")
        except Exception as e:
            logger.error(f"Failed to load tracking data: {e}")
            self._used_problems = set()

    def _save(self) -> None:
        """Save tracking data to storage file."""
        try:
            data = {
                "used_problems": list(self._used_problems),
                "last_updated": datetime.now().isoformat(),
                "total_used": len(self._used_problems)
            }
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved {len(self._used_problems)} used problems to tracking file")
        except Exception as e:
            logger.error(f"Failed to save tracking data: {e}")

    def mark_as_used(self, problem: Problem) -> None:
        """
        Mark a problem as used.

        Args:
            problem: The Problem object to mark as used.
        """
        problem_id = self._get_problem_id(problem)
        if problem_id not in self._used_problems:
            self._used_problems.add(problem_id)
            self._save()
            logger.debug(f"Marked problem as used: {problem_id}")

    def mark_multiple_as_used(self, problems: List[Problem]) -> None:
        """
        Mark multiple problems as used.

        Args:
            problems: List of Problem objects to mark as used.
        """
        for problem in problems:
            self.mark_as_used(problem)

    def is_used(self, problem: Problem) -> bool:
        """
        Check if a problem has been used.

        Args:
            problem: The Problem object to check.

        Returns:
            True if the problem has been used, False otherwise.
        """
        problem_id = self._get_problem_id(problem)
        return problem_id in self._used_problems

    def get_unused_problems(self, problems: List[Problem]) -> List[Problem]:
        """
        Filter out problems that have already been used.

        Args:
            problems: List of all available problems.

        Returns:
            List of problems that haven't been used yet.
        """
        unused = [p for p in problems if not self.is_used(p)]
        logger.info(f"Filtered {len(problems)} problems: {len(unused)} unused, {len(problems) - len(unused)} used")
        return unused

    def reset(self) -> None:
        """Reset all tracking data."""
        self._used_problems.clear()
        self._save()
        logger.info("Problem tracking reset")

    def get_stats(self) -> dict:
        """
        Get tracking statistics.

        Returns:
            Dictionary with tracking statistics.
        """
        return {
            "total_used": len(self._used_problems),
            "storage_path": str(self.storage_path),
            "last_updated": datetime.now().isoformat() if self._used_problems else None
        }

    def _get_problem_id(self, problem: Problem) -> str:
        """
        Generate a unique identifier for a problem.

        Uses file path and text content hash to identify problems.

        Args:
            problem: The Problem object.

        Returns:
            Unique identifier string.
        """
        import hashlib
        
        # Use file path if available, otherwise hash the content
        if problem.file_path:
            # Include file path and a hash of the content for uniqueness
            content_hash = hashlib.md5(problem.text.encode()).hexdigest()[:8]
            return f"{problem.file_path}:{content_hash}"
        else:
            # Fallback: hash the entire content
            return hashlib.md5(problem.text.encode()).hexdigest()

