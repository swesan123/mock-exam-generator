"""Unit tests for LaTeX parser."""

import os
import tempfile
from pathlib import Path

import pytest

from models import Question
from parser import load_questions_from_latex, parse_latex_questions


class TestParseLatexQuestions:
    """Test cases for parse_latex_questions function."""
    
    def test_parse_single_question(self):
        """Test parsing a single problem/solution pair."""
        latex_text = """
        \\begin{problem}
        Solve the equation x + 1 = 0.
        \\end{problem}
        
        \\begin{solution}
        x = -1
        \\end{solution}
        """
        
        questions = parse_latex_questions(latex_text, topic="test")
        
        assert len(questions) == 1
        assert questions[0].topic == "test"
        assert "x + 1 = 0" in questions[0].text
        assert "x = -1" in questions[0].solution
        assert questions[0].id == "test_1"
    
    def test_parse_multiple_questions(self):
        """Test parsing multiple problem/solution pairs."""
        latex_text = """
        \\begin{problem}
        Question 1
        \\end{problem}
        \\begin{solution}
        Solution 1
        \\end{solution}
        
        \\begin{problem}
        Question 2
        \\end{problem}
        \\begin{solution}
        Solution 2
        \\end{solution}
        """
        
        questions = parse_latex_questions(latex_text, topic="test")
        
        assert len(questions) == 2
        assert questions[0].id == "test_1"
        assert questions[1].id == "test_2"
        assert "Question 1" in questions[0].text
        assert "Question 2" in questions[1].text
    
    def test_parse_question_without_solution(self):
        """Test parsing a question without a solution."""
        latex_text = """
        \\begin{problem}
        Question without solution
        \\end{problem}
        """
        
        questions = parse_latex_questions(latex_text, topic="test")
        
        assert len(questions) == 1
        assert questions[0].solution == ""
    
    def test_parse_empty_text(self):
        """Test parsing empty LaTeX text."""
        questions = parse_latex_questions("", topic="test")
        assert len(questions) == 0
    
    def test_parse_with_multiline_content(self):
        """Test parsing questions with multiline content."""
        latex_text = """
        \\begin{problem}
        This is a multi-line
        question with
        multiple lines.
        \\end{problem}
        \\begin{solution}
        This is a multi-line
        solution with
        multiple lines.
        \\end{solution}
        """
        
        questions = parse_latex_questions(latex_text, topic="test")
        
        assert len(questions) == 1
        assert "multi-line" in questions[0].text
        assert "multi-line" in questions[0].solution
    
    def test_parse_subsection_format_single_question(self):
        """Test parsing subsection format with single problem and solution."""
        latex_text = """
        \\subsection*{Problem 1 — Test Problem}
        Solve the equation x + 1 = 0.
        
        \\section*{Solutions}
        \\subsection*{Solution 1}
        x = -1
        """
        
        questions = parse_latex_questions(latex_text, topic="test")
        
        assert len(questions) == 1
        assert questions[0].topic == "test"
        assert questions[0].id == "test_1"
        assert "x + 1 = 0" in questions[0].text
        assert "x = -1" in questions[0].solution
    
    def test_parse_subsection_format_multiple_questions(self):
        """Test parsing subsection format with multiple problems and solutions."""
        latex_text = """
        \\subsection*{Problem 1}
        Question 1 text
        
        \\subsection*{Problem 2}
        Question 2 text
        
        \\section*{Solutions}
        \\subsection*{Solution 1}
        Solution 1 text
        
        \\subsection*{Solution 2}
        Solution 2 text
        """
        
        questions = parse_latex_questions(latex_text, topic="test")
        
        assert len(questions) == 2
        assert questions[0].id == "test_1"
        assert questions[1].id == "test_2"
        assert "Question 1" in questions[0].text
        assert "Question 2" in questions[1].text
        assert "Solution 1" in questions[0].solution
        assert "Solution 2" in questions[1].solution
    
    def test_parse_subsection_format_missing_solution(self):
        """Test parsing subsection format where a problem has no solution."""
        latex_text = """
        \\subsection*{Problem 1}
        Question 1 text
        
        \\subsection*{Problem 2}
        Question 2 text
        
        \\section*{Solutions}
        \\subsection*{Solution 1}
        Solution 1 text
        """
        
        questions = parse_latex_questions(latex_text, topic="test")
        
        assert len(questions) == 2
        assert questions[0].solution != ""
        assert questions[1].solution == ""  # Problem 2 has no solution
    
    def test_parse_subsection_format_with_title(self):
        """Test parsing subsection format with problem titles."""
        latex_text = """
        \\subsection*{Problem 1 — First Problem}
        Question text here
        
        \\section*{Solutions}
        \\subsection*{Solution 1}
        Solution text here
        """
        
        questions = parse_latex_questions(latex_text, topic="test")
        
        assert len(questions) == 1
        assert questions[0].id == "test_1"
        assert "Question text here" in questions[0].text


