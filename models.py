"""Data models for the Mock Exam Generator."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Question:
    """Represents a single question in the question bank."""
    
    id: str
    topic: str
    text: str
    solution: str
    done: bool = False
    last_seen: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate question data after initialization."""
        if not self.id:
            raise ValueError("Question ID cannot be empty")
        if not self.text:
            raise ValueError("Question text cannot be empty")
        # Solution can be empty (some questions may not have solutions yet)


@dataclass
class Exam:
    """Represents a generated mock exam."""
    
    questions: List[Question]
    timestamp: datetime
    num_questions: int
    
    def __post_init__(self):
        """Validate exam data after initialization."""
        if self.num_questions != len(self.questions):
            raise ValueError(
                f"Number of questions ({len(self.questions)}) "
                f"does not match num_questions ({self.num_questions})"
            )
        if self.num_questions == 0:
            raise ValueError("Exam must contain at least one question")


class QuestionBank:
    """Manages a collection of questions."""
    
    def __init__(self, questions: Optional[List[Question]] = None):
        """Initialize the question bank with optional questions."""
        self._questions: List[Question] = questions if questions else []
    
    def add_question(self, question: Question) -> None:
        """Add a question to the bank."""
        if not isinstance(question, Question):
            raise TypeError("Only Question objects can be added to the bank")
        self._questions.append(question)
    
    def add_questions(self, questions: List[Question]) -> None:
        """Add multiple questions to the bank."""
        for question in questions:
            self.add_question(question)
    
    def get_all_questions(self) -> List[Question]:
        """Get all questions in the bank."""
        return self._questions.copy()
    
    def get_unsolved_questions(self) -> List[Question]:
        """Get all questions that are not marked as done."""
        return [q for q in self._questions if not q.done]
    
    def get_solved_questions(self) -> List[Question]:
        """Get all questions that are marked as done."""
        return [q for q in self._questions if q.done]
    
    def reset_all_questions(self) -> None:
        """Reset all questions to not done and clear last_seen."""
        for question in self._questions:
            question.done = False
            question.last_seen = None
    
    def get_questions_by_topic(self, topic: str) -> List[Question]:
        """Get all questions for a specific topic."""
        return [q for q in self._questions if q.topic == topic]
    
    def get_total_count(self) -> int:
        """Get the total number of questions."""
        return len(self._questions)
    
    def get_solved_count(self) -> int:
        """Get the number of solved questions."""
        return len(self.get_solved_questions())
    
    def get_unsolved_count(self) -> int:
        """Get the number of unsolved questions."""
        return len(self.get_unsolved_questions())
    
    def get_topics(self) -> List[str]:
        """Get a list of all unique topics."""
        return sorted(list(set(q.topic for q in self._questions)))

