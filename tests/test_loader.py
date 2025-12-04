"""Tests for the problem loader."""
import pytest
from pathlib import Path
import tempfile
import shutil

from core.loader import ProblemLoader
from core.models import Problem


class TestProblemLoader:
    """Test cases for ProblemLoader."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.problems_dir = self.temp_dir / "problems"
        self.problems_dir.mkdir()

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_problems_single_topic(self) -> None:
        """Test loading problems from flat structure."""
        # Create test .tex files directly in problems directory
        (self.problems_dir / "problem1.tex").write_text("Problem 1 content")
        (self.problems_dir / "problem2.tex").write_text("Problem 2 content")

        # Load problems
        loader = ProblemLoader(self.problems_dir)
        topics = loader.load_all_problems()

        # Assertions
        assert "problems" in topics
        assert len(topics["problems"]) == 2
        assert all(isinstance(p, Problem) for p in topics["problems"])
        assert topics["problems"][0].topic == "problems"
        assert topics["problems"][0].text == "Problem 1 content"

    def test_load_problems_multiple_topics(self) -> None:
        """Test loading problems from multiple files."""
        # Create multiple .tex files directly in problems directory
        files = ["problem1.tex", "problem2.tex", "problem3.tex"]
        for file in files:
            (self.problems_dir / file).write_text(f"Problem from {file}")

        # Load problems
        loader = ProblemLoader(self.problems_dir)
        result = loader.load_all_problems()

        # Assertions - all should be in single "problems" topic
        assert len(result) == 1
        assert "problems" in result
        assert len(result["problems"]) == 3

    def test_load_problems_ignores_non_tex_files(self) -> None:
        """Test that non-.tex files are ignored."""
        (self.problems_dir / "problem1.tex").write_text("Valid problem")
        (self.problems_dir / "readme.txt").write_text("Not a problem")
        (self.problems_dir / "notes.md").write_text("Also not a problem")

        loader = ProblemLoader(self.problems_dir)
        topics = loader.load_all_problems()

        assert len(topics["problems"]) == 1
        assert topics["problems"][0].text == "Valid problem"

    def test_load_problems_empty_file(self) -> None:
        """Test that empty files are skipped."""
        (self.problems_dir / "problem1.tex").write_text("Valid problem")
        (self.problems_dir / "empty.tex").write_text("")  # Empty file

        loader = ProblemLoader(self.problems_dir)
        topics = loader.load_all_problems()

        assert len(topics["problems"]) == 1

    def test_load_problems_nonexistent_directory(self) -> None:
        """Test that FileNotFoundError is raised for nonexistent directory."""
        nonexistent = self.temp_dir / "nonexistent"

        with pytest.raises(FileNotFoundError):
            ProblemLoader(nonexistent)

    def test_load_problems_file_path_set(self) -> None:
        """Test that file_path is set correctly on Problem objects."""
        file_path = self.problems_dir / "problem1.tex"
        file_path.write_text("Problem content")

        loader = ProblemLoader(self.problems_dir)
        topics = loader.load_all_problems()

        problem = topics["problems"][0]
        assert problem.file_path == file_path

