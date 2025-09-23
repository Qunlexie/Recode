"""
Core classes for the coding interview revision system.
"""

import yaml
import ast
import sys
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import deque
import random


@dataclass
class TestCase:
    """Represents a single test case for a problem."""
    input: str
    expected: str
    edge_case: bool = False
    description: str = ""


@dataclass
class QuizQuestion:
    """Represents a quiz question for a problem."""
    question: str
    answer: str
    context: str = ""


@dataclass
class Problem:
    """Represents a coding problem with its core concept and tests."""
    id: str
    title: str
    concept: str
    description: str
    snippet: str
    tags: Dict[str, str]
    test_cases: List[TestCase]
    common_bugs: List[str]
    quiz_questions: List[QuizQuestion]
    
    def get_concept_tags(self) -> List[str]:
        """Get list of concept tags for filtering."""
        return [f"{k}:{v}" for k, v in self.tags.items()]
    
    def get_test_input(self, test_case: TestCase) -> Tuple:
        """Parse test case input into executable format."""
        # Simple parser for common input formats
        input_str = test_case.input
        if input_str.startswith("nums="):
            # Extract array from "nums=[1,2,3]"
            array_str = input_str.split("nums=")[1].split(", target=")[0]
            nums = ast.literal_eval(array_str)
            if ", target=" in input_str:
                target = int(input_str.split("target=")[1])
                return (nums, target)
            return (nums,)
        elif input_str.startswith("root="):
            # For tree problems, we'll handle this differently
            return (None,)  # Placeholder
        return (input_str,)
    
    def execute_snippet(self, test_case: TestCase) -> str:
        """Execute the problem snippet with given test case."""
        try:
            # Create a namespace for execution
            namespace = {
                'deque': deque,
                'collections': __import__('collections'),
                'TreeNode': self._create_tree_node_class()
            }
            
            # Compile and execute the snippet
            exec(self.snippet, namespace)
            
            # Get the function name (assuming it matches the problem id)
            func_name = self.id.replace('_', '_')
            if 'two_sum' in func_name:
                func_name = 'two_sum'
            elif 'binary_search' in func_name:
                func_name = 'binary_search'
            elif 'dfs' in func_name:
                func_name = 'dfs'
            elif 'sliding_window' in func_name:
                func_name = 'max_sliding_window'
            
            if func_name not in namespace:
                return "Function not found"
            
            func = namespace[func_name]
            inputs = self.get_test_input(test_case)
            
            # Execute the function
            result = func(*inputs)
            return str(result)
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _create_tree_node_class(self):
        """Create a simple TreeNode class for tree problems."""
        class TreeNode:
            def __init__(self, val=0, left=None, right=None):
                self.val = val
                self.left = left
                self.right = right
        return TreeNode


class ProblemBank:
    """Manages the collection of problems."""
    
    def __init__(self, yaml_file: str):
        self.problems: Dict[str, Problem] = {}
        self.load_from_yaml(yaml_file)
    
    def load_from_yaml(self, yaml_file: str):
        """Load problems from YAML file."""
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
        
        for problem_data in data['problems']:
            # Convert test cases
            test_cases = [
                TestCase(
                    input=tc['input'],
                    expected=tc['expected'],
                    edge_case=tc.get('edge_case', False),
                    description=tc.get('description', '')
                )
                for tc in problem_data['test_cases']
            ]
            
            # Convert quiz questions
            quiz_questions = [
                QuizQuestion(
                    question=q['question'],
                    answer=q['answer'],
                    context=q.get('context', '')
                )
                for q in problem_data.get('quiz_questions', [])
            ]
            
            problem = Problem(
                id=problem_data['id'],
                title=problem_data['title'],
                concept=problem_data['concept'],
                description=problem_data['description'],
                snippet=problem_data['snippet'],
                tags=problem_data['tags'],
                test_cases=test_cases,
                common_bugs=problem_data.get('common_bugs', []),
                quiz_questions=quiz_questions
            )
            
            self.problems[problem.id] = problem
    
    def get_problems_by_tag(self, tag_type: str, tag_value: str) -> List[Problem]:
        """Get problems filtered by tag."""
        filtered = []
        for problem in self.problems.values():
            if problem.tags.get(tag_type) == tag_value:
                filtered.append(problem)
        return filtered
    
    def get_random_problem(self, tag_filters: Optional[Dict[str, str]] = None) -> Problem:
        """Get a random problem, optionally filtered by tags."""
        candidates = list(self.problems.values())
        
        if tag_filters:
            candidates = [
                p for p in candidates
                if all(p.tags.get(k) == v for k, v in tag_filters.items())
            ]
        
        return random.choice(candidates) if candidates else None
    
    def get_all_concepts(self) -> List[str]:
        """Get list of all unique concepts."""
        return list(set(p.concept for p in self.problems.values()))
    
    def get_all_patterns(self) -> List[str]:
        """Get list of all unique patterns."""
        patterns = set()
        for problem in self.problems.values():
            if 'pattern' in problem.tags:
                patterns.add(problem.tags['pattern'])
        return list(patterns)


