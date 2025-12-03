"""Unit tests for persistence module."""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from models import Question, QuestionBank
from persistence import clear_progress, load_progress, save_progress


class TestSaveProgress:
    """Test cases for save_progress function."""
    
    def test_save_progress_creates_file(self):
        """Test that saving progress creates a JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            progress_file = os.path.join(tmpdir, "progress.json")
            
            bank = QuestionBank()
            q1 = Question(id="q1", topic="test", text="Q1", solution="S1", done=True)
            q2 = Question(id="q2", topic="test", text="Q2", solution="S2", done=False)
            bank.add_questions([q1, q2])
            
            save_progress(bank, progress_file)
            
            assert os.path.exists(progress_file)
    
    def test_save_progress_content(self):
        """Test that saved progress contains correct data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            progress_file = os.path.join(tmpdir, "progress.json")
            
            bank = QuestionBank()
            now = datetime.now()
            q1 = Question(
                id="q1",
                topic="test",
                text="Q1",
                solution="S1",
                done=True,
                last_seen=now
            )
            q2 = Question(
                id="q2",
                topic="test",
                text="Q2",
                solution="S2",
                done=False,
                last_seen=None
            )
            bank.add_questions([q1, q2])
            
            save_progress(bank, progress_file)
            
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert "questions" in data
            assert len(data["questions"]) == 2
            
            # Find q1 and q2 in the data
            q1_data = next(q for q in data["questions"] if q["id"] == "q1")
            q2_data = next(q for q in data["questions"] if q["id"] == "q2")
            
            assert q1_data["done"] is True
            assert q1_data["last_seen"] is not None
            assert q2_data["done"] is False
            assert q2_data["last_seen"] is None


class TestLoadProgress:
    """Test cases for load_progress function."""
    
    def test_load_progress_nonexistent_file(self):
        """Test that loading from nonexistent file doesn't crash."""
        bank = QuestionBank()
        q = Question(id="q1", topic="test", text="Q1", solution="S1")
        bank.add_question(q)
        
        # Should not raise an error
        load_progress(bank, "nonexistent.json")
        
        # Question should remain unchanged
        assert not q.done
    
    def test_load_progress_updates_questions(self):
        """Test that loading progress updates question states."""
        with tempfile.TemporaryDirectory() as tmpdir:
            progress_file = os.path.join(tmpdir, "progress.json")
            
            # Create progress file
            progress_data = {
                "questions": [
                    {
                        "id": "q1",
                        "topic": "test",
                        "done": True,
                        "last_seen": "2025-01-01T12:00:00"
                    },
                    {
                        "id": "q2",
                        "topic": "test",
                        "done": False,
                        "last_seen": None
                    }
                ]
            }
            
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f)
            
            # Create bank with questions
            bank = QuestionBank()
            q1 = Question(id="q1", topic="test", text="Q1", solution="S1", done=False)
            q2 = Question(id="q2", topic="test", text="Q2", solution="S2", done=False)
            bank.add_questions([q1, q2])
            
            # Load progress
            load_progress(bank, progress_file)
            
            # Check that progress was loaded
            assert q1.done is True
            assert q1.last_seen is not None
            assert q2.done is False
            assert q2.last_seen is None
    
    def test_load_progress_handles_invalid_json(self):
        """Test that loading invalid JSON doesn't crash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            progress_file = os.path.join(tmpdir, "progress.json")
            
            # Write invalid JSON
            with open(progress_file, 'w', encoding='utf-8') as f:
                f.write("invalid json content")
            
            bank = QuestionBank()
            q = Question(id="q1", topic="test", text="Q1", solution="S1")
            bank.add_question(q)
            
            # Should not raise an error, just print warning
            load_progress(bank, progress_file)
            
            # Question should remain unchanged
            assert not q.done


class TestClearProgress:
    """Test cases for clear_progress function."""
    
    def test_clear_progress_deletes_file(self):
        """Test that clearing progress deletes the file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            progress_file = os.path.join(tmpdir, "progress.json")
            
            # Create a progress file
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump({"questions": []}, f)
            
            assert os.path.exists(progress_file)
            
            clear_progress(progress_file)
            
            assert not os.path.exists(progress_file)
    
    def test_clear_progress_nonexistent_file(self):
        """Test that clearing nonexistent file doesn't crash."""
        clear_progress("nonexistent.json")
        # Should not raise an error

