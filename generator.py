"""Main program for generating mock exams."""

import random
from datetime import datetime
from pathlib import Path
from typing import Optional

from exporter import export_exam_to_latex, export_solutions_to_latex
from models import Exam, QuestionBank
from parser import load_questions_from_latex
from persistence import load_progress, save_progress


def generate_mock_exam(question_bank: QuestionBank, num_questions: int, one_per_topic: bool = False) -> Exam:
    """
    Generate a mock exam with the specified number of questions.
    
    Args:
        question_bank: The QuestionBank to select questions from
        num_questions: Number of questions to include in the exam
        one_per_topic: If True, ensures at most one question per topic
    
    Returns:
        An Exam object containing the selected questions
    """
    if num_questions <= 0:
        raise ValueError("Number of questions must be positive")
    
    if one_per_topic:
        return _generate_exam_one_per_topic(question_bank, num_questions)
    
    # Get unsolved questions
    unsolved = question_bank.get_unsolved_questions()
    
    # If not enough unsolved questions, reset all questions
    if len(unsolved) < num_questions:
        question_bank.reset_all_questions()
        unsolved = question_bank.get_unsolved_questions()
    
    if len(unsolved) < num_questions:
        raise ValueError(
            f"Not enough questions in bank. "
            f"Requested: {num_questions}, Available: {len(unsolved)}"
        )
    
    # Randomly select questions
    selected = random.sample(unsolved, num_questions)
    
    # Mark selected questions as done and update last_seen
    current_time = datetime.now()
    for question in selected:
        question.done = True
        question.last_seen = current_time
    
    # Create exam
    exam = Exam(
        questions=selected,
        num_questions=num_questions,
        timestamp=current_time
    )
    
    return exam


def _generate_exam_one_per_topic(question_bank: QuestionBank, num_questions: int) -> Exam:
    """
    Generate a mock exam with at most one question per topic.
    
    Args:
        question_bank: The QuestionBank to select questions from
        num_questions: Number of questions to include in the exam
    
    Returns:
        An Exam object containing the selected questions
    """
    # Get all available topics
    topics = question_bank.get_topics()
    
    if num_questions > len(topics):
        raise ValueError(
            f"Cannot generate {num_questions} questions with one per topic. "
            f"Only {len(topics)} topic(s) available: {', '.join(topics)}. "
            f"Please request at most {len(topics)} question(s) or use normal selection mode."
        )
    
    # Get unsolved questions grouped by topic
    unsolved_by_topic = {}
    for topic in topics:
        topic_unsolved = [
            q for q in question_bank.get_questions_by_topic(topic)
            if not q.done
        ]
        if topic_unsolved:
            unsolved_by_topic[topic] = topic_unsolved
    
    # If not enough topics have unsolved questions, reset all questions
    if len(unsolved_by_topic) < num_questions:
        question_bank.reset_all_questions()
        unsolved_by_topic = {}
        for topic in topics:
            topic_unsolved = question_bank.get_questions_by_topic(topic)
            if topic_unsolved:
                unsolved_by_topic[topic] = topic_unsolved
    
    if len(unsolved_by_topic) < num_questions:
        raise ValueError(
            f"Not enough topics with available questions. "
            f"Requested: {num_questions}, Available topics: {len(unsolved_by_topic)}"
        )
    
    # Randomly select topics
    selected_topics = random.sample(list(unsolved_by_topic.keys()), num_questions)
    
    # Select one random question from each selected topic
    selected = []
    current_time = datetime.now()
    
    for topic in selected_topics:
        topic_questions = unsolved_by_topic[topic]
        question = random.choice(topic_questions)
        question.done = True
        question.last_seen = current_time
        selected.append(question)
    
    # Create exam
    exam = Exam(
        questions=selected,
        num_questions=num_questions,
        timestamp=current_time
    )
    
    return exam


def review_stats(question_bank: QuestionBank) -> None:
    """
    Print statistics about the question bank.
    
    Args:
        question_bank: The QuestionBank to analyze
    """
    total = question_bank.get_total_count()
    solved = question_bank.get_solved_count()
    unsolved = question_bank.get_unsolved_count()
    
    print("\n" + "=" * 60)
    print("QUESTION BANK STATISTICS")
    print("=" * 60)
    print(f"Total questions: {total}")
    print(f"Solved questions: {solved}")
    print(f"Unsolved questions: {unsolved}")
    
    if total > 0:
        completion_rate = (solved / total) * 100
        print(f"Completion rate: {completion_rate:.1f}%")
    
    # Per-topic statistics
    topics = question_bank.get_topics()
    if topics:
        print("\nPer-topic statistics:")
        print("-" * 60)
        for topic in topics:
            topic_questions = question_bank.get_questions_by_topic(topic)
            topic_solved = sum(1 for q in topic_questions if q.done)
            topic_total = len(topic_questions)
            topic_unsolved = topic_total - topic_solved
            
            print(f"\n{topic}:")
            print(f"  Total: {topic_total}")
            print(f"  Solved: {topic_solved}")
            print(f"  Unsolved: {topic_unsolved}")
            if topic_total > 0:
                topic_rate = (topic_solved / topic_total) * 100
                print(f"  Completion: {topic_rate:.1f}%")
    
    print("=" * 60 + "\n")


