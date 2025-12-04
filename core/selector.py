"""Select questions for exam generation."""
import random
import logging
from typing import List, Dict, Optional

from .models import Problem
from .persistence import ProblemTracker

logger = logging.getLogger(__name__)


class QuestionSelector:
    """Selects questions from topics for exam generation."""

    def __init__(
        self, 
        topics: Dict[str, List[Problem]], 
        seed: Optional[int] = None,
        tracker: Optional[ProblemTracker] = None,
        prefer_unused: bool = True
    ) -> None:
        """
        Initialize the selector with topics.

        Args:
            topics: Dictionary mapping topic names to lists of problems.
            seed: Optional random seed for reproducibility.
            tracker: Optional ProblemTracker to track used problems.
            prefer_unused: If True, prefer unused problems when available.
        """
        self.topics = topics
        self.seed = seed
        self.tracker = tracker
        self.prefer_unused = prefer_unused
        self._rng = random.Random(seed) if seed is not None else random
        if seed is not None:
            logger.info(f"Random seed set to: {seed}")
        if tracker:
            stats = tracker.get_stats()
            logger.info(f"Problem tracker active: {stats['total_used']} problems already used")

    def select_questions(self, num_questions: int) -> List[Problem]:
        """
        Select questions for an exam.

        Strategy:
        1. Select exactly one question from each topic
        2. If num_questions > num_topics, add extra questions randomly
        3. Ensure no duplicates

        Args:
            num_questions: Total number of questions to select.

        Returns:
            List of selected Problem objects.

        Raises:
            ValueError: If num_questions is invalid or insufficient problems available.
        """
        if num_questions <= 0:
            raise ValueError(f"Number of questions must be positive, got {num_questions}")

        # Get all available topics
        available_topics = [topic for topic, problems in self.topics.items() if problems]
        num_topics = len(available_topics)

        if num_topics == 0:
            raise ValueError("No topics with problems available")

        if num_questions > self._get_total_available_questions():
            raise ValueError(
                f"Requested {num_questions} questions, but only "
                f"{self._get_total_available_questions()} available"
            )

        selected: List[Problem] = []

        # Step 1: Select exactly one question from each topic
        for topic in available_topics:
            if len(selected) >= num_questions:
                break

            problems = self.topics[topic]
            if problems:
                # Filter to unused problems if tracker is available and prefer_unused is True
                candidate_problems = problems
                if self.tracker and self.prefer_unused:
                    unused = self.tracker.get_unused_problems(problems)
                    if unused:
                        candidate_problems = unused
                        logger.debug(f"Using {len(unused)} unused problems from topic '{topic}'")
                    else:
                        logger.warning(f"All problems in topic '{topic}' have been used, selecting from all")
                
                chosen = self._rng.choice(candidate_problems)
                selected.append(chosen)
                logger.debug(f"Selected question from topic '{topic}'")

        # Step 2: If we need more questions, add extras randomly
        while len(selected) < num_questions:
            # Choose a random topic
            topic = self._rng.choice(available_topics)
            problems = self.topics[topic]

            # Filter to unused problems if tracker is available and prefer_unused is True
            candidate_problems = problems
            if self.tracker and self.prefer_unused:
                unused = self.tracker.get_unused_problems(problems)
                if unused:
                    candidate_problems = unused

            # Choose a random problem from that topic
            candidate = self._rng.choice(candidate_problems)

            # Ensure no duplicates
            if candidate not in selected:
                selected.append(candidate)
                logger.debug(f"Selected extra question from topic '{topic}'")
            else:
                # If all problems from this topic are already selected,
                # try another topic
                if all(p in selected for p in candidate_problems):
                    continue

        logger.info(f"Selected {len(selected)} questions from {len(set(p.topic for p in selected))} topics")
        return selected

    def _get_total_available_questions(self) -> int:
        """Get total number of available questions across all topics."""
        return sum(len(problems) for problems in self.topics.values())

