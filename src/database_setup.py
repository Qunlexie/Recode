#!/usr/bin/env python3
"""
Enhanced database setup script using the better NeetCode-Solutions repository.
This version extracts high-quality Python solutions with detailed explanations.
"""

import sqlite3
import os
import re
import json
from pathlib import Path
from textwrap import dedent

from code_validator import validate_code

def create_database():
    """Create the SQLite database with problems table."""
    conn = sqlite3.connect('recode.db')
    cur = conn.cursor()
    
    # Drop existing tables to start fresh
    cur.execute('DROP TABLE IF EXISTS problems')
    cur.execute('DROP TABLE IF EXISTS user_stats')
    
    # Create problems table with enhanced schema
    cur.execute('''
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            leetcode_id INTEGER,
            title TEXT NOT NULL,
            difficulty TEXT,
            category TEXT,
            description TEXT,
            examples TEXT,
            constraints TEXT,
            solution_code TEXT,
            solution_language TEXT DEFAULT 'python',
            explanation TEXT,
            time_complexity TEXT,
            space_complexity TEXT,
            leetcode_link TEXT,
            file_path TEXT,
            tags TEXT,  -- JSON array of tags
            times_reviewed INTEGER DEFAULT 0,
            success_count INTEGER DEFAULT 0,
            last_reviewed TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create user_stats table for tracking progress
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id INTEGER,
            session_id TEXT,
            success BOOLEAN,
            review_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (problem_id) REFERENCES problems (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Enhanced database created successfully!")

def parse_python_solution_file(file_path):
    """Parse a Python solution file to extract problem information."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract LeetCode ID from filename (e.g., 0001-two-sum.py -> 1)
        filename = os.path.basename(file_path)
        leetcode_id_match = re.search(r'^(\d+)-', filename)
        leetcode_id = int(leetcode_id_match.group(1)) if leetcode_id_match else None
        
        # Extract title from filename (e.g., 0001-two-sum.py -> Two Sum)
        title_match = re.search(r'^\d+-(.+)\.py$', filename)
        if title_match:
            title = title_match.group(1).replace('-', ' ').title()
        else:
            title = "Unknown Problem"
        
        # Extract problem description from docstring
        docstring_match = re.search(r'"""\s*Problem: (.+?)\n\n(.+?)(?=\n\nTime Complexity:|$)', content, re.DOTALL)
        if docstring_match:
            problem_title = docstring_match.group(1)
            description = docstring_match.group(2).strip()
        else:
            description = ""
        
        # Extract key idea/explanation
        explanation_match = re.search(r'Key Idea:\s*(.+?)(?=\n\nTime Complexity:|$)', content, re.DOTALL)
        explanation = explanation_match.group(1).strip() if explanation_match else ""
        
        # Extract time complexity
        time_complexity_match = re.search(r'Time Complexity:\s*(.+?)(?=\n\nSpace Complexity:|$)', content, re.DOTALL)
        time_complexity = time_complexity_match.group(1).strip() if time_complexity_match else ""
        
        # Extract space complexity
        space_complexity_match = re.search(r'Space Complexity:\s*(.+?)(?=\n\n"""|$)', content, re.DOTALL)
        space_complexity = space_complexity_match.group(1).strip() if space_complexity_match else ""
        
        # Extract the solution class without manually reformatting lines
        solution_code = ""
        class_match = re.search(r'(class Solution:[\s\S]+?)(?=\n\n"""|$)', content)
        if class_match:
            raw_code = dedent(class_match.group(1))
            solution_code = raw_code.rstrip() + "\n"
        else:
            func_match = re.search(r'(def\s+\w+.*?)(?=\n\n"""|$)', content, re.DOTALL)
            if func_match:
                raw_code = dedent(func_match.group(1))
                if not raw_code.startswith('class Solution:'):
                    solution_code = 'class Solution:\n    ' + raw_code.replace('\n', '\n    ') + "\n"
                else:
                    solution_code = raw_code.rstrip() + "\n"
            else:
                solution_code = ""

        if solution_code:
            validation_result = validate_code(solution_code)
            if validation_result.is_valid:
                solution_code = validation_result.fixed_code
            else:
                print(f"⚠️ Validation issues in {file_path}: {validation_result.errors}")
        
        return {
            'leetcode_id': leetcode_id,
            'title': title,
            'description': description,
            'explanation': explanation,
            'time_complexity': time_complexity,
            'space_complexity': space_complexity,
            'solution_code': solution_code,
            'file_path': str(file_path)
        }
    
    except Exception as e:
        print(f"❌ Error parsing {file_path}: {e}")
        return None

def get_category_from_path(file_path):
    """Extract category from file path."""
    path_parts = Path(file_path).parts
    
    # Find the category folder (usually the first numbered folder)
    for part in path_parts:
        if re.match(r'^\d+_', part):
            # Remove the number and clean up the name
            category = re.sub(r'^\d+_', '', part).replace('_', ' ')
            return category
    
    return "Misc"

def get_difficulty_from_category_and_title(category, title, leetcode_id):
    """Determine difficulty based on category patterns and LeetCode ID ranges."""
    # This is a simplified approach - in a real scenario, you might want to
    # maintain a mapping of LeetCode IDs to difficulties
    difficulty_mapping = {
        # Easy problems (common patterns)
        'contains duplicate': 'Easy',
        'valid anagram': 'Easy', 
        'two sum': 'Easy',
        'valid palindrome': 'Easy',
        'binary search': 'Easy',
        'reverse linked list': 'Easy',
        'invert binary tree': 'Easy',
        'maximum depth of binary tree': 'Easy',
        'same tree': 'Easy',
        'single number': 'Easy',
        'number of 1 bits': 'Easy',
        'counting bits': 'Easy',
        'reverse bits': 'Easy',
        'missing number': 'Easy',
        'best time to buy and sell stock': 'Easy',
        
        # Medium problems
        'group anagrams': 'Medium',
        'top k frequent elements': 'Medium',
        'product of array except self': 'Medium',
        'valid sudoku': 'Medium',
        'longest consecutive sequence': 'Medium',
        'two sum ii': 'Medium',
        '3sum': 'Medium',
        'container with most water': 'Medium',
        'longest substring without repeating characters': 'Medium',
        'longest repeating character replacement': 'Medium',
        'permutation in string': 'Medium',
        'valid parentheses': 'Medium',
        'min stack': 'Medium',
        'evaluate reverse polish notation': 'Medium',
        'generate parentheses': 'Medium',
        'daily temperatures': 'Medium',
        'search a 2d matrix': 'Medium',
        'find minimum in rotated sorted array': 'Medium',
        'search in rotated sorted array': 'Medium',
        'merge two sorted lists': 'Medium',
        'remove nth node from end of list': 'Medium',
        'copy list with random pointer': 'Medium',
        'add two numbers': 'Medium',
        'linked list cycle': 'Medium',
        'find the duplicate number': 'Medium',
        'lru cache': 'Medium',
        'merge k sorted lists': 'Medium',
        'diameter of binary tree': 'Medium',
        'balanced binary tree': 'Medium',
        'subtree of another tree': 'Medium',
        'lowest common ancestor of a binary search tree': 'Medium',
        'binary tree level order traversal': 'Medium',
        'binary tree right side view': 'Medium',
        'count good nodes in binary tree': 'Medium',
        'validate binary search tree': 'Medium',
        'kth smallest element in a bst': 'Medium',
        'construct binary tree from preorder and inorder traversal': 'Medium',
        'implement trie prefix tree': 'Medium',
        'design add and search words data structure': 'Medium',
        'kth largest element in a stream': 'Medium',
        'last stone weight': 'Medium',
        'k closest points to origin': 'Medium',
        'kth largest element in an array': 'Medium',
        'task scheduler': 'Medium',
        'find median from data stream': 'Medium',
        'subsets': 'Medium',
        'combination sum': 'Medium',
        'permutations': 'Medium',
        'subsets ii': 'Medium',
        'combination sum ii': 'Medium',
        'word search': 'Medium',
        'palindrome partitioning': 'Medium',
        'letter combinations of a phone number': 'Medium',
        'number of islands': 'Medium',
        'clone graph': 'Medium',
        'max area of island': 'Medium',
        'pacific atlantic water flow': 'Medium',
        'surrounded regions': 'Medium',
        'rotting oranges': 'Medium',
        'walls and gates': 'Medium',
        'course schedule': 'Medium',
        'course schedule ii': 'Medium',
        'redundant connection': 'Medium',
        'number of connected components in an undirected graph': 'Medium',
        'graph valid tree': 'Medium',
        'word ladder': 'Medium',
        'min cost to connect all points': 'Medium',
        'network delay time': 'Medium',
        'cheapest flights within k stops': 'Medium',
        'climbing stairs': 'Medium',
        'min cost climbing stairs': 'Medium',
        'house robber': 'Medium',
        'house robber ii': 'Medium',
        'longest palindromic substring': 'Medium',
        'palindromic substrings': 'Medium',
        'decode ways': 'Medium',
        'coin change': 'Medium',
        'maximum product subarray': 'Medium',
        'word break': 'Medium',
        'longest increasing subsequence': 'Medium',
        'partition equal subset sum': 'Medium',
        'unique paths': 'Medium',
        'longest common subsequence': 'Medium',
        'best time to buy and sell stock with cooldown': 'Medium',
        'coin change ii': 'Medium',
        'target sum': 'Medium',
        'interleaving string': 'Medium',
        'longest increasing path in a matrix': 'Medium',
        'edit distance': 'Medium',
        'maximum subarray': 'Medium',
        'jump game': 'Medium',
        'jump game ii': 'Medium',
        'gas station': 'Medium',
        'hand of straights': 'Medium',
        'valid parenthesis string': 'Medium',
        'insert interval': 'Medium',
        'merge intervals': 'Medium',
        'non overlapping intervals': 'Medium',
        'meeting rooms': 'Medium',
        'meeting rooms ii': 'Medium',
        'rotate image': 'Medium',
        'spiral matrix': 'Medium',
        'set matrix zeroes': 'Medium',
        'happy number': 'Medium',
        'plus one': 'Medium',
        'pow(x, n)': 'Medium',
        'multiply strings': 'Medium',
        'detect squares': 'Medium',
        'sum of two integers': 'Medium',
        'reverse integer': 'Medium',
        
        # Hard problems
        'trapping rain water': 'Hard',
        'minimum window substring': 'Hard',
        'sliding window maximum': 'Hard',
        'car fleet': 'Hard',
        'largest rectangle in histogram': 'Hard',
        'median of two sorted arrays': 'Hard',
        'reverse nodes in k group': 'Hard',
        'binary tree maximum path sum': 'Medium',  # Actually Medium on LeetCode
        'word search ii': 'Hard',
        'design twitter': 'Medium',  # Actually Medium on LeetCode
        'n queens': 'Hard',
        'alien dictionary': 'Hard',
        'reconstruct itinerary': 'Hard',
        'swim in rising water': 'Hard',
        'burst balloons': 'Hard',
        'regular expression matching': 'Hard',
        'minimum interval to include each query': 'Hard'
    }
    
    title_lower = title.lower()
    return difficulty_mapping.get(title_lower, 'Medium')  # Default to Medium

def import_problems_from_repo(repo_path):
    """Import all problems from the NeetCode-Solutions repository."""
    conn = sqlite3.connect('recode.db')
    cur = conn.cursor()
    
    problem_count = 0
    
    # Walk through all Python solution files
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                
                # Parse the Python solution file
                problem_data = parse_python_solution_file(file_path)
                if problem_data:
                    category = get_category_from_path(file_path)
                    difficulty = get_difficulty_from_category_and_title(
                        category, problem_data['title'], problem_data['leetcode_id']
                    )
                    
                    # Create tags array
                    tags = [difficulty, category]
                    
                    # Create LeetCode link
                    leetcode_link = ""
                    if problem_data['leetcode_id']:
                        leetcode_link = f"https://leetcode.com/problems/{problem_data['title'].lower().replace(' ', '-')}/"
                    
                    # Insert into database
                    cur.execute('''
                        INSERT INTO problems 
                        (leetcode_id, title, difficulty, category, description, examples, constraints, 
                         solution_code, solution_language, explanation, time_complexity, space_complexity,
                         leetcode_link, file_path, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        problem_data['leetcode_id'],
                        problem_data['title'],
                        difficulty,
                        category,
                        problem_data['description'],
                        "",  # examples - could be extracted from description
                        "",  # constraints - could be extracted from description
                        problem_data['solution_code'],
                        'python',
                        problem_data['explanation'],
                        problem_data['time_complexity'],
                        problem_data['space_complexity'],
                        leetcode_link,
                        problem_data['file_path'],
                        json.dumps(tags)
                    ))
                    
                    problem_count += 1
                    print(f"✅ Imported: {problem_data['title']} ({difficulty}, {category})")
    
    conn.commit()
    conn.close()
    print(f"\n🎉 Successfully imported {problem_count} problems with enhanced Python solutions!")

def main():
    """Main function to set up database and import problems."""
    print("🚀 Setting up enhanced Recode database with high-quality Python solutions...")
    
    # Create database
    create_database()
    
    # Import problems from NeetCode-Solutions repo
    repo_path = "/Users/oowola01/Library/Mobile Documents/com~apple~CloudDocs/OneDrive - Tufts/Personal Development/Coding/Code Repo/NeetCode-Solutions"
    
    if os.path.exists(repo_path):
        print(f"\n📁 Importing problems from: {repo_path}")
        import_problems_from_repo(repo_path)
    else:
        print(f"❌ Repository path not found: {repo_path}")
        print("Please update the repo_path variable in this script.")
    
    print("\n✨ Enhanced database setup complete!")
    print("You now have high-quality Python solutions with detailed explanations!")

if __name__ == "__main__":
    main()
