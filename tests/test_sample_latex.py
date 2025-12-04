"""Tests for sample LaTeX problem compilation."""
import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from core.generator import ExamGenerator
from core.compiler import LaTeXCompiler
from core.models import Problem


class TestSampleLaTeX:
    """Test cases for sample LaTeX problems."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.template_path = self.temp_dir / "template.tex"
        self.template_path.write_text(
            "\\documentclass{article}\n"
            "\\usepackage{amsmath}\n"
            "\\usepackage{amsfonts}\n"
            "\\usepackage{amssymb}\n"
            "\\begin{document}\n"
            "{{BODY}}\n"
            "\\end{document}\n"
        )

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_sample_ode_problem_format(self) -> None:
        """Test that sample ODE problem LaTeX format is correct."""
        # Sample problem in the format provided
        sample_problem = Problem(
            topic="odes_rk",
            text=(
                "\\subsection*{Problem 1 — First-Order ODE (Analytic Solution)}\n\n"
                "Solve the initial value problem:\n\n"
                "\\[\n"
                "y' = -y + t, \\qquad y(0) = 5.\n"
                "\\]\n\n"
                "Find the explicit closed-form solution \\(y(t)\\)."
            )
        )

        generator = ExamGenerator(self.template_path)
        exam_latex = generator.generate_exam([sample_problem], shuffle=False)

        # Verify LaTeX structure
        assert "\\documentclass{article}" in exam_latex
        assert "\\usepackage{amsmath}" in exam_latex
        assert "y' = -y + t" in exam_latex
        assert "\\subsection*{Problem 1}" in exam_latex
        assert "\\textbf{Topic:} odes_rk" in exam_latex

    def test_sample_pendulum_problem(self) -> None:
        """Test pendulum system conversion problem."""
        sample_problem = Problem(
            topic="odes_rk",
            text=(
                "\\subsection*{Problem 2 — Pendulum System Conversion}\n\n"
                "The motion of a pendulum of length \\(r = 1\\) satisfies:\n\n"
                "\\[\n"
                "\\theta'' = -g \\sin \\theta, \\qquad g = 9.81.\n"
                "\\]\n\n"
                "Convert this second-order ODE into an equivalent first-order system "
                "in variables \\(y_1, y_2\\).\n\n"
                "State the required initial conditions."
            )
        )

        generator = ExamGenerator(self.template_path)
        exam_latex = generator.generate_exam([sample_problem], shuffle=False)

        assert "\\theta'' = -g \\sin \\theta" in exam_latex
        assert "first-order system" in exam_latex

    def test_sample_rk4_problem(self) -> None:
        """Test Runge-Kutta 4th order problem."""
        sample_problem = Problem(
            topic="odes_rk",
            text=(
                "\\subsection*{Problem 13 — Runge–Kutta 4th Order (One Step)}\n\n"
                "Consider the initial value problem\n\n"
                "\\[\n"
                "y' = -2y + t, \\qquad y(0) = 1.\n"
                "\\]\n\n"
                "Use one step of the classical 4th-order Runge–Kutta method (RK4) "
                "with stepsize\n\n"
                "\\[\n"
                "h = 0.1\n"
                "\\]\n\n"
                "to approximate \\(y(0.1)\\).\n\n"
                "Write out the values of \\(k_1, k_2, k_3, k_4\\) and the final "
                "approximation \\(y_1\\)."
            )
        )

        generator = ExamGenerator(self.template_path)
        exam_latex = generator.generate_exam([sample_problem], shuffle=False)

        assert "y' = -2y + t" in exam_latex
        assert "Runge–Kutta" in exam_latex
        assert "k_1, k_2, k_3, k_4" in exam_latex

    @patch("core.compiler.subprocess.run")
    def test_sample_latex_compiles(self, mock_run: MagicMock) -> None:
        """Test that sample LaTeX compiles successfully."""
        # Mock successful compilation
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # Create sample exam LaTeX
        sample_problem = Problem(
            topic="odes_rk",
            text=(
                "\\subsection*{Problem 1}\n\n"
                "Solve: \\(y' = -y + t, \\quad y(0) = 5\\)."
            )
        )

        generator = ExamGenerator(self.template_path)
        exam_latex = generator.generate_exam([sample_problem], shuffle=False)

        # Save to file
        tex_file = self.temp_dir / "test_exam.tex"
        tex_file.write_text(exam_latex, encoding="utf-8")

        # Test compilation
        logs_dir = self.temp_dir / "logs"
        compiler = LaTeXCompiler(logs_dir=logs_dir)
        
        with patch.object(Path, "exists", return_value=True):
            pdf_path = compiler.compile(tex_file, self.temp_dir)
            
            # Verify subprocess was called
            mock_run.assert_called_once()
            
            # Verify logs directory would be created
            assert compiler.logs_dir == logs_dir

    def test_sample_latex_with_multiple_problems(self) -> None:
        """Test exam generation with multiple sample ODE problems."""
        problems = [
            Problem(
                topic="odes_rk",
                text="\\subsection*{Problem 1}\n\nSolve: \\(y' = -y + t\\)."
            ),
            Problem(
                topic="odes_rk",
                text="\\subsection*{Problem 2}\n\nConvert \\(\\theta'' = -g \\sin \\theta\\) to first-order system."
            ),
            Problem(
                topic="odes_rk",
                text="\\subsection*{Problem 3}\n\nApply Forward Euler with \\(h = 0.1\\)."
            ),
        ]

        generator = ExamGenerator(self.template_path)
        exam_latex = generator.generate_exam(problems, shuffle=False)

        # Verify all problems are included
        assert "Problem 1" in exam_latex
        assert "Problem 2" in exam_latex
        assert "Problem 3" in exam_latex
        assert "\\subsection*{Problem 1}" in exam_latex
        assert "\\subsection*{Problem 2}" in exam_latex
        assert "\\subsection*{Problem 3}" in exam_latex

