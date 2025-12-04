# Mock Exam Generator: AI-Powered LaTeX Question Bank Automation

A comprehensive system for generating randomized mock exams from LaTeX-based question banks and PDF documents. Features AI-powered PDF extraction, self-learning regex patterns, and multiple user interfaces (Web, GUI, CLI).

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Software Architecture](#software-architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [System Architecture](#system-architecture)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [License](#license)

---

## Project Overview

This project automates the entire workflow from PDF documents to practice exams. It uses AI to learn extraction patterns, continuously improves accuracy, and provides multiple interfaces for different use cases.

**Use Cases:**
- Extract questions from lecture notes, assignments, or problem sets
- Generate randomized practice exams
- Track progress and prevent question repetition
- Support spaced repetition learning

---

## Key Features

### Core Features
- **AI-Powered PDF Extraction**: Automatically extract questions from PDFs using OpenAI
- **Self-Learning Regex Patterns**: AI discovers and refines extraction patterns, stored persistently
- **Automated Solution Generation**: Generate solutions for questions without answers
- **LaTeX Parsing**: Parse existing LaTeX question banks
- **Randomized Exam Generation**: Generate fresh mock exams on demand
- **Progress Tracking**: Track solved vs. unsolved questions with persistence
- **Topic Management**: Organize questions by topic with per-topic statistics
- **One-Per-Topic Option**: Generate exams with one question per topic

### User Interfaces
- **Web Interface**: Modern, responsive web UI for PDF upload and exam download
- **Graphical UI**: Desktop GUI with visual statistics and controls
- **Command-Line Interface**: Terminal-based interface with rich formatting

### Advanced Features
- **Auto-Refinement**: Automatically improves extraction patterns on validation failures
- **Validation Engine**: Comprehensive validation of extracted content
- **Multiple Question Formats**: Supports Problem, Example, Q1, Exercise, etc.
- **Timestamped Exams**: Each exam saved with timestamp for organization
- **Progress Reset**: Option to reset all progress and start fresh

---

## Software Architecture

This application follows a **Layered Architecture** (N-Tier Architecture) with elements of:

1. **Layered Architecture Pattern**
   - **Presentation Layer**: Web UI, GUI, CLI interfaces
   - **Application Layer**: Business logic and orchestration (generator, pipeline)
   - **Domain Layer**: Core models and entities (Question, Exam, QuestionBank)
   - **Infrastructure Layer**: External services, file I/O, persistence

2. **Pipeline Pattern**
   - PDF processing follows a pipeline: Extract → Discover → Extract → Validate → Refine → Format

3. **Service Layer Pattern**
   - Business logic encapsulated in service classes (OpenAIClient, RegexExtractor, Validator)

4. **Repository Pattern**
   - Data persistence abstracted (RegexStorage, persistence.py)

5. **Strategy Pattern**
   - Multiple extraction strategies (regex-based, simple extraction)

### Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│              Presentation Layer                         │
│  - Web UI (Flask + HTML/CSS/JS)                        │
│  - GUI (Tkinter)                                        │
│  - CLI (Rich terminal UI)                              │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│              Application Layer                          │
│  - generator.py (Exam generation logic)                │
│  - pdf_to_exam_pipeline.py (Orchestration)             │
│  - web_app.py (API endpoints)                          │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│              Domain Layer                               │
│  - models.py (Question, Exam, QuestionBank)            │
│  - Business rules and validation                       │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│              Infrastructure Layer                       │
│  - pdf_extractor.py (PDF I/O)                          │
│  - openai_client.py (External API)                     │
│  - regex_storage.py (Persistence)                      │
│  - persistence.py (Progress tracking)                  │
│  - parser.py, exporter.py (File operations)            │
└─────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

- **Python 3.9+**
- **OpenAI API Key** (for PDF extraction features) - Get from https://platform.openai.com/api-keys
- **LaTeX distribution** (optional, for PDF compilation)

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd mock-exam-generator
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Environment Variables

```bash
export OPENAI_API_KEY="your-api-key-here"
export FLASK_SECRET_KEY="your-secret-key-here"  # Optional, for production
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
FLASK_SECRET_KEY=your-secret-key-here
```

### Step 4: Verify Installation

```bash
python3 verify_setup.py
```

---

## Quick Start

### Web Interface (Recommended)

```bash
python3 web_app.py
```

Open `http://localhost:5000` in your browser.

### GUI Application

```bash
python3 gui.py
```

### Command-Line Interface

```bash
python3 generator.py
```

---

## Usage

### Web Interface

1. **Upload PDF**: Click "Upload PDF" and select a PDF file
2. **Process**: System automatically extracts questions using AI
3. **Generate Exam**: Enter number of questions and click "Generate Exam"
4. **Download**: Download exam as ZIP file containing LaTeX files

### GUI Application

1. Launch `gui.py`
2. View statistics in the top panel
3. Enter number of questions and check "One per topic" if desired
4. Click "Generate Exam"
5. View results in the output panel

### Command-Line Interface

```bash
python3 generator.py
```

Interactive prompts will guide you through:
- Entering number of questions
- Choosing one-per-topic option
- Viewing statistics
- Resetting progress (type 'r')
- Quitting (type 'q')

### Example Session

```
Loading questions from LaTeX files...
Loaded 29 questions from questions/
Resumed progress: 10 questions already completed

============================================================
MOCK EXAM GENERATOR
============================================================
Available questions: 19
Enter the number of questions for the mock exam (or 'q' to quit):
8

Generating exam with 8 questions...
Exam generated successfully!
Exam file: mock_exams/2025-12-03_16-39-25/exam_2025-12-03_16-39-25.tex
Solutions file: mock_exams/2025-12-03_16-39-25/solutions_2025-12-03_16-39-25.tex

Solve the exam now. Press Enter when finished...
[User presses Enter]

Reviewing your performance...
============================================================
QUESTION BANK STATISTICS
============================================================
Total questions: 29
Solved questions: 18
Unsolved questions: 11
Completion rate: 62.1%
...
```

---

## System Architecture

### Data Flow

#### PDF Upload Flow

```
PDF Upload → Text Extraction → AI Pattern Discovery → 
Regex Extraction → Validation → Solution Generation → 
LaTeX Formatting → questions/ folder → Mock Exam Generator
```

#### Exam Generation Flow

```
User Request → Load Questions → Filter Unsolved → 
Random Selection → Mark as Done → Export LaTeX → 
Save Progress → Return Download Link
```

### Module Responsibilities

#### Core Modules

- **pdf_extractor.py**: Extracts text from PDF files
- **openai_client.py**: Wraps OpenAI API for pattern discovery and solution generation
- **regex_storage.py**: Persistent storage of learned regex patterns
- **regex_extractor.py**: Applies patterns to extract questions
- **validator.py**: Validates extraction quality
- **latex_formatter.py**: Converts extracted content to LaTeX format
- **pdf_to_exam_pipeline.py**: Orchestrates PDF-to-exam process

#### Application Modules

- **generator.py**: Exam generation logic and CLI interface
- **models.py**: Data models (Question, Exam, QuestionBank)
- **parser.py**: LaTeX parsing utilities
- **exporter.py**: LaTeX export functionality
- **persistence.py**: Progress tracking persistence

#### Web Application

- **web_app.py**: Flask REST API
- **templates/index.html**: Web UI
- **static/**: CSS and JavaScript files
- **config.py**: Configuration management

---

## API Documentation

### Web API Endpoints

#### POST `/api/upload`
Upload and process a PDF file.

**Request:**
- `file`: PDF file (multipart/form-data)
- `generate_solutions`: boolean (optional, default: true)

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed PDF...",
  "result": {
    "questions_extracted": 10,
    "questions_with_solutions": 8,
    "validation_warnings": []
  }
}
```

#### POST `/api/generate-exam`
Generate a mock exam.

**Request:**
```json
{
  "num_questions": 5,
  "one_per_topic": false
}
```

**Response:**
```json
{
  "success": true,
  "exam_id": "2025-12-03_16-39-25",
  "exam_path": "mock_exams/.../exam_...tex",
  "solutions_path": "mock_exams/.../solutions_...tex",
  "num_questions": 5,
  "topics": ["ODE", "Newton"]
}
```

#### GET `/api/download-exam/<exam_id>`
Download exam files as ZIP.

#### GET `/api/stats`
Get question bank statistics.

#### POST `/api/reset-progress`
Reset all progress.

### Programmatic API

```python
from src.core.openai_client import OpenAIClient
from src.core.pdf_to_exam_pipeline import PDFToExamPipeline
from src.core.regex_storage import RegexStorage

# Initialize
client = OpenAIClient(api_key="your-key")
storage = RegexStorage()
pipeline = PDFToExamPipeline(client, storage)

# Process PDF
result = pipeline.process_pdf("lecture.pdf", topic="ODE")
print(f"Extracted {result['questions_extracted']} questions")
```

---

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

### Run Specific Test Suite

```bash
pytest tests/test_pdf_extractor.py -v
pytest tests/test_generator.py -v
pytest tests/test_web_app.py -v
```

### Test Coverage

- ✅ 91+ tests passing
- ✅ Unit tests for all modules
- ✅ Integration tests for pipeline
- ✅ Mock-based testing for external APIs

---

## Reference Files for Validation

The system uses reference LaTeX files to validate formatting. Place reference `.tex` files in the `data/references/` folder.

### Setting Up Reference Files

1. Copy your reference LaTeX files to `data/references/`:
   ```bash
   mkdir -p data/references
   cp /path/to/reference.tex data/references/
   ```

2. Name reference files to match topics (e.g., `ODEs.tex`, `Newtons Method.tex`)

3. The system will automatically:
   - Compare generated LaTeX with references
   - Validate structure, formatting, and math alignment
   - Use AI to check formatting quality
   - Provide suggestions for improvements

### Validation Methods

The system uses multiple validation methods:

1. **Reference Comparison**: Compares structure and format with reference files
2. **AI Validation**: Uses OpenAI to validate formatting, math, and structure
3. **Structural Validation**: Checks for required sections and proper LaTeX structure
4. **Math Formatting Validation**: Validates math mode usage and equation formatting

## Troubleshooting

### OpenAI API Errors

- **Problem**: API key not found or invalid
- **Solution**: Verify `OPENAI_API_KEY` is set: `echo $OPENAI_API_KEY`
- **Check**: API quota and billing status
- **Ensure**: Internet connection is available

### PDF Extraction Fails

- **Problem**: No text extracted from PDF
- **Solution**: Verify PDF has extractable text (not just images)
- **Check**: PDF is not password-protected
- **Try**: Different PDF format or OCR if needed

### No Questions Extracted

- **Problem**: AI extraction returns zero questions
- **Solution**: Check validation warnings in response
- **Review**: `regex_rules.json` for learned patterns
- **Try**: Uploading PDF with clearer question markers
- **Verify**: OpenAI API is working correctly

### Web App Won't Start

- **Problem**: Flask application fails to start
- **Solution**: Check Flask is installed: `pip install flask`
- **Verify**: Port 5000 is available
- **Check**: Syntax errors: `python3 -m py_compile web_app.py`

### Import Errors

- **Problem**: Module not found errors
- **Solution**: Ensure you're in the project root directory
- **Check**: All dependencies installed: `pip install -r requirements.txt`
- **Verify**: Python path includes project directory

---

## Security

### Security Checklist

- [ ] Set strong `FLASK_SECRET_KEY` in production
- [ ] Use HTTPS in production
- [ ] Restrict file upload size (default: 50MB)
- [ ] Validate all user inputs
- [ ] Keep API keys secure (use environment variables)
- [ ] Regularly update dependencies
- [ ] Never commit API keys to version control

### File Upload Security

- Files validated for extension and size
- Secure filename handling
- Temporary files cleaned up after processing
- Input sanitization on all user inputs

### API Key Management

- Store keys in environment variables
- Use `.env` file for local development (add to `.gitignore`)
- Rotate keys regularly
- Use different keys for development and production

---

## Project Structure

```
mock-exam-generator/
├── src/                      # Source code
│   ├── core/                # Core business logic
│   │   ├── pdf_extractor.py
│   │   ├── openai_client.py
│   │   ├── regex_storage.py
│   │   ├── regex_extractor.py
│   │   ├── validator.py
│   │   ├── latex_formatter.py
│   │   └── pdf_to_exam_pipeline.py
│   ├── application/         # Application layer
│   │   ├── generator.py
│   │   ├── models.py
│   │   ├── parser.py
│   │   ├── exporter.py
│   │   └── persistence.py
│   └── web/                 # Web application
│       ├── web_app.py
│       ├── config.py
│       ├── templates/
│       └── static/
├── tests/                   # Test suite
│   ├── test_pdf_extractor.py
│   ├── test_generator.py
│   ├── test_web_app.py
│   └── ...
├── scripts/                 # Utility scripts
│   ├── run_web.sh
│   └── verify_setup.py
├── data/                    # Data directories
│   ├── questions/          # LaTeX question banks
│   ├── mock_exams/         # Generated exams
│   └── uploads/            # Temporary uploads
├── docs/                    # Documentation
│   └── (archived docs)
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

---

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | Yes | - |
| `FLASK_SECRET_KEY` | Secret key for Flask sessions | No | dev-secret-key |
| `FLASK_HOST` | Host to bind Flask server | No | 0.0.0.0 |
| `FLASK_PORT` | Port for Flask server | No | 5000 |
| `FLASK_DEBUG` | Enable Flask debug mode | No | False |

---

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

### Using Docker (Future)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "web_app:app"]
```

---

## Dependencies

- **pytest>=7.4.0** - Testing framework
- **pytest-cov>=4.1.0** - Coverage reporting
- **rich>=13.0.0** - Terminal UI
- **PyPDF2>=3.0.0** - PDF extraction
- **openai>=1.0.0** - OpenAI API client
- **flask>=3.0.0** - Web framework
- **werkzeug>=3.0.0** - WSGI utilities

---

## License

Licensed under the MIT License.

---

## Author

**S. Pathmanathan**  
Software Engineering Student @ McMaster University  
Previous Co-op @ AMD (Datacenter GPU Validation)  
Focus: Numerical Methods, Automation Tools, and Developer Productivity

---

## Academic Integrity Notice

Use this tool responsibly.  
This system is intended for **personal study and exam preparation only**.  
Do not use it to distribute copyrighted course material or violate academic policies.