class QuizEngine:
    """Handles different quiz modes."""
    
    def __init__(self, problem_bank: ProblemBank):
        self.problem_bank = problem_bank
        self.current_problem: Optional[Problem] = None
        self.score = 0
        self.total_questions = 0
    
    def start_flashcard_mode(self, problem: Problem) -> Dict[str, Any]:
        """Start flashcard mode for a problem."""
        self.current_problem = problem
        question = random.choice(problem.quiz_questions)
        
        return {
            'mode': 'flashcard',
            'problem_title': problem.title,
            'concept': problem.concept,
            'question': question.question,
            'context': question.context,
            'correct_answer': question.answer
        }
    
    def check_flashcard_answer(self, user_answer: str) -> Dict[str, Any]:
        """Check user's flashcard answer."""
        if not self.current_problem:
            return {'error': 'No active problem'}
        
        question = self.current_problem.quiz_questions[0]  # Simplified for now
        is_correct = user_answer.strip().lower() == question.answer.strip().lower()
        
        self.total_questions += 1
        if is_correct:
            self.score += 1
        
        return {
            'correct': is_correct,
            'user_answer': user_answer,
            'correct_answer': question.answer,
            'score': self.score,
            'total': self.total_questions
        }
    
    def start_unit_test_mode(self, problem: Problem) -> Dict[str, Any]:
        """Start unit test mode for a problem."""
        self.current_problem = problem
        edge_case = random.choice([tc for tc in problem.test_cases if tc.edge_case])
        
        return {
            'mode': 'unit_test',
            'problem_title': problem.title,
            'concept': problem.concept,
            'test_input': edge_case.input,
            'test_description': edge_case.description,
            'expected_output': edge_case.expected
        }
    
    def run_test_case(self, modified_snippet: str) -> Dict[str, Any]:
        """Run a test case with modified snippet."""
        if not self.current_problem:
            return {'error': 'No active problem'}
        
        # Find the current test case
        edge_cases = [tc for tc in self.current_problem.test_cases if tc.edge_case]
        if not edge_cases:
            return {'error': 'No edge cases found'}
        
        test_case = edge_cases[0]  # Simplified for now
        
        try:
            # Execute the modified snippet
            namespace = {
                'deque': deque,
                'collections': __import__('collections'),
                'TreeNode': self.current_problem._create_tree_node_class()
            }
            
            exec(modified_snippet, namespace)
            
            # Get the function and execute
            func_name = self.current_problem.id.replace('_', '_')
            if 'two_sum' in func_name:
                func_name = 'two_sum'
            elif 'binary_search' in func_name:
                func_name = 'binary_search'
            elif 'dfs' in func_name:
                func_name = 'dfs'
            elif 'sliding_window' in func_name:
                func_name = 'max_sliding_window'
            
            func = namespace[func_name]
            inputs = self.current_problem.get_test_input(test_case)
            result = func(*inputs)
            
            is_correct = str(result) == test_case.expected
            
            self.total_questions += 1
            if is_correct:
                self.score += 1
            
            return {
                'correct': is_correct,
                'result': str(result),
                'expected': test_case.expected,
                'score': self.score,
                'total': self.total_questions
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'correct': False,
                'score': self.score,
                'total': self.total_questions
            }
    
    def start_explain_mode(self, problem: Problem) -> Dict[str, Any]:
        """Start explain mode for a problem."""
        return {
            'mode': 'explain',
            'problem_title': problem.title,
            'concept': problem.concept,
            'snippet': problem.snippet,
            'common_bugs': problem.common_bugs,
            'key_points': [
                f"Pattern: {problem.tags.get('pattern', 'N/A')}",
                f"Complexity: {problem.tags.get('complexity', 'N/A')}",
                f"Data Structure: {problem.tags.get('data_structure', 'N/A')}"
            ]
        }
    
    def get_score_summary(self) -> Dict[str, Any]:
        """Get current score summary."""
        accuracy = (self.score / self.total_questions * 100) if self.total_questions > 0 else 0
        return {
            'score': self.score,
            'total': self.total_questions,
            'accuracy': round(accuracy, 1)
        }