def main() -> None:
    """Main program loop."""
    # Configuration
    questions_folder = "questions"
    mock_exams_folder = "mock_exams"
    progress_file = "progress.json"
    
    # Create necessary directories
    Path(questions_folder).mkdir(exist_ok=True)
    Path(mock_exams_folder).mkdir(exist_ok=True)
    
    # Load question bank
    print("Loading questions from LaTeX files...")
    try:
        questions = load_questions_from_latex(questions_folder)
        question_bank = QuestionBank(questions)
        print(f"Loaded {question_bank.get_total_count()} questions from {questions_folder}/")
    except Exception as e:
        print(f"Error loading questions: {e}")
        return
    
    if question_bank.get_total_count() == 0:
        print("No questions found. Please add .tex files to the questions/ folder.")
        return
    
    # Load saved progress
    print("Loading saved progress...")
    load_progress(question_bank, progress_file)
    solved_count = question_bank.get_solved_count()
    if solved_count > 0:
        print(f"Resumed progress: {solved_count} questions already completed.")
    else:
        print("Starting fresh - no previous progress found.")
    
    # Main loop
    while True:
        try:
            print("\n" + "=" * 60)
            print("MOCK EXAM GENERATOR")
            print("=" * 60)
            print(f"Available questions: {question_bank.get_unsolved_count()}")
            print("Enter the number of questions for the mock exam (or 'q' to quit):")
            
            user_input = input().strip().lower()
            
            if user_input == 'q' or user_input == 'quit':
                print("Saving progress...")
                save_progress(question_bank, progress_file)
                print("Progress saved! Goodbye!")
                break
            
            try:
                num_questions = int(user_input)
            except ValueError:
                print("Invalid input. Please enter a number or 'q' to quit.")
                continue
            
            if num_questions <= 0:
                print("Number of questions must be positive.")
                continue
            
            # Ask if user wants one question per topic
            topics = question_bank.get_topics()
            print(f"\nAvailable topics: {len(topics)} ({', '.join(topics)})")
            print("Do you want one question per topic? (y/n, default: n):")
            one_per_topic_input = input().strip().lower()
            one_per_topic = one_per_topic_input in ['y', 'yes']
            
            if one_per_topic and num_questions > len(topics):
                print("\n" + "=" * 60)
                print("ERROR: Cannot generate exam with one question per topic")
                print("=" * 60)
                print(f"You requested: {num_questions} questions")
                print(f"Available topics: {len(topics)}")
                print(f"Topics: {', '.join(topics)}")
                print(f"\nWith one question per topic, you can request at most {len(topics)} questions.")
                print(f"Please try again with a number <= {len(topics)} or choose 'n' for normal selection.")
                print("=" * 60 + "\n")
                continue
            
            # Generate exam
            if one_per_topic:
                print(f"\nGenerating exam with {num_questions} questions (one per topic)...")
            else:
                print(f"\nGenerating exam with {num_questions} questions...")
            exam = generate_mock_exam(question_bank, num_questions, one_per_topic=one_per_topic)
            
            # Create timestamped folder
            timestamp_str = exam.timestamp.strftime("%Y-%m-%d_%H-%M-%S")
            exam_folder = Path(mock_exams_folder) / timestamp_str
            exam_folder.mkdir(exist_ok=True)
            
            # Export exam and solutions
            exam_path = exam_folder / f"exam_{timestamp_str}.tex"
            solutions_path = exam_folder / f"solutions_{timestamp_str}.tex"
            
            export_exam_to_latex(exam, str(exam_path))
            export_solutions_to_latex(exam, str(solutions_path))
            
            print(f"\nExam generated successfully!")
            print(f"Exam file: {exam_path}")
            print(f"Solutions file: {solutions_path}")
            print("\nSolve the exam now. Press Enter when finished...")
            
            # Wait for user to finish
            input()
            
            # Show statistics
            print("\nReviewing your performance...")
            review_stats(question_bank)
            
            # Save progress after each exam
            save_progress(question_bank, progress_file)
            print("Progress saved!")
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Saving progress...")
            save_progress(question_bank, progress_file)
            print("Progress saved! Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.")
    
    # Save progress one final time before exiting
    save_progress(question_bank, progress_file)


if __name__ == "__main__":
    main()

