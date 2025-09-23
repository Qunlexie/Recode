#!/usr/bin/env python3
"""
Demo script to showcase the coding interview revision system.
"""

import os
from core import ProblemBank, QuizEngine


def demo_problem_bank():
    """Demonstrate the problem bank functionality."""
    print("🎯 Coding Interview Revision System - Demo")
    print("=" * 50)
    
    # Load the problem bank
    problem_bank = ProblemBank('problem_bank.yaml')
    
    print(f"📚 Loaded {len(problem_bank.problems)} problems")
    print()
    
    # Show available concepts
    print("Available Concepts:")
    for concept in problem_bank.get_all_concepts():
        print(f"  • {concept}")
    print()
    
    # Show available patterns
    print("Available Patterns:")
    for pattern in problem_bank.get_all_patterns():
        print(f"  • {pattern}")
    print()
    
    return problem_bank


def demo_quiz_modes(problem_bank):
    """Demonstrate different quiz modes."""
    quiz_engine = QuizEngine(problem_bank)
    
    # Get a sample problem
    problem = problem_bank.problems['two_sum']
    
    print("🃏 FLASHCARD MODE DEMO")
    print("-" * 30)
    flashcard_data = quiz_engine.start_flashcard_mode(problem)
    print(f"Problem: {flashcard_data['problem_title']}")
    print(f"Concept: {flashcard_data['concept']}")
    print(f"Question: {flashcard_data['question']}")
    print(f"Context: {flashcard_data['context']}")
    print(f"Correct Answer: {flashcard_data['correct_answer']}")
    print()
    
    print("🧪 UNIT TEST MODE DEMO")
    print("-" * 30)
    test_data = quiz_engine.start_unit_test_mode(problem)
    print(f"Problem: {test_data['problem_title']}")
    print(f"Test Input: {test_data['test_input']}")
    print(f"Expected Output: {test_data['expected_output']}")
    print(f"Description: {test_data['test_description']}")
    print()
    
    print("📚 EXPLAIN MODE DEMO")
    print("-" * 30)
    explain_data = quiz_engine.start_explain_mode(problem)
    print(f"Problem: {explain_data['problem_title']}")
    print(f"Concept: {explain_data['concept']}")
    print("Key Points:")
    for point in explain_data['key_points']:
        print(f"  • {point}")
    print("Common Bugs:")
    for bug in explain_data['common_bugs']:
        print(f"  • {bug}")
    print()


def demo_filtering(problem_bank):
    """Demonstrate problem filtering."""
    print("🔍 FILTERING DEMO")
    print("-" * 30)
    
    # Filter by difficulty
    easy_problems = problem_bank.get_problems_by_tag('difficulty', 'easy')
    print(f"Easy problems: {len(easy_problems)}")
    for problem in easy_problems:
        print(f"  • {problem.title} ({problem.concept})")
    print()
    
    # Filter by pattern
    binary_search_problems = problem_bank.get_problems_by_tag('pattern', 'binary_search')
    print(f"Binary search problems: {len(binary_search_problems)}")
    for problem in binary_search_problems:
        print(f"  • {problem.title} ({problem.concept})")
    print()
    
    # Random problem
    random_problem = problem_bank.get_random_problem()
    print(f"Random problem: {random_problem.title} ({random_problem.concept})")
    print()


def demo_execution():
    """Demonstrate code execution."""
    print("⚡ CODE EXECUTION DEMO")
    print("-" * 30)
    
    problem_bank = ProblemBank('problem_bank.yaml')
    problem = problem_bank.problems['two_sum']
    
    # Test with a simple case
    test_case = problem.test_cases[0]
    print(f"Testing: {test_case.input}")
    print(f"Expected: {test_case.expected}")
    
    result = problem.execute_snippet(test_case)
    print(f"Actual: {result}")
    
    if result == test_case.expected:
        print("✅ Test passed!")
    else:
        print("❌ Test failed!")
    print()


def main():
    """Run the complete demo."""
    if not os.path.exists('problem_bank.yaml'):
        print("❌ problem_bank.yaml not found. Please make sure it exists.")
        return
    
    try:
        # Run all demos
        problem_bank = demo_problem_bank()
        demo_quiz_modes(problem_bank)
        demo_filtering(problem_bank)
        demo_execution()
        
        print("🎉 Demo completed successfully!")
        print()
        print("Next steps:")
        print("1. Run 'python cli.py' for the command-line interface")
        print("2. Run 'streamlit run web_app.py' for the web interface")
        print("3. Add more problems to problem_bank.yaml")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == '__main__':
    main()
