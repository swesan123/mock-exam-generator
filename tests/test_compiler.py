"""Tests for the LaTeX compiler."""
import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from core.compiler import LaTeXCompiler


class TestLaTeXCompiler:
    """Test cases for LaTeXCompiler."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.tex_file = self.temp_dir / "test.tex"
        self.tex_file.write_text("\\documentclass{article}\\begin{document}Test\\end{document}")

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("core.compiler.subprocess.run")
    def test_compile_success(self, mock_run: MagicMock) -> None:
        """Test successful compilation."""
        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # Create mock PDF file
        pdf_file = self.temp_dir / "test.pdf"
        pdf_file.write_text("fake pdf content")

        compiler = LaTeXCompiler()
        output_dir = self.temp_dir

        # This will fail because subprocess is mocked, but we can test the logic
        # In a real scenario, we'd need to mock the file system too
        with patch.object(Path, "exists", return_value=True):
            result = compiler.compile(self.tex_file, output_dir)

            # Verify subprocess was called correctly
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert "latexmk" in call_args[0][0] or "-pdf" in call_args[0][0]

    @patch("core.compiler.subprocess.run")
    def test_compile_file_not_found(self, mock_run: MagicMock) -> None:
        """Test that missing .tex file raises FileNotFoundError."""
        compiler = LaTeXCompiler()
        nonexistent = self.temp_dir / "nonexistent.tex"

        with pytest.raises(FileNotFoundError):
            compiler.compile(nonexistent, self.temp_dir)

        # subprocess should not be called
        mock_run.assert_not_called()

    @patch("core.compiler.subprocess.run")
    def test_compile_failure(self, mock_run: MagicMock) -> None:
        """Test that compilation failure raises CalledProcessError."""
        import subprocess

        # Mock failed subprocess run
        error = subprocess.CalledProcessError(returncode=1, cmd=["latexmk"])
        error.stdout = b"Error output"
        error.stderr = b"LaTeX Error"
        mock_run.side_effect = error

        compiler = LaTeXCompiler()
        output_dir = self.temp_dir

        with pytest.raises(subprocess.CalledProcessError):
            compiler.compile(self.tex_file, output_dir)

    @patch("core.compiler.subprocess.run")
    def test_compile_compiler_not_found(self, mock_run: MagicMock) -> None:
        """Test that missing compiler raises RuntimeError."""
        import subprocess

        # Mock FileNotFoundError (compiler not in PATH)
        mock_run.side_effect = FileNotFoundError("latexmk not found")

        compiler = LaTeXCompiler()
        output_dir = self.temp_dir

        with pytest.raises(RuntimeError, match="not found"):
            compiler.compile(self.tex_file, output_dir)

    def test_compiler_custom_options(self) -> None:
        """Test compiler with custom options."""
        compiler = LaTeXCompiler(
            compiler="pdflatex",
            options=["-output-directory", "output"]
        )

        assert compiler.compiler == "pdflatex"
        assert "-output-directory" in compiler.options

    def test_compiler_default_options(self) -> None:
        """Test compiler with default options."""
        compiler = LaTeXCompiler()

        assert compiler.compiler == "latexmk"
        assert "-pdf" in compiler.options
        assert "-interaction=nonstopmode" in compiler.options

