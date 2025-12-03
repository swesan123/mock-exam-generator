"""Unit tests for LaTeX exporter."""

import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from exporter import export_exam_to_latex, export_solutions_to_latex
from models import Exam, Question


class TestExportExamToLatex:
    """Test cases for export_exam_to_latex function."""
    
    def test_export_exam_creates_file(self):
        """Test that exporting an exam creates a LaTeX file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            questions = [
                Question(id="1", topic="ODE", text="Question 1", solution="Solution 1"),
                Question(id="2", topic="Newton", text="Question 2", solution="Solution 2")
            ]
            exam = Exam(
                questions=questions,
                timestamp=datetime.now(),
                num_questions=2
            )
            
            output_path = os.path.join(tmpdir, "exam.tex")
            export_exam_to_latex(exam, output_path)
            
            assert os.path.exists(output_path)
    
    def test_export_exam_content(self):
        """Test that exported exam contains expected content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            questions = [
                Question(id="1", topic="ODE", text="Test question", solution="Test solution")
            ]
            exam = Exam(
                questions=questions,
                timestamp=datetime(2025, 1, 1, 12, 0, 0),
                num_questions=1
            )
            
            output_path = os.path.join(tmpdir, "exam.tex")
            export_exam_to_latex(exam, output_path)
            
            content = Path(output_path).read_text()
            assert "\\documentclass" in content
            assert "Mock Exam" in content
            assert "Test question" in content
            assert "Question 1" in content
            assert "ODE" in content
            assert "\\begin{document}" in content
            assert "\\end{document}" in content
    
    def test_export_exam_creates_directory(self):
        """Test that export creates parent directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            questions = [
                Question(id="1", topic="test", text="Q1", solution="S1")
            ]
            exam = Exam(
                questions=questions,
                timestamp=datetime.now(),
                num_questions=1
            )
            
            # Path with non-existent subdirectory
            output_path = os.path.join(tmpdir, "subdir", "exam.tex")
            export_exam_to_latex(exam, output_path)
            
            assert os.path.exists(output_path)


class TestExportSolutionsToLatex:
    """Test cases for export_solutions_to_latex function."""
    
    def test_export_solutions_creates_file(self):
        """Test that exporting solutions creates a LaTeX file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            questions = [
                Question(id="1", topic="ODE", text="Question 1", solution="Solution 1")
            ]
            exam = Exam(
                questions=questions,
                timestamp=datetime.now(),
                num_questions=1
            )
            
            output_path = os.path.join(tmpdir, "solutions.tex")
            export_solutions_to_latex(exam, output_path)
            
            assert os.path.exists(output_path)
    
    def test_export_solutions_content(self):
        """Test that exported solutions contain expected content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            questions = [
                Question(id="1", topic="ODE", text="Test question", solution="Test solution")
            ]
            exam = Exam(
                questions=questions,
                timestamp=datetime(2025, 1, 1, 12, 0, 0),
                num_questions=1
            )
            
            output_path = os.path.join(tmpdir, "solutions.tex")
            export_solutions_to_latex(exam, output_path)
            
            content = Path(output_path).read_text()
            assert "\\documentclass" in content
            assert "Solutions" in content
            assert "Test question" in content
            assert "Test solution" in content
            assert "Solution 1" in content
            assert "\\begin{document}" in content
            assert "\\end{document}" in content
    
    def test_export_multiple_questions(self):
        """Test exporting exam with multiple questions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            questions = [
                Question(id="1", topic="ODE", text="Q1", solution="S1"),
                Question(id="2", topic="Newton", text="Q2", solution="S2"),
                Question(id="3", topic="ODE", text="Q3", solution="S3")
            ]
            exam = Exam(
                questions=questions,
                timestamp=datetime.now(),
                num_questions=3
            )
            
            exam_path = os.path.join(tmpdir, "exam.tex")
            solutions_path = os.path.join(tmpdir, "solutions.tex")
            
            export_exam_to_latex(exam, exam_path)
            export_solutions_to_latex(exam, solutions_path)
            
            exam_content = Path(exam_path).read_text()
            solutions_content = Path(solutions_path).read_text()
            
            # Check that all questions appear
            assert "Question 1" in exam_content
            assert "Question 2" in exam_content
            assert "Question 3" in exam_content
            
            assert "Solution 1" in solutions_content
            assert "Solution 2" in solutions_content
            assert "Solution 3" in solutions_content

