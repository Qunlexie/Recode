#!/usr/bin/env python3
"""
Command-line interface for the coding interview revision system.
"""

import argparse
import sys
import os
from typing import Optional
from core import ProblemBank, QuizEngine


class CLIInterface:
    """Command-line interface for the quiz system."""
    
    def __init__(self, problem_bank_file: str):
        self.problem_bank = ProblemBank(problem_bank_file)
        self.quiz_engine = QuizEngine(self.problem_bank)
        self.current_mode = None
        self.current_quiz_data = None
    
    def show_welcome(self):
        """Display welcome message and available commands."""
        print("🎯 Coding Interview Revision System")
        print("=" * 50)
        print("Quick practice for core coding concepts!")
        print()
        self.show_help()
    
    def show_help(self):
        """Display help information."""
        print("Available commands:")
        print("  list                    - List all available concepts")
        print("  concepts               - Show all concepts by category")
        print("  practice <concept>     - Practice a specific concept")
        print("  random                 - Practice a random concept")
        print("  flashcard <problem_id> - Start flashcard mode")
        print("  test <problem_id>      - Start unit test mode")
        print("  explain <problem_id>   - Start explain mode")
        print("  score                  - Show current score")
        print("  help                   - Show this help")
        print("  quit                   - Exit the program")
        print()
    
    def list_concepts(self):
        """List all available concepts."""
        concepts = self.problem_bank.get_all_concepts()
        patterns = self.problem_bank.get_all_patterns()
        
        print("📚 Available Concepts:")
        for i, concept in enumerate(concepts, 1):
            print(f"  {i}. {concept}")
        
        print("\n🏷️  Available Patterns:")
        for i, pattern in enumerate(patterns, 1):
            print(f"  {i}. {pattern}")
        print()
    
    def show_concepts_by_category(self):
        """Show concepts organized by category."""
        print("📊 Concepts by Category:")
        print()
        
        # Group by data structure
        data_structures = {}
        patterns = {}
        difficulties = {}
        
        for problem in self.problem_bank.problems.values():
            ds = problem.tags.get('data_structure', 'other')
            pattern = problem.tags.get('pattern', 'other')
            difficulty = problem.tags.get('difficulty', 'unknown')
            
            if ds not in data_structures:
                data_structures[ds] = []
            if pattern not in patterns:
                patterns[pattern] = []
            if difficulty not in difficulties:
                difficulties[difficulty] = []
            
            data_structures[ds].append(problem.concept)
            patterns[pattern].append(problem.concept)
            difficulties[difficulty].append(problem.concept)
        
        print("🗂️  By Data Structure:")
        for ds, concepts in data_structures.items():
            print(f"  {ds}: {', '.join(set(concepts))}")
        
        print("\n🔄 By Pattern:")
        for pattern, concepts in patterns.items():
            print(f"  {pattern}: {', '.join(set(concepts))}")
        
        print("\n⚡ By Difficulty:")
        for diff, concepts in difficulties.items():
            print(f"  {diff}: {', '.join(set(concepts))}")
        print()
    
    def practice_concept(self, concept_name: str):
        """Practice a specific concept."""
        # Find problems with this concept
        matching_problems = [
            p for p in self.problem_bank.problems.values()
            if concept_name.lower() in p.concept.lower()
        ]
        
        if not matching_problems:
            print(f"❌ No problems found for concept: {concept_name}")
            return
        
        problem = matching_problems[0]  # Take the first match
        print(f"🎯 Practicing: {problem.title}")
        print(f"💡 Concept: {problem.concept}")
        print()
        
        # Start with flashcard mode
        self.start_flashcard_mode(problem.id)
    
    def practice_random(self):
        """Practice a random concept."""
        problem = self.problem_bank.get_random_problem()
        if not problem:
            print("❌ No problems available")
            return
        
        print(f"🎲 Random Practice: {problem.title}")
        print(f"💡 Concept: {problem.concept}")
        print()
        
        # Start with flashcard mode
        self.start_flashcard_mode(problem.id)
    
    def start_flashcard_mode(self, problem_id: str):
        """Start flashcard mode for a problem."""
        if problem_id not in self.problem_bank.problems:
            print(f"❌ Problem '{problem_id}' not found")
            return
        
        problem = self.problem_bank.problems[problem_id]
        self.current_quiz_data = self.quiz_engine.start_flashcard_mode(problem)
        self.current_mode = 'flashcard'
        
        print("🃏 FLASHCARD MODE")
        print("=" * 30)
        print(f"Problem: {self.current_quiz_data['problem_title']}")
        print(f"Concept: {self.current_quiz_data['concept']}")
        print()
        print(f"❓ {self.current_quiz_data['question']}")
        if self.current_quiz_data['context']:
            print(f"💭 Context: {self.current_quiz_data['context']}")
        print()
        print("Type your answer (or 'skip' to see the answer):")
    
    def start_unit_test_mode(self, problem_id: str):
        """Start unit test mode for a problem."""
        if problem_id not in self.problem_bank.problems:
            print(f"❌ Problem '{problem_id}' not found")
            return
        
        problem = self.problem_bank.problems[problem_id]
        self.current_quiz_data = self.quiz_engine.start_unit_test_mode(problem)
        self.current_mode = 'unit_test'
        
        print("🧪 UNIT TEST MODE")
        print("=" * 30)
        print(f"Problem: {self.current_quiz_data['problem_title']}")
        print(f"Concept: {self.current_quiz_data['concept']}")
        print()
        print(f"📝 Test Case: {self.current_quiz_data['test_input']}")
        print(f"📋 Description: {self.current_quiz_data['test_description']}")
        print(f"🎯 Expected Output: {self.current_quiz_data['expected_output']}")
        print()
        print("Modify the code snippet to handle this edge case.")
        print("Type 'show' to see the current snippet, or 'skip' to see the solution:")
    
    def start_explain_mode(self, problem_id: str):
        """Start explain mode for a problem."""
        if problem_id not in self.problem_bank.problems:
            print(f"❌ Problem '{problem_id}' not found")
            return
        
        problem = self.problem_bank.problems[problem_id]
        self.current_quiz_data = self.quiz_engine.start_explain_mode(problem)
        
        print("📚 EXPLAIN MODE")
        print("=" * 30)
        print(f"Problem: {self.current_quiz_data['problem_title']}")
        print(f"Concept: {self.current_quiz_data['concept']}")
        print()
        
        for point in self.current_quiz_data['key_points']:
            print(f"• {point}")
        print()
        
        print("📝 Code Snippet:")
        print("-" * 20)
        print(self.current_quiz_data['snippet'])
        print()
        
        if self.current_quiz_data['common_bugs']:
            print("🐛 Common Bugs to Watch For:")
            for bug in self.current_quiz_data['common_bugs']:
                print(f"  • {bug}")
            print()
        
        print("Explain how this code works out loud, then press Enter to continue.")
        input()
    
    def show_score(self):
        """Show current score."""
        summary = self.quiz_engine.get_score_summary()
        print("📊 Current Score")
        print("=" * 20)
        print(f"Correct: {summary['score']}")
        print(f"Total: {summary['total']}")
        print(f"Accuracy: {summary['accuracy']}%")
        print()
    
    def handle_flashcard_input(self, user_input: str):
        """Handle input during flashcard mode."""
        if user_input.lower() == 'skip':
            print(f"✅ Correct Answer: {self.current_quiz_data['correct_answer']}")
            print()
        else:
            result = self.quiz_engine.check_flashcard_answer(user_input)
            
            if result['correct']:
                print("✅ Correct!")
            else:
                print("❌ Incorrect!")
                print(f"Your answer: {result['user_answer']}")
                print(f"Correct answer: {result['correct_answer']}")
            
            print(f"Score: {result['score']}/{result['total']}")
            print()
        
        self.current_mode = None
        self.current_quiz_data = None
    
    def handle_unit_test_input(self, user_input: str):
        """Handle input during unit test mode."""
        if user_input.lower() == 'skip':
            problem = self.problem_bank.problems[self.current_quiz_data['problem_title'].lower().replace(' ', '_')]
            print("✅ Solution:")
            print(problem.snippet)
            print()
        elif user_input.lower() == 'show':
            problem = self.problem_bank.problems[self.current_quiz_data['problem_title'].lower().replace(' ', '_')]
            print("📝 Current Snippet:")
            print(problem.snippet)
            print()
            print("Now modify it to handle the edge case:")
            return  # Don't exit the mode
        
        self.current_mode = None
        self.current_quiz_data = None
    
    def run(self):
        """Main CLI loop."""
        self.show_welcome()
        
        while True:
            try:
                if self.current_mode == 'flashcard':
                    user_input = input("> ")
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break
                    self.handle_flashcard_input(user_input)
                    continue
                elif self.current_mode == 'unit_test':
                    user_input = input("> ")
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        break
                    self.handle_unit_test_input(user_input)
                    continue
                
                command = input("🎯 > ").strip().lower()
                
                if command in ['quit', 'exit', 'q']:
                    break
                elif command == 'help':
                    self.show_help()
                elif command == 'list':
                    self.list_concepts()
                elif command == 'concepts':
                    self.show_concepts_by_category()
                elif command == 'random':
                    self.practice_random()
                elif command == 'score':
                    self.show_score()
                elif command.startswith('practice '):
                    concept = command[9:]  # Remove 'practice '
                    self.practice_concept(concept)
                elif command.startswith('flashcard '):
                    problem_id = command[10:]  # Remove 'flashcard '
                    self.start_flashcard_mode(problem_id)
                elif command.startswith('test '):
                    problem_id = command[5:]  # Remove 'test '
                    self.start_unit_test_mode(problem_id)
                elif command.startswith('explain '):
                    problem_id = command[8:]  # Remove 'explain '
                    self.start_explain_mode(problem_id)
                else:
                    print("❓ Unknown command. Type 'help' for available commands.")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Coding Interview Revision System')
    parser.add_argument('--bank', default='problem_bank.yaml',
                       help='Path to problem bank YAML file')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.bank):
        print(f"❌ Problem bank file not found: {args.bank}")
        sys.exit(1)
    
    try:
        cli = CLIInterface(args.bank)
        cli.run()
    except Exception as e:
        print(f"❌ Failed to start CLI: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
