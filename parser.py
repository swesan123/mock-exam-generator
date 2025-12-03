"""LaTeX parsing utilities for extracting questions from LaTeX files."""

import os
import re
from pathlib import Path
from typing import List, Tuple

from models import Question


def parse_latex_questions(latex_text: str, topic: str = "unknown") -> List[Question]:
    """
    Parse LaTeX text and extract problem/solution pairs.
    
    Supports two formats:
    1. Old format: \begin{problem}...\end{problem} with \begin{solution}...\end{solution}
    2. New format: \subsection*{Problem X} and \subsection*{Solution X} in separate sections
    
    Args:
        latex_text: The LaTeX content to parse
        topic: The topic name (usually derived from filename)
    
    Returns:
        List of Question objects extracted from the LaTeX text
    """
    questions: List[Question] = []
    
    # Try new format first (subsection*{Problem X} and subsection*{Solution X})
    if r'\subsection*{Problem' in latex_text:
        questions = _parse_subsection_format(latex_text, topic)
        if questions:
            return questions
    
    # Fall back to old format (\begin{problem}...\end{problem})
    problem_pattern = r'\\begin\{problem\}(.*?)\\end\{problem\}'
    solution_pattern = r'\\begin\{solution\}(.*?)\\end\{solution\}'
    
    # Find all problem blocks
    problem_matches = re.finditer(problem_pattern, latex_text, re.DOTALL)
    
    for idx, problem_match in enumerate(problem_matches):
        problem_text = problem_match.group(1).strip()
        
        # Find the corresponding solution (next solution after this problem)
        solution_text = ""
        solution_start = problem_match.end()
        solution_match = re.search(
            solution_pattern,
            latex_text[solution_start:],
            re.DOTALL
        )
        
        if solution_match:
            solution_text = solution_match.group(1).strip()
        else:
            # If no solution found, use empty string
            solution_text = ""
        
        # Generate unique ID: topic_index
        question_id = f"{topic}_{idx + 1}"
        
        # Create Question object
        question = Question(
            id=question_id,
            topic=topic,
            text=problem_text,
            solution=solution_text
        )
        
        questions.append(question)
    
    return questions


def _parse_subsection_format(latex_text: str, topic: str) -> List[Question]:
    """
    Parse LaTeX files using \subsection*{Problem X} and \subsection*{Solution X} format.
    
    Args:
        latex_text: The LaTeX content to parse
        topic: The topic name
    
    Returns:
        List of Question objects
    """
    questions: List[Question] = []
    
    # Pattern to match \subsection*{Problem X — Title} or \subsection*{Problem X}
    problem_pattern = r'\\subsection\*\{Problem\s+(\d+)(?:\s*—\s*[^}]*)?\}(.*?)(?=\\subsection\*\{Problem|\Z)'
    
    # Pattern to match \subsection*{Solution X}
    solution_pattern = r'\\subsection\*\{Solution\s+(\d+)\}(.*?)(?=\\subsection\*\{Solution|\Z)'
    
    # Extract all problems with their numbers
    problems = {}
    problem_matches = re.finditer(problem_pattern, latex_text, re.DOTALL)
    
    for match in problem_matches:
        problem_num = int(match.group(1))
        problem_text = match.group(2).strip()
        # Remove leading/trailing whitespace and comments
        problem_text = re.sub(r'^%[^\n]*\n?', '', problem_text, flags=re.MULTILINE)
        problem_text = problem_text.strip()
        problems[problem_num] = problem_text
    
    # Extract all solutions with their numbers
    solutions = {}
    solution_matches = re.finditer(solution_pattern, latex_text, re.DOTALL)
    
    for match in solution_matches:
        solution_num = int(match.group(1))
        solution_text = match.group(2).strip()
        # Remove leading/trailing whitespace and comments
        solution_text = re.sub(r'^%[^\n]*\n?', '', solution_text, flags=re.MULTILINE)
        solution_text = solution_text.strip()
        solutions[solution_num] = solution_text
    
    # Match problems with solutions by number
    for problem_num in sorted(problems.keys()):
        problem_text = problems[problem_num]
        solution_text = solutions.get(problem_num, "")
        
        # Generate unique ID: topic_problem_number
        question_id = f"{topic}_{problem_num}"
        
        # Create Question object
        question = Question(
            id=question_id,
            topic=topic,
            text=problem_text,
            solution=solution_text
        )
        
        questions.append(question)
    
    return questions


def load_questions_from_latex(folder_path: str) -> List[Question]:
    """
    Load all questions from LaTeX files in a folder.
    
    Args:
        folder_path: Path to the folder containing LaTeX files
    
    Returns:
        List of all Question objects from all files
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Path is not a directory: {folder_path}")
    
    all_questions: List[Question] = []
    folder = Path(folder_path)
    
    # Find all .tex files in the folder
    tex_files = list(folder.glob("*.tex"))
    
    if not tex_files:
        raise ValueError(f"No .tex files found in {folder_path}")
    
    for tex_file in tex_files:
        try:
            # Read file content
            with open(tex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract topic from filename (without extension)
            topic = tex_file.stem
            
            # Parse questions from this file
            questions = parse_latex_questions(content, topic)
            all_questions.extend(questions)
            
        except Exception as e:
            # Log error but continue with other files
            print(f"Warning: Error processing {tex_file}: {e}")
            continue
    
    return all_questions

