# Mock Exam Generator

A Python application for generating randomized mock exams from LaTeX problem files organized by topic.

## Features

- **Topic-based Organization**: Problems organized in topic subdirectories
- **Smart Question Selection**: Selects one question per topic, then randomly fills remaining slots
- **No Duplicates**: Ensures no question appears twice in an exam
- **LaTeX Compilation**: Automatically compiles exams to PDF
- **Rich CLI**: Beautiful terminal interface with progress bars and tables
- **Comprehensive Testing**: Full unit test coverage with pytest

## Installation

### Prerequisites

- Python 3.9+
- LaTeX distribution (for PDF compilation):
  - `latexmk` (recommended) or `pdflatex`
  - Required LaTeX packages: `amsmath`, `amsfonts`, `amssymb`, `geometry`, `graphicx`, `enumitem`

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or using the project:

```bash
pip install -e .
```

## Project Structure

```
question_bank/
├── main.py              # Entry point
├── cli.py               # CLI interface
├── config.py            # Configuration
├── core/
│   ├── loader.py        # Load LaTeX problems
│   ├── selector.py      # Select questions
│   ├── generator.py     # Generate exam LaTeX
│   ├── compiler.py      # Compile LaTeX to PDF
│   └── models.py        # Data models
├── latex/
│   └── template.tex     # LaTeX exam template
problems/
├── floating_point/      # Topic directories
├── linear_systems/
├── interpolation/
├── integration/
├── least_squares/
├── newtons_method/
└── odes_rk/
output/                  # Generated exams
tests/                   # Unit tests
```

## Usage

### Command Line Interface

Run the main script:

```bash
python -m question_bank.main
```

Or:

```bash
python question_bank/main.py
```

The CLI will:
1. Load all problems from the `problems/` directory
2. Prompt for the number of questions
3. Ask if you want to shuffle the order
4. Display a summary table of selected questions
5. Generate the exam LaTeX file
6. Compile to PDF (if LaTeX is available)

### Programmatic Usage

```python
from pathlib import Path
from question_bank.core.loader import ProblemLoader
from question_bank.core.selector import QuestionSelector
from question_bank.core.generator import ExamGenerator
from question_bank.core.compiler import LaTeXCompiler

# Load problems
loader = ProblemLoader(Path("problems"))
topics = loader.load_all_problems()

# Select questions
selector = QuestionSelector(topics)
selected = selector.select_questions(num_questions=5)

# Generate exam
generator = ExamGenerator(Path("question_bank/latex/template.tex"))
exam_latex = generator.generate_exam(selected, shuffle=True)

# Save LaTeX file
Path("output/exam.tex").write_text(exam_latex)

# Compile to PDF
compiler = LaTeXCompiler()
pdf_path = compiler.compile(Path("output/exam.tex"), Path("output"))
```

## Question Selection Algorithm

1. **One per Topic**: Selects exactly one question from each available topic
2. **Random Fill**: If more questions are requested than topics available, randomly selects additional questions from any topic
3. **No Duplicates**: Ensures no question appears twice in the same exam

## Testing

Run all tests:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=question_bank --cov-report=html
```

### Test Coverage

- `test_loader.py`: Tests for loading problems from directories
- `test_selector.py`: Tests for question selection logic
- `test_generator.py`: Tests for LaTeX generation
- `test_compiler.py`: Tests for LaTeX compilation (mocked)
- `test_cli.py`: Tests for CLI interface

## Configuration

Edit `question_bank/config.py` to customize:

- Problem directory path
- Output directory path
- LaTeX template path
- Compiler settings
- Default number of questions
- Logging level

## Adding Problems

1. Create a topic directory in `problems/` (e.g., `problems/my_topic/`)
2. Add `.tex` files containing LaTeX problem content
3. Run the generator - it will automatically detect new topics

Example problem file (`problems/floating_point/problem1.tex`):

```latex
Consider the floating point representation with base $\beta = 10$, 
precision $p = 3$, and exponent range $e \in [-2, 2]$.

What is the machine epsilon for this system?
```

## LaTeX Template

The exam template is located at `question_bank/latex/template.tex`. The `{{BODY}}` placeholder will be replaced with the selected problems.

Customize the template to match your institution's exam format.

## Troubleshooting

### LaTeX Compilation Fails

- Ensure LaTeX is installed: `which latexmk` or `which pdflatex`
- Check that required packages are installed
- Review the LaTeX log file in the output directory

### No Problems Found

- Verify `.tex` files exist in topic subdirectories
- Check that the `problems/` directory path is correct
- Ensure files have `.tex` extension

### Import Errors

- Make sure you're running from the project root directory
- Install the package: `pip install -e .`
- Check Python path includes the project directory

## License

MIT License

