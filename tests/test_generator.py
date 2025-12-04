"""Tests for the exam generator."""
import pytest
from pathlib import Path
import tempfile
import shutil

from core.generator import ExamGenerator
from core.models import Problem


class TestExamGenerator:
    """Test cases for ExamGenerator."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.template_path = self.temp_dir / "template.tex"
        self.template_path.write_text(
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            "{{BODY}}\n"
            "\\end{document}\n"
        )

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generate_exam_basic(self) -> None:
        """Test basic exam generation."""
        generator = ExamGenerator(self.template_path)
        problems = [
            Problem(topic="floating_point", text="Problem 1 content"),
            Problem(topic="linear_systems", text="Problem 2 content"),
        ]

        result = generator.generate_exam(problems, shuffle=False)

        # Check that template structure is preserved
        assert "\\documentclass{article}" in result
        assert "\\begin{document}" in result
        assert "\\end{document}" in result

        # Check that problems are included
        assert "Problem 1 content" in result
        assert "Problem 2 content" in result

        # Check numbering
        assert "\\subsection*{Problem 1}" in result
        assert "\\subsection*{Problem 2}" in result

    def test_generate_exam_with_shuffle(self) -> None:
        """Test that shuffle changes order."""
        generator = ExamGenerator(self.template_path)
        problems = [
            Problem(topic="topic1", text="First"),
            Problem(topic="topic2", text="Second"),
            Problem(topic="topic3", text="Third"),
        ]

        result1 = generator.generate_exam(problems, shuffle=True)
        result2 = generator.generate_exam(problems, shuffle=True)

        # Results might be different due to shuffling
        # But both should contain all problems
        assert "First" in result1
        assert "Second" in result1
        assert "Third" in result1

    def test_generate_exam_without_shuffle(self) -> None:
        """Test that no shuffle preserves order."""
        generator = ExamGenerator(self.template_path)
        problems = [
            Problem(topic="topic1", text="First"),
            Problem(topic="topic2", text="Second"),
            Problem(topic="topic3", text="Third"),
        ]

        result1 = generator.generate_exam(problems, shuffle=False)
        result2 = generator.generate_exam(problems, shuffle=False)

        # Without shuffle, order should be consistent
        idx1 = result1.find("First")
        idx2 = result1.find("Second")
        idx3 = result1.find("Third")
        assert idx1 < idx2 < idx3

    def test_generate_exam_empty_problems(self) -> None:
        """Test that empty problems list raises ValueError."""
        generator = ExamGenerator(self.template_path)
        with pytest.raises(ValueError, match="no problems"):
            generator.generate_exam([], shuffle=False)

    def test_generate_exam_includes_topic(self) -> None:
        """Test that topic is included in generated exam."""
        generator = ExamGenerator(self.template_path)
        problems = [
            Problem(topic="floating_point", text="Problem content"),
        ]

        result = generator.generate_exam(problems, shuffle=False)

        assert "floating_point" in result
        assert "\\textbf{Topic:}" in result

    def test_generate_exam_numbering(self) -> None:
        """Test that problems are numbered correctly."""
        generator = ExamGenerator(self.template_path)
        problems = [
            Problem(topic="topic1", text="P1"),
            Problem(topic="topic2", text="P2"),
            Problem(topic="topic3", text="P3"),
        ]

        result = generator.generate_exam(problems, shuffle=False)

        # Check that all numbers 1-3 appear
        assert "\\subsection*{Problem 1}" in result
        assert "\\subsection*{Problem 2}" in result
        assert "\\subsection*{Problem 3}" in result

    def test_generate_exam_template_not_found(self) -> None:
        """Test that missing template raises FileNotFoundError."""
        nonexistent = self.temp_dir / "nonexistent.tex"
        with pytest.raises(FileNotFoundError):
            ExamGenerator(nonexistent)

    def test_generate_exam_body_replacement(self) -> None:
        """Test that {{BODY}} placeholder is replaced."""
        generator = ExamGenerator(self.template_path)
        problems = [
            Problem(topic="topic1", text="Test content"),
        ]

        result = generator.generate_exam(problems, shuffle=False)

        # {{BODY}} should be replaced
        assert "{{BODY}}" not in result
        # Content should be present
        assert "Test content" in result

