#!/usr/bin/env python3
"""
Database utility functions for Recode app.
Handles all database operations for problems and user stats.
"""

import sqlite3
import json
import random
import os
from typing import List, Dict, Optional, Tuple

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'recode.db')

def get_connection():
    """Get database connection."""
    # Check if database exists, if not, create it
    if not os.path.exists(DATABASE_PATH):
        print(f"Database not found at {DATABASE_PATH}. Creating new database...")
        conn = sqlite3.connect(DATABASE_PATH)
        create_database_schema(conn)
        return conn
    return sqlite3.connect(DATABASE_PATH)

def create_database_schema(conn):
    """Create the database schema if it doesn't exist."""
    cursor = conn.cursor()
    
    # Create problems table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            question TEXT,
            answer TEXT,
            difficulty TEXT,
            category TEXT,
            tags TEXT,
            leetcode_link TEXT,
            leetcode_id INTEGER,
            key_idea TEXT,
            explanation TEXT,
            time_complexity TEXT,
            space_complexity TEXT
        )
    ''')
    
    # Create user_stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id INTEGER,
            attempts INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0,
            last_attempt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (problem_id) REFERENCES problems (id)
        )
    ''')
    
    conn.commit()
    print("Database schema created successfully!")


def get_all_problems() -> List[Dict]:
    """Get all problems from the database."""
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cur = conn.cursor()
        
        cur.execute('''
            SELECT * FROM problems 
            ORDER BY category, title
        ''')
        
        problems = []
        for row in cur.fetchall():
            problem = dict(row)
            # Parse tags JSON
            if problem['tags']:
                try:
                    problem['tags'] = json.loads(problem['tags'])
                except json.JSONDecodeError:
                    problem['tags'] = []
            else:
                problem['tags'] = []
            problems.append(problem)
        
        conn.close()
        return problems
        
    except sqlite3.Error as e:
        print(f"Database error in get_all_problems: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error in get_all_problems: {e}")
        return []

def get_random_problem() -> Optional[Dict]:
    """Get a random problem from the database."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute('''
        SELECT * FROM problems 
        ORDER BY RANDOM() 
        LIMIT 1
    ''')
    
    row = cur.fetchone()
    conn.close()
    
    if row:
        problem = dict(row)
        if problem['tags']:
            problem['tags'] = json.loads(problem['tags'])
        else:
            problem['tags'] = []
        return problem
    
    return None

def get_problem_by_id(problem_id: int) -> Optional[Dict]:
    """Get a specific problem by ID."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute('SELECT * FROM problems WHERE id = ?', (problem_id,))
    row = cur.fetchone()
    conn.close()
    
    if row:
        problem = dict(row)
        if problem['tags']:
            problem['tags'] = json.loads(problem['tags'])
        else:
            problem['tags'] = []
        return problem
    
    return None

def filter_problems(difficulty: str = None, category: str = None, tags: List[str] = None) -> List[Dict]:
    """Filter problems based on criteria."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    query = 'SELECT * FROM problems WHERE 1=1'
    params = []
    
    if difficulty and difficulty != "All":
        query += ' AND difficulty = ?'
        params.append(difficulty)
    
    if category and category != "All":
        query += ' AND category = ?'
        params.append(category)
    
    if tags:
        # For tags, we need to check JSON array
        tag_conditions = []
        for tag in tags:
            tag_conditions.append('tags LIKE ?')
            params.append(f'%"{tag}"%')
        if tag_conditions:
            query += ' AND (' + ' OR '.join(tag_conditions) + ')'
    
    query += ' ORDER BY category, title'
    
    cur.execute(query, params)
    
    problems = []
    for row in cur.fetchall():
        problem = dict(row)
        if problem['tags']:
            problem['tags'] = json.loads(problem['tags'])
        else:
            problem['tags'] = []
        problems.append(problem)
    
    conn.close()
    return problems

def get_all_categories() -> List[str]:
    """Get all unique categories."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT DISTINCT category FROM problems WHERE category IS NOT NULL ORDER BY category')
    categories = [row[0] for row in cur.fetchall()]
    
    conn.close()
    return categories

def get_all_tags() -> List[str]:
    """Get all unique tags from all problems."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT tags FROM problems WHERE tags IS NOT NULL')
    all_tags = set()
    
    for row in cur.fetchall():
        if row[0]:
            tags = json.loads(row[0])
            all_tags.update(tags)
    
    conn.close()
    return sorted(list(all_tags))

def update_problem_stats(problem_id: int, success: bool):
    """Update problem statistics after a review."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Update problem stats
    if success:
        cur.execute('''
            UPDATE problems 
            SET times_reviewed = times_reviewed + 1,
                success_count = success_count + 1,
                last_reviewed = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (problem_id,))
    else:
        cur.execute('''
            UPDATE problems 
            SET times_reviewed = times_reviewed + 1,
                last_reviewed = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (problem_id,))
    
    conn.commit()
    conn.close()

def add_custom_problem(title: str, difficulty: str, category: str, description: str, 
                      solution_code: str = "", tags: List[str] = None) -> int:
    """Add a custom problem to the database."""
    conn = get_connection()
    cur = conn.cursor()
    
    if tags is None:
        tags = []
    
    cur.execute('''
        INSERT INTO problems 
        (title, difficulty, category, description, solution_code, tags)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, difficulty, category, description, solution_code, json.dumps(tags)))
    
    problem_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    return problem_id

def update_problem(problem_id: int, **kwargs):
    """Update a problem with new data."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Build dynamic update query
    set_clauses = []
    params = []
    
    for key, value in kwargs.items():
        if key == 'tags' and isinstance(value, list):
            value = json.dumps(value)
        set_clauses.append(f"{key} = ?")
        params.append(value)
    
    if set_clauses:
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        query = f"UPDATE problems SET {', '.join(set_clauses)} WHERE id = ?"
        params.append(problem_id)
        
        cur.execute(query, params)
        conn.commit()
    
    conn.close()

def get_problem_stats(problem_id: int) -> Dict:
    """Get statistics for a specific problem."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute('''
        SELECT times_reviewed, success_count, last_reviewed
        FROM problems 
        WHERE id = ?
    ''', (problem_id,))
    
    row = cur.fetchone()
    conn.close()
    
    if row:
        stats = dict(row)
        if stats['times_reviewed'] > 0:
            stats['success_rate'] = (stats['success_count'] / stats['times_reviewed']) * 100
        else:
            stats['success_rate'] = 0
        return stats
    
    return {'times_reviewed': 0, 'success_count': 0, 'success_rate': 0, 'last_reviewed': None}

def search_problems(query: str) -> List[Dict]:
    """Search problems by title or description."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute('''
        SELECT * FROM problems 
        WHERE title LIKE ? OR description LIKE ?
        ORDER BY title
    ''', (f'%{query}%', f'%{query}%'))
    
    problems = []
    for row in cur.fetchall():
        problem = dict(row)
        if problem['tags']:
            problem['tags'] = json.loads(problem['tags'])
        else:
            problem['tags'] = []
        problems.append(problem)
    
    conn.close()
    return problems