class TestLoadQuestionsFromLatex:
    """Test cases for load_questions_from_latex function."""
    
    def test_load_from_single_file(self):
        """Test loading questions from a single file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test LaTeX file
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text("""
            \\begin{problem}
            Test question
            \\end{problem}
            \\begin{solution}
            Test solution
            \\end{solution}
            """)
            
            questions = load_questions_from_latex(tmpdir)
            
            assert len(questions) == 1
            assert questions[0].topic == "test"
            assert isinstance(questions[0], Question)
    
    def test_load_from_multiple_files(self):
        """Test loading questions from multiple files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple test files
            file1 = Path(tmpdir) / "ODE.tex"
            file1.write_text("""
            \\begin{problem}
            ODE question
            \\end{problem}
            \\begin{solution}
            ODE solution
            \\end{solution}
            """)
            
            file2 = Path(tmpdir) / "Newton.tex"
            file2.write_text("""
            \\begin{problem}
            Newton question
            \\end{problem}
            \\begin{solution}
            Newton solution
            \\end{solution}
            """)
            
            questions = load_questions_from_latex(tmpdir)
            
            assert len(questions) == 2
            topics = [q.topic for q in questions]
            assert "ODE" in topics
            assert "Newton" in topics
    
    def test_load_nonexistent_folder_raises_error(self):
        """Test that loading from nonexistent folder raises error."""
        with pytest.raises(FileNotFoundError):
            load_questions_from_latex("/nonexistent/folder/path")
    
    def test_load_from_file_raises_error(self):
        """Test that loading from a file (not directory) raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            with pytest.raises(NotADirectoryError):
                load_questions_from_latex(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_load_from_empty_folder_raises_error(self):
        """Test that loading from empty folder raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="No .tex files found"):
                load_questions_from_latex(tmpdir)
    
    def test_load_ignores_non_tex_files(self):
        """Test that non-.tex files are ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a .tex file and a .txt file
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text("""
            \\begin{problem}
            Test question
            \\end{problem}
            \\begin{solution}
            Test solution
            \\end{solution}
            """)
            
            txt_file = Path(tmpdir) / "test.txt"
            txt_file.write_text("This should be ignored")
            
            questions = load_questions_from_latex(tmpdir)
            
            assert len(questions) == 1
    
    def test_load_subsection_format_file(self):
        """Test loading questions from file with subsection format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test.tex"
            tex_file.write_text("""
            \\subsection*{Problem 1}
            Test question
            
            \\section*{Solutions}
            \\subsection*{Solution 1}
            Test solution
            """)
            
            questions = load_questions_from_latex(tmpdir)
            
            assert len(questions) == 1
            assert questions[0].topic == "test"
            assert "Test question" in questions[0].text
            assert "Test solution" in questions[0].solution
    
    def test_load_mixed_format_files(self):
        """Test loading from files with different formats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Old format file
            file1 = Path(tmpdir) / "old.tex"
            file1.write_text("""
            \\begin{problem}
            Old format question
            \\end{problem}
            \\begin{solution}
            Old format solution
            \\end{solution}
            """)
            
            # New format file
            file2 = Path(tmpdir) / "new.tex"
            file2.write_text("""
            \\subsection*{Problem 1}
            New format question
            
            \\section*{Solutions}
            \\subsection*{Solution 1}
            New format solution
            """)
            
            questions = load_questions_from_latex(tmpdir)
            
            assert len(questions) == 2
            topics = [q.topic for q in questions]
            assert "old" in topics
            assert "new" in topics

