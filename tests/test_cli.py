"""Tests for the CLI."""
import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock, Mock

from cli import ExamGeneratorCLI
from core.models import Problem


class TestExamGeneratorCLI:
    """Test cases for ExamGeneratorCLI."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.problems_dir = self.temp_dir / "problems"
        self.output_dir = self.temp_dir / "output"
        self.template_dir = self.temp_dir / "latex"
        self.template_dir.mkdir(parents=True)
        self.template_file = self.template_dir / "template.tex"
        self.template_file.write_text(
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            "{{BODY}}\n"
            "\\end{document}\n"
        )

        # Create sample problems
        topic_dir = self.problems_dir / "floating_point"
        topic_dir.mkdir(parents=True)
        (topic_dir / "problem1.tex").write_text("Problem 1 content")
        (topic_dir / "problem2.tex").write_text("Problem 2 content")

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("cli.IntPrompt.ask")
    @patch("cli.Confirm.ask")
    @patch("cli.LaTeXCompiler")
    def test_cli_run_success(
        self,
        mock_compiler_class: MagicMock,
        mock_confirm: MagicMock,
        mock_int_prompt: MagicMock
    ) -> None:
        """Test successful CLI run."""
        # Mock user inputs
        mock_int_prompt.return_value = 2
        mock_confirm.return_value = False

        # Mock compiler
        mock_compiler = MagicMock()
        mock_pdf = self.output_dir / "exam.pdf"
        mock_compiler.compile.return_value = mock_pdf
        mock_compiler_class.return_value = mock_compiler

        cli = ExamGeneratorCLI(
            problem_dir=self.problems_dir,
            output_dir=self.output_dir,
            template_path=self.template_file
        )

        # Should not raise
        cli.run()

        # Verify LaTeX file was created
        tex_file = self.output_dir / "exam.tex"
        assert tex_file.exists()

        # Verify compiler was called
        mock_compiler.compile.assert_called_once()

    @patch("cli.IntPrompt.ask")
    def test_cli_no_problems(self, mock_int_prompt: MagicMock) -> None:
        """Test CLI with no problems available."""
        empty_dir = self.temp_dir / "empty_problems"
        empty_dir.mkdir()

        cli = ExamGeneratorCLI(
            problem_dir=empty_dir,
            output_dir=self.output_dir,
            template_path=self.template_file
        )

        # Should handle gracefully
        cli.run()

    @patch("cli.IntPrompt.ask")
    def test_cli_invalid_num_questions(self, mock_int_prompt: MagicMock) -> None:
        """Test CLI with invalid number of questions."""
        # Mock returning negative number, then valid number
        mock_int_prompt.side_effect = [-1, 0, 100, 2]

        cli = ExamGeneratorCLI(
            problem_dir=self.problems_dir,
            output_dir=self.output_dir,
            template_path=self.template_file
        )

        # Should eventually get valid input
        with patch("cli.Confirm.ask", return_value=False):
            with patch("cli.LaTeXCompiler"):
                cli.run()

        # Should have been called multiple times due to invalid inputs
        assert mock_int_prompt.call_count >= 2

    @patch("cli.IntPrompt.ask")
    @patch("cli.Confirm.ask")
    def test_cli_shuffle_preference(
        self,
        mock_confirm: MagicMock,
        mock_int_prompt: MagicMock
    ) -> None:
        """Test that shuffle preference is respected."""
        mock_int_prompt.return_value = 2
        mock_confirm.return_value = True  # Shuffle enabled

        cli = ExamGeneratorCLI(
            problem_dir=self.problems_dir,
            output_dir=self.output_dir,
            template_path=self.template_file
        )

        with patch("cli.LaTeXCompiler"):
            cli.run()

        # Verify confirm was called
        mock_confirm.assert_called_once()

    def test_cli_question_summary(self) -> None:
        """Test that question summary table is generated."""
        problems = [
            Problem(topic="topic1", text="P1", file_path=Path("file1.tex")),
            Problem(topic="topic2", text="P2", file_path=Path("file2.tex")),
        ]

        cli = ExamGeneratorCLI(
            problem_dir=self.problems_dir,
            output_dir=self.output_dir,
            template_path=self.template_file
        )

        # Should not raise
        cli._show_question_summary(problems)

