"""Main entry point for the exam generator."""
import argparse
import sys
from config import setup_logging, TRACKER_FILE
from cli import ExamGeneratorCLI
from core.persistence import ProblemTracker


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate mock exams from LaTeX problem files"
    )
    parser.add_argument(
        "--reset-tracking",
        action="store_true",
        help="Reset problem tracking (clear all used problems)"
    )
    parser.add_argument(
        "--show-stats",
        action="store_true",
        help="Show tracking statistics and exit"
    )
    
    args = parser.parse_args()
    setup_logging()
    
    # Handle reset tracking
    if args.reset_tracking:
        tracker = ProblemTracker(TRACKER_FILE)
        stats = tracker.get_stats()
        if stats["total_used"] > 0:
            tracker.reset()
            print(f"✓ Reset tracking: {stats['total_used']} problems cleared")
        else:
            print("✓ No tracked problems to reset")
        return
    
    # Handle show stats
    if args.show_stats:
        tracker = ProblemTracker(TRACKER_FILE)
        stats = tracker.get_stats()
        print(f"\nProblem Tracking Statistics:")
        print(f"  Total used: {stats['total_used']}")
        print(f"  Storage: {stats['storage_path']}")
        if stats.get('last_updated'):
            print(f"  Last updated: {stats['last_updated']}")
        return
    
    # Normal operation
    cli = ExamGeneratorCLI()
    cli.run()


if __name__ == "__main__":
    main()

