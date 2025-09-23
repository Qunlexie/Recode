#!/usr/bin/env python3
"""
Simple test suite for the coding interview revision system.
"""

import sys
import os
from core import ProblemBank, QuizEngine


def test_problem_bank_loading():
    """Test that the problem bank loads correctly."""
    print("🧪 Testing problem bank loading...")
    
    try:
        problem_bank = ProblemBank('problem_bank.yaml')
        assert len(problem_bank.problems) > 0, "No problems loaded"
        
        # Check that we have the expected problems
        expected_problems = ['two_sum', 'binary_search', 'dfs_traversal', 'sliding_window']
        for problem_id in expected_problems:
            assert problem_id in problem_bank.problems, f"Missing problem: {problem_id}"
        
        print("✅ Problem bank loading test passed")
        return True
        
    except Exception as e:
        print(f"❌ Problem bank loading test failed: {e}")
        return False


def test_quiz_engine():
    """Test the quiz engine functionality."""
    print("🧪 Testing quiz engine...")
    
    try:
        problem_bank = ProblemBank('problem_bank.yaml')
        quiz_engine = QuizEngine(problem_bank)
        
        # Test flashcard mode
        problem = problem_bank.problems['two_sum']
        flashcard_data = quiz_engine.start_flashcard_mode(problem)
        assert 'question' in flashcard_data, "Flashcard data missing question"
        assert 'correct_answer' in flashcard_data, "Flashcard data missing answer"
        
        # Test unit test mode
        test_data = quiz_engine.start_unit_test_mode(problem)
        assert 'test_input' in test_data, "Unit test data missing input"
        assert 'expected_output' in test_data, "Unit test data missing expected output"
        
        # Test explain mode
        explain_data = quiz_engine.start_explain_mode(problem)
        assert 'snippet' in explain_data, "Explain data missing snippet"
        assert 'common_bugs' in explain_data, "Explain data missing bugs"
        
        print("✅ Quiz engine test passed")
        return True
        
    except Exception as e:
        print(f"❌ Quiz engine test failed: {e}")
        return False


def test_problem_filtering():
    """Test problem filtering functionality."""
    print("🧪 Testing problem filtering...")
    
    try:
        problem_bank = ProblemBank('problem_bank.yaml')
        
        # Test filtering by difficulty
        easy_problems = problem_bank.get_problems_by_tag('difficulty', 'easy')
        assert len(easy_problems) > 0, "No easy problems found"
        
        # Test filtering by pattern
        binary_search_problems = problem_bank.get_problems_by_tag('pattern', 'binary_search')
        assert len(binary_search_problems) > 0, "No binary search problems found"
        
        # Test random problem selection
        random_problem = problem_bank.get_random_problem()
        assert random_problem is not None, "Random problem selection failed"
        
        print("✅ Problem filtering test passed")
        return True
        
    except Exception as e:
        print(f"❌ Problem filtering test failed: {e}")
        return False


def test_concept_retrieval():
    """Test concept and pattern retrieval."""
    print("🧪 Testing concept retrieval...")
    
    try:
        problem_bank = ProblemBank('problem_bank.yaml')
        
        concepts = problem_bank.get_all_concepts()
        assert len(concepts) > 0, "No concepts found"
        
        patterns = problem_bank.get_all_patterns()
        assert len(patterns) > 0, "No patterns found"
        
        # Check that we have expected concepts
        expected_concepts = ['Hash Map Lookup', 'Mid Calculation & Bounds Update']
        for concept in expected_concepts:
            assert concept in concepts, f"Missing expected concept: {concept}"
        
        print("✅ Concept retrieval test passed")
        return True
        
    except Exception as e:
        print(f"❌ Concept retrieval test failed: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("🎯 Running Coding Interview Revision System Tests")
    print("=" * 60)
    
    tests = [
        test_problem_bank_loading,
        test_quiz_engine,
        test_problem_filtering,
        test_concept_retrieval
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("📊 Test Results")
    print("=" * 20)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
