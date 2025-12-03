# Mock Exam Generator: LaTeX Question Bank Automation

This project provides a fully automated system for generating randomized mock exams from LaTeX-based question banks.  
It is designed to help students practice large pools of numerical‑methods (or any LaTeX‑formatted) questions efficiently by preventing repeats, tracking progress, and producing clean exam + solution files.

---

## Project Overview
Developed as a personal study tool for automating exam preparation.  
The project parses LaTeX problem/solution blocks, stores them in an internal question bank, and generates fresh mock exams on demand.  
Each exam is exported into a timestamped folder with its corresponding solution file, making it ideal for timed practice and iterative learning.

---

## Key Concepts

- Automated parsing of LaTeX problem banks
- Randomized mock‑exam generation
- Tracking solved vs. unsolved questions
- Topic inference from file names
- Timestamped exam folders
- Exporting exams and solutions as LaTeX (and optionally PDF)
- Supports large question pools (100+ problems)
- Reset logic when all questions have been used

---

## Repository Structure

```
mock-exam-generator/
│
├── generator.py                 # Main program
├── parser.py                    # LaTeX parsing utilities (if modularized)
│
├── questions/                   # Input LaTeX question banks
│   ├── ODE.tex
│   ├── Newton.tex
│   ├── LeastSquares.tex
│   ├── Interpolation.tex
│   ├── Integration.tex
│   ├── GE.tex
│   ├── LU.tex
│   └── FP.tex
│
├── mock_exams/                  # Timestamped auto‑generated exams
│   ├── 2025-12-02_18-30-15/
│   │   ├── exam_2025-12-02_18-30-15.tex
│   │   ├── solutions_2025-12-02_18-30-15.tex
│   │   └── metadata.json
│   └── ...
│
├── README.md
└── .gitignore
```

---

## System Specification

### Input Format (LaTeX)

Each `.tex` file in `questions/` may contain multiple problems:

```latex
egin{problem}
Apply Forward Euler with h=0.1 to y' = -y.
\end{problem}

egin{solution}
y1 = y0 + h(-y0)
\end{solution}
```

### Output Format
Each generated exam folder contains:

- `exam_TIMESTAMP.tex`
- `solutions_TIMESTAMP.tex`
- `metadata.json` (tracking question usage)

Optional:
- `exam_TIMESTAMP.pdf`
- `solutions_TIMESTAMP.pdf`

---

## Features

### Part 1 – Question Parsing  
- Reads all `.tex` files in `questions/`
- Extracts problem/solution pairs
- Infers topic from filename
- Stores each question with metadata (id, topic, solved‑flag, last‑seen)

### Part 2 – Mock Exam Generation  
- Randomly selects *N* unsolved questions
- Marks them as solved
- Saves exam/solution pairs into timestamped folder
- Resets the bank when all questions are used

### Part 3 – Progress Tracking  
- `metadata.json` tracks:
  - solved questions
  - remaining question count
  - timestamp of last appearance
- Allows spaced repetition and balanced coverage

### Part 4 – Optional PDF Compilation  
Run `pdflatex` to produce fully formatted PDFs using:

```
pdflatex exam_TIMESTAMP.tex
```

---

## Running the Program

### Prerequisites
- Python 3.9+
- A LaTeX distribution (optional, for PDF export)

### Basic Usage

```
python generator.py --num 8
```

Generates an 8‑question mock exam.

### Folder Requirements

```
questions/   # must exist and contain .tex files
mock_exams/  # will be created automatically
```

---

## Example Outputs

| File | Description |
|------|-------------|
| `exam_2025-12-02_20-14-55.tex` | Randomized 8‑question LaTeX exam |
| `solutions_2025-12-02_20-14-55.tex` | Complete worked solutions |
| `metadata.json` | Progress tracking (solved/unsolved) |

---

## Tools and Technologies

- Python 3
- Regular expressions for LaTeX parsing
- JSON for progress tracking
- LaTeX for exam rendering
- Optional: `pdflatex` for PDF generation

---

## Academic Integrity Notice

Use this tool responsibly.  
This system is intended for **personal study and exam preparation only**.  
Do not use it to distribute copyrighted course material or violate academic policies.

---

## License
Licensed under the MIT License – see `LICENSE`.

---

## Author
**S. Pathmanathan**  
Software Engineering Student @ McMaster University  
Previous Co‑op @ AMD (Datacenter GPU Validation)  
Focus: Numerical Methods, Automation Tools, and Developer Productivity
