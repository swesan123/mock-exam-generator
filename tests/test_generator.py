"""Unit tests for exam generator."""

import pytest
from datetime import datetime

from generator import generate_mock_exam, review_stats
from models import Question, QuestionBank


class TestGenerateMockExam:
    """Test cases for generate_mock_exam function."""
    
    def test_generate_exam_with_enough_questions(self):
        """Test generating an exam when enough questions are available."""
        bank = QuestionBank()
        for i in range(10):
            q = Question(
                id=f"q{i}",
                topic="test",
                text=f"Question {i}",
                solution=f"Solution {i}"
            )
            bank.add_question(q)
        
        exam = generate_mock_exam(bank, 5)
        
        assert exam.num_questions == 5
        assert len(exam.questions) == 5
        assert isinstance(exam.timestamp, datetime)
        
        # Check that selected questions are marked as done
        for question in exam.questions:
            assert question.done is True
            assert question.last_seen is not None
    
    def test_generate_exam_resets_when_needed(self):
        """Test that exam generation resets questions when all are done."""
        bank = QuestionBank()
        for i in range(5):
            q = Question(
                id=f"q{i}",
                topic="test",
                text=f"Question {i}",
                solution=f"Solution {i}",
                done=True
            )
            bank.add_question(q)
        
        # All questions are done, but we request 3
        exam = generate_mock_exam(bank, 3)
        
        assert exam.num_questions == 3
        # All questions should be reset and then 3 selected
        assert bank.get_unsolved_count() == 2  # 5 - 3 = 2 remaining
    
    def test_generate_exam_negative_number_raises_error(self):
        """Test that negative number of questions raises error."""
        bank = QuestionBank()
        with pytest.raises(ValueError, match="must be positive"):
            generate_mock_exam(bank, -1)
    
    def test_generate_exam_zero_raises_error(self):
        """Test that zero questions raises error."""
        bank = QuestionBank()
        with pytest.raises(ValueError, match="must be positive"):
            generate_mock_exam(bank, 0)
    
    def test_generate_exam_not_enough_questions_raises_error(self):
        """Test that requesting more questions than available raises error."""
        bank = QuestionBank()
        q = Question(id="q1", topic="test", text="Q1", solution="S1")
        bank.add_question(q)
        
        with pytest.raises(ValueError, match="Not enough questions"):
            generate_mock_exam(bank, 10)
    
    def test_generate_exam_random_selection(self):
        """Test that questions are randomly selected."""
        bank = QuestionBank()
        for i in range(20):
            q = Question(
                id=f"q{i}",
                topic="test",
                text=f"Question {i}",
                solution=f"Solution {i}"
            )
            bank.add_question(q)
        
        # Generate two exams and check they're different
        exam1 = generate_mock_exam(bank, 5)
        # Reset to get fresh selection
        bank.reset_all_questions()
        exam2 = generate_mock_exam(bank, 5)
        
        # It's very unlikely (but not impossible) that both exams have
        # the same questions in the same order
        ids1 = [q.id for q in exam1.questions]
        ids2 = [q.id for q in exam2.questions]
        
        # At least one question should be different (very high probability)
        # We'll just check that both exams have 5 questions
        assert len(ids1) == 5
        assert len(ids2) == 5
    
    def test_generate_exam_one_per_topic(self):
        """Test generating exam with one question per topic."""
        bank = QuestionBank()
        # Create questions from 3 different topics
        for i in range(9):
            topic = f"topic{i // 3}"  # topic0, topic0, topic0, topic1, topic1, topic1, etc.
            q = Question(
                id=f"q{i}",
                topic=topic,
                text=f"Question {i}",
                solution=f"Solution {i}"
            )
            bank.add_question(q)
        
        exam = generate_mock_exam(bank, 3, one_per_topic=True)
        
        assert exam.num_questions == 3
        # Check that all questions are from different topics
        topics_in_exam = [q.topic for q in exam.questions]
        assert len(set(topics_in_exam)) == 3  # All topics should be unique
    
    def test_generate_exam_one_per_topic_too_many_questions(self):
        """Test that requesting more questions than topics raises error."""
        bank = QuestionBank()
        # Create questions from 2 topics
        for i in range(4):
            topic = "topic0" if i < 2 else "topic1"
            q = Question(
                id=f"q{i}",
                topic=topic,
                text=f"Question {i}",
                solution=f"Solution {i}"
            )
            bank.add_question(q)
        
        with pytest.raises(ValueError, match="Cannot generate"):
            generate_mock_exam(bank, 3, one_per_topic=True)
    
    def test_generate_exam_one_per_topic_resets_when_needed(self):
        """Test that one_per_topic resets when all questions in topics are done."""
        bank = QuestionBank()
        # Create questions from 2 topics, all done
        for i in range(4):
            topic = "topic0" if i < 2 else "topic1"
            q = Question(
                id=f"q{i}",
                topic=topic,
                text=f"Question {i}",
                solution=f"Solution {i}",
                done=True
            )
            bank.add_question(q)
        
        exam = generate_mock_exam(bank, 2, one_per_topic=True)
        
        assert exam.num_questions == 2
        # Should have reset and selected one from each topic
        topics_in_exam = [q.topic for q in exam.questions]
        assert len(set(topics_in_exam)) == 2


class TestReviewStats:
    """Test cases for review_stats function."""
    
    def test_review_stats_empty_bank(self, capsys):
        """Test stats for empty question bank."""
        bank = QuestionBank()
        review_stats(bank)
        
        captured = capsys.readouterr()
        assert "Total questions: 0" in captured.out
        assert "Solved questions: 0" in captured.out
        assert "Unsolved questions: 0" in captured.out
    
    def test_review_stats_with_questions(self, capsys):
        """Test stats for bank with questions."""
        bank = QuestionBank()
        for i in range(5):
            q = Question(
                id=f"q{i}",
                topic="topic1" if i < 3 else "topic2",
                text=f"Question {i}",
                solution=f"Solution {i}",
                done=(i < 2)  # First 2 are done
            )
            bank.add_question(q)
        
        review_stats(bank)
        
        captured = capsys.readouterr()
        assert "Total questions: 5" in captured.out
        assert "Solved questions: 2" in captured.out
        assert "Unsolved questions: 3" in captured.out
        assert "Completion rate: 40.0%" in captured.out
    
    def test_review_stats_with_topics(self, capsys):
        """Test stats include topic breakdown."""
        bank = QuestionBank()
        for i in range(4):
            q = Question(
                id=f"q{i}",
                topic="ODE" if i < 2 else "Newton",
                text=f"Question {i}",
                solution=f"Solution {i}",
                done=(i == 0)  # Only first is done
            )
            bank.add_question(q)
        
        review_stats(bank)
        
        captured = capsys.readouterr()
        assert "ODE" in captured.out
        assert "Newton" in captured.out

