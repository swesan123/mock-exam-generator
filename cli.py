"""Command-line interface for the exam generator."""
import logging
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import IntPrompt, Confirm
from rich import print as rprint

from config import (
    PROBLEM_DIR,
    OUTPUT_DIR,
    LOGS_DIR,
    TEMPLATE_FILE,
    TRACKER_FILE,
    DEFAULT_NUM_QUESTIONS,
    MAX_QUESTIONS,
    setup_logging
)
from core.loader import ProblemLoader
from core.selector import QuestionSelector
from core.generator import ExamGenerator
from core.compiler import LaTeXCompiler
from core.models import Problem
from core.persistence import ProblemTracker

console = Console()
logger = logging.getLogger(__name__)


class ExamGeneratorCLI:
    """Command-line interface for exam generation."""

    def __init__(
        self,
        problem_dir: Path = PROBLEM_DIR,
        output_dir: Path = OUTPUT_DIR,
        template_path: Path = TEMPLATE_FILE,
        logs_dir: Path = LOGS_DIR,
        tracker_file: Path = TRACKER_FILE
    ) -> None:
        """Initialize the CLI."""
        self.problem_dir = Path(problem_dir)
        self.output_dir = Path(output_dir)
        self.template_path = Path(template_path)
        self.logs_dir = Path(logs_dir)
        self.tracker = ProblemTracker(tracker_file)

    def run(self) -> None:
        """Run the CLI application."""
        try:
            self._show_header()

            # Load problems
            topics = self._load_problems()

            if not topics:
                console.print("[red]No problems found! Please add .tex files to the problems/ directory.[/red]")
                return

            # Show tracking stats
            self._show_tracking_stats(topics)

            # Option to reset tracking (only if there are used problems)
            stats = self.tracker.get_stats()
            if stats["total_used"] > 0:
                console.print("[yellow]Tip: Use --reset-tracking flag to reset, or answer below[/yellow]")
                if Confirm.ask("[bold]Reset problem tracking now?[/bold]", default=False):
                    self.tracker.reset()
                    console.print("[green]✓ Problem tracking reset[/green]\n")
                    self._show_tracking_stats(topics)

            # Get number of questions
            num_questions = self._prompt_num_questions(len(topics))

            # Get shuffle preference
            shuffle = self._prompt_shuffle()

            # Select questions
            selected = self._select_questions(topics, num_questions)

            # Show summary table
            self._show_question_summary(selected)

            # Generate exam
            self._generate_exam(selected, shuffle)

            console.print("\n[green]✓ Exam generated successfully![/green]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        except Exception as e:
            logger.exception("Error in CLI")
            console.print(f"[red]Error: {e}[/red]")
            raise

    def _show_header(self) -> None:
        """Display the application header."""
        console.print("\n[bold cyan]╔═══════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║[/bold cyan]  [bold white]Mock Exam Generator[/bold white]  [bold cyan]║[/bold cyan]")
        console.print("[bold cyan]╚═══════════════════════════════════════╝[/bold cyan]\n")

    def _load_problems(self) -> dict[str, list[Problem]]:
        """Load problems from the problems directory."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Loading problems...", total=None)
            try:
                loader = ProblemLoader(self.problem_dir)
                topics = loader.load_all_problems()
                progress.update(task, completed=True)
                return topics
            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[red]Failed to load problems: {e}[/red]")
                raise

    def _prompt_num_questions(self, num_topics: int) -> int:
        """Prompt user for number of questions."""
        console.print(f"[cyan]Found {num_topics} topics with problems.[/cyan]\n")

        while True:
            try:
                num = IntPrompt.ask(
                    f"[bold]How many questions?[/bold]",
                    default=DEFAULT_NUM_QUESTIONS
                )

                if num <= 0:
                    console.print("[yellow]Number must be positive.[/yellow]")
                    continue

                if num > MAX_QUESTIONS:
                    console.print(f"[yellow]Maximum {MAX_QUESTIONS} questions allowed.[/yellow]")
                    continue

                return num
            except KeyboardInterrupt:
                raise
            except Exception as e:
                console.print(f"[yellow]Invalid input: {e}[/yellow]")

    def _prompt_shuffle(self) -> bool:
        """Prompt user for shuffle preference."""
        return Confirm.ask(
            "[bold]Shuffle question order?[/bold]",
            default=True
        )

    def _select_questions(
        self,
        topics: dict[str, list[Problem]],
        num_questions: int
    ) -> list[Problem]:
        """Select questions for the exam."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Selecting questions...", total=None)
            try:
                selector = QuestionSelector(topics, tracker=self.tracker, prefer_unused=True)
                selected = selector.select_questions(num_questions)
                
                # Mark selected problems as used
                self.tracker.mark_multiple_as_used(selected)
                
                progress.update(task, completed=True)
                return selected
            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[red]Failed to select questions: {e}[/red]")
                raise

    def _show_question_summary(self, problems: list[Problem]) -> None:
        """Display a table summarizing selected questions."""
        table = Table(title="Selected Questions", show_header=True, header_style="bold magenta")
        table.add_column("Number", style="cyan", justify="right")
        table.add_column("Topic", style="green")
        table.add_column("File", style="yellow")
        table.add_column("Status", style="yellow")

        for i, problem in enumerate(problems, start=1):
            file_name = problem.file_path.name if problem.file_path else "N/A"
            was_used = self.tracker.is_used(problem) if self.tracker else False
            status = "[red]Used[/red]" if was_used else "[green]New[/green]"
            table.add_row(str(i), problem.topic, file_name, status)

        console.print("\n")
        console.print(table)
        console.print("\n")

    def _show_tracking_stats(self, topics: dict[str, list[Problem]]) -> None:
        """Display tracking statistics."""
        if not self.tracker:
            return

        all_problems = []
        for problem_list in topics.values():
            all_problems.extend(problem_list)

        total = len(all_problems)
        used = sum(1 for p in all_problems if self.tracker.is_used(p))
        unused = total - used

        if total > 0:
            percentage = (used / total) * 100
            console.print(f"\n[cyan]Problem Tracking:[/cyan]")
            console.print(f"  Total problems: {total}")
            console.print(f"  [green]Unused: {unused}[/green] | [yellow]Used: {used}[/yellow] ({percentage:.1f}%)")
            console.print()

    def _generate_exam(self, problems: list[Problem], shuffle: bool) -> None:
        """Generate the exam LaTeX and PDF."""
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate LaTeX
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating LaTeX...", total=None)
            try:
                generator = ExamGenerator(self.template_path)
                exam_latex = generator.generate_exam(problems, shuffle=shuffle)
                progress.update(task, completed=True)
            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[red]Failed to generate LaTeX: {e}[/red]")
                raise

        # Save LaTeX file
        tex_path = self.output_dir / "exam.tex"
        tex_path.write_text(exam_latex, encoding="utf-8")
        console.print(f"[green]✓[/green] LaTeX saved to: {tex_path}")

        # Compile to PDF
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Compiling PDF...", total=None)
            try:
                compiler = LaTeXCompiler(logs_dir=self.logs_dir)
                pdf_path = compiler.compile(tex_path, self.output_dir)
                progress.update(task, completed=True)
                console.print(f"[green]✓[/green] PDF generated: {pdf_path}")
            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[yellow]Warning: PDF compilation failed: {e}[/yellow]")
                console.print(f"[yellow]LaTeX file is available at: {tex_path}[/yellow]")
                if self.logs_dir.exists():
                    console.print(f"[yellow]Check logs in: {self.logs_dir}[/yellow]")
                # Don't raise - allow user to compile manually

