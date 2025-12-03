"""Persistence utilities for saving and loading question bank progress."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from models import Question, QuestionBank


def save_progress(question_bank: QuestionBank, file_path: str = "progress.json") -> None:
    """
    Save question bank progress to a JSON file.
    
    Args:
        question_bank: The QuestionBank to save
        file_path: Path to the JSON file where progress will be saved
    """
    progress_data = {
        "questions": []
    }
    
    for question in question_bank.get_all_questions():
        question_data = {
            "id": question.id,
            "topic": question.topic,
            "done": question.done,
            "last_seen": question.last_seen.isoformat() if question.last_seen else None
        }
        progress_data["questions"].append(question_data)
    
    # Ensure directory exists
    file_path_obj = Path(file_path)
    file_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, indent=2, ensure_ascii=False)


def load_progress(
    question_bank: QuestionBank,
    file_path: str = "progress.json"
) -> None:
    """
    Load question bank progress from a JSON file and update the bank.
    
    Args:
        question_bank: The QuestionBank to update
        file_path: Path to the JSON file containing progress
    """
    if not Path(file_path).exists():
        # No progress file exists, start fresh
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            progress_data = json.load(f)
        
        # Create a mapping of question IDs to their progress data
        progress_map: Dict[str, Dict] = {}
        for q_data in progress_data.get("questions", []):
            progress_map[q_data["id"]] = q_data
        
        # Update questions in the bank
        for question in question_bank.get_all_questions():
            if question.id in progress_map:
                q_data = progress_map[question.id]
                question.done = q_data.get("done", False)
                last_seen_str = q_data.get("last_seen")
                if last_seen_str:
                    try:
                        question.last_seen = datetime.fromisoformat(last_seen_str)
                    except (ValueError, TypeError):
                        question.last_seen = None
                else:
                    question.last_seen = None
                    
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # If there's an error loading progress, just start fresh
        print(f"Warning: Could not load progress from {file_path}: {e}")
        print("Starting with fresh progress.")


def clear_progress(file_path: str = "progress.json") -> None:
    """
    Delete the progress file to reset all progress.
    
    Args:
        file_path: Path to the progress file to delete
    """
    progress_file = Path(file_path)
    if progress_file.exists():
        progress_file.unlink()

