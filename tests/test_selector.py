"""Tests for the question selector."""
import pytest
from core.selector import QuestionSelector
from core.models import Problem


class TestQuestionSelector:
    """Test cases for QuestionSelector."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Create sample problems
        self.topics = {
            "floating_point": [
                Problem(topic="floating_point", text="Problem 1"),
                Problem(topic="floating_point", text="Problem 2"),
            ],
            "linear_systems": [
                Problem(topic="linear_systems", text="Problem 3"),
                Problem(topic="linear_systems", text="Problem 4"),
            ],
            "integration": [
                Problem(topic="integration", text="Problem 5"),
            ],
        }

    def test_select_one_per_topic(self) -> None:
        """Test selecting exactly one question from each topic."""
        selector = QuestionSelector(self.topics, seed=42)
        selected = selector.select_questions(3)

        assert len(selected) == 3
        # Check that we have one from each topic
        topics_selected = {p.topic for p in selected}
        assert len(topics_selected) == 3
        assert topics_selected == {"floating_point", "linear_systems", "integration"}

    def test_select_extra_questions(self) -> None:
        """Test selecting more questions than topics."""
        selector = QuestionSelector(self.topics, seed=42)
        selected = selector.select_questions(5)

        assert len(selected) == 5
        # Should have at least one from each topic
        topics_selected = {p.topic for p in selected}
        assert len(topics_selected) >= 3

    def test_no_duplicates(self) -> None:
        """Test that no duplicate questions are selected."""
        selector = QuestionSelector(self.topics, seed=42)
        selected = selector.select_questions(5)

        # Check for duplicates
        selected_texts = [p.text for p in selected]
        assert len(selected_texts) == len(set(selected_texts))

    def test_select_exact_number(self) -> None:
        """Test that exactly the requested number is selected."""
        selector = QuestionSelector(self.topics, seed=42)
        for num in [1, 2, 3, 4, 5]:
            selected = selector.select_questions(num)
            assert len(selected) == num

    def test_select_invalid_number_negative(self) -> None:
        """Test that negative numbers raise ValueError."""
        selector = QuestionSelector(self.topics)
        with pytest.raises(ValueError, match="must be positive"):
            selector.select_questions(-1)

    def test_select_invalid_number_zero(self) -> None:
        """Test that zero raises ValueError."""
        selector = QuestionSelector(self.topics)
        with pytest.raises(ValueError, match="must be positive"):
            selector.select_questions(0)

    def test_select_too_many_questions(self) -> None:
        """Test that requesting more questions than available raises ValueError."""
        selector = QuestionSelector(self.topics)
        # Only 5 problems total available
        with pytest.raises(ValueError, match="only.*available"):
            selector.select_questions(10)

    def test_select_with_empty_topics(self) -> None:
        """Test selection when some topics are empty."""
        topics_with_empty = {
            "floating_point": [
                Problem(topic="floating_point", text="Problem 1"),
            ],
            "empty_topic": [],  # Empty topic
            "linear_systems": [
                Problem(topic="linear_systems", text="Problem 2"),
            ],
        }

        selector = QuestionSelector(topics_with_empty, seed=42)
        selected = selector.select_questions(2)

        assert len(selected) == 2
        topics_selected = {p.topic for p in selected}
        assert "empty_topic" not in topics_selected

    def test_select_all_available(self) -> None:
        """Test selecting all available questions."""
        selector = QuestionSelector(self.topics, seed=42)
        # Total: 2 + 2 + 1 = 5 problems
        selected = selector.select_questions(5)

        assert len(selected) == 5
        # All should be unique
        assert len(set(selected)) == 5

    def test_reproducibility_with_seed(self) -> None:
        """Test that same seed produces same results."""
        selector1 = QuestionSelector(self.topics, seed=123)
        selector2 = QuestionSelector(self.topics, seed=123)

        selected1 = selector1.select_questions(3)
        selected2 = selector2.select_questions(3)

        assert selected1 == selected2

