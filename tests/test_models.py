"""Unit tests for data models."""

import pytest
from datetime import datetime

from models import Question, Exam, QuestionBank


class TestQuestion:
    """Test cases for Question class."""
    
    def test_question_creation(self):
        """Test creating a valid question."""
        question = Question(
            id="test_1",
            topic="test_topic",
            text="Test question text",
            solution="Test solution"
        )
        assert question.id == "test_1"
        assert question.topic == "test_topic"
        assert question.text == "Test question text"
        assert question.solution == "Test solution"
        assert question.done is False
        assert question.last_seen is None
    
    def test_question_with_done_flag(self):
        """Test creating a question with done flag set."""
        question = Question(
            id="test_2",
            topic="test_topic",
            text="Test question",
            solution="Test solution",
            done=True
        )
        assert question.done is True
    
    def test_question_with_last_seen(self):
        """Test creating a question with last_seen timestamp."""
        now = datetime.now()
        question = Question(
            id="test_3",
            topic="test_topic",
            text="Test question",
            solution="Test solution",
            last_seen=now
        )
        assert question.last_seen == now
    
    def test_question_empty_id_raises_error(self):
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="Question ID cannot be empty"):
            Question(id="", topic="test", text="text", solution="solution")
    
    def test_question_empty_text_raises_error(self):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="Question text cannot be empty"):
            Question(id="test", topic="test", text="", solution="solution")
    
    def test_question_empty_solution_allowed(self):
        """Test that empty solution is allowed."""
        question = Question(id="test", topic="test", text="text", solution="")
        assert question.solution == ""


class TestExam:
    """Test cases for Exam class."""
    
    def test_exam_creation(self):
        """Test creating a valid exam."""
        questions = [
            Question(id="1", topic="topic1", text="Q1", solution="S1"),
            Question(id="2", topic="topic2", text="Q2", solution="S2")
        ]
        timestamp = datetime.now()
        exam = Exam(questions=questions, timestamp=timestamp, num_questions=2)
        
        assert len(exam.questions) == 2
        assert exam.num_questions == 2
        assert exam.timestamp == timestamp
    
    def test_exam_mismatched_count_raises_error(self):
        """Test that mismatched question count raises ValueError."""
        questions = [
            Question(id="1", topic="topic1", text="Q1", solution="S1")
        ]
        with pytest.raises(ValueError, match="does not match"):
            Exam(questions=questions, timestamp=datetime.now(), num_questions=2)
    
    def test_exam_empty_questions_raises_error(self):
        """Test that empty exam raises ValueError."""
        with pytest.raises(ValueError, match="must contain at least one question"):
            Exam(questions=[], timestamp=datetime.now(), num_questions=0)


class TestQuestionBank:
    """Test cases for QuestionBank class."""
    
    def test_empty_bank_creation(self):
        """Test creating an empty question bank."""
        bank = QuestionBank()
        assert bank.get_total_count() == 0
        assert bank.get_unsolved_count() == 0
        assert bank.get_solved_count() == 0
    
    def test_bank_with_questions(self):
        """Test creating a bank with initial questions."""
        questions = [
            Question(id="1", topic="topic1", text="Q1", solution="S1"),
            Question(id="2", topic="topic2", text="Q2", solution="S2")
        ]
        bank = QuestionBank(questions)
        assert bank.get_total_count() == 2
    
    def test_add_question(self):
        """Test adding a question to the bank."""
        bank = QuestionBank()
        question = Question(id="1", topic="topic1", text="Q1", solution="S1")
        bank.add_question(question)
        assert bank.get_total_count() == 1
    
    def test_add_questions(self):
        """Test adding multiple questions."""
        bank = QuestionBank()
        questions = [
            Question(id="1", topic="topic1", text="Q1", solution="S1"),
            Question(id="2", topic="topic2", text="Q2", solution="S2")
        ]
        bank.add_questions(questions)
        assert bank.get_total_count() == 2
    
    def test_add_invalid_type_raises_error(self):
        """Test that adding non-Question objects raises TypeError."""
        bank = QuestionBank()
        with pytest.raises(TypeError, match="Only Question objects"):
            bank.add_question("not a question")
    
    def test_get_unsolved_questions(self):
        """Test getting unsolved questions."""
        bank = QuestionBank()
        q1 = Question(id="1", topic="topic1", text="Q1", solution="S1", done=False)
        q2 = Question(id="2", topic="topic2", text="Q2", solution="S2", done=True)
        bank.add_questions([q1, q2])
        
        unsolved = bank.get_unsolved_questions()
        assert len(unsolved) == 1
        assert unsolved[0].id == "1"
    
    def test_get_solved_questions(self):
        """Test getting solved questions."""
        bank = QuestionBank()
        q1 = Question(id="1", topic="topic1", text="Q1", solution="S1", done=False)
        q2 = Question(id="2", topic="topic2", text="Q2", solution="S2", done=True)
        bank.add_questions([q1, q2])
        
        solved = bank.get_solved_questions()
        assert len(solved) == 1
        assert solved[0].id == "2"
    
    def test_reset_all_questions(self):
        """Test resetting all questions."""
        bank = QuestionBank()
        now = datetime.now()
        q1 = Question(id="1", topic="topic1", text="Q1", solution="S1", done=True, last_seen=now)
        q2 = Question(id="2", topic="topic2", text="Q2", solution="S2", done=True, last_seen=now)
        bank.add_questions([q1, q2])
        
        bank.reset_all_questions()
        
        assert q1.done is False
        assert q2.done is False
        assert q1.last_seen is None
        assert q2.last_seen is None
        assert bank.get_unsolved_count() == 2
    
    def test_get_questions_by_topic(self):
        """Test getting questions by topic."""
        bank = QuestionBank()
        q1 = Question(id="1", topic="ODE", text="Q1", solution="S1")
        q2 = Question(id="2", topic="ODE", text="Q2", solution="S2")
        q3 = Question(id="3", topic="Newton", text="Q3", solution="S3")
        bank.add_questions([q1, q2, q3])
        
        ode_questions = bank.get_questions_by_topic("ODE")
        assert len(ode_questions) == 2
        assert all(q.topic == "ODE" for q in ode_questions)
    
    def test_get_topics(self):
        """Test getting all unique topics."""
        bank = QuestionBank()
        q1 = Question(id="1", topic="ODE", text="Q1", solution="S1")
        q2 = Question(id="2", topic="Newton", text="Q2", solution="S2")
        q3 = Question(id="3", topic="ODE", text="Q3", solution="S3")
        bank.add_questions([q1, q2, q3])
        
        topics = bank.get_topics()
        assert len(topics) == 2
        assert "ODE" in topics
        assert "Newton" in topics
        assert topics == sorted(topics)  # Should be sorted

