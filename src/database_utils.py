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
    
    conn = sqlite3.connect(DATABASE_PATH)
    # Ensure schema is up to date for existing databases
    migrate_database_schema(conn)
    return conn

def create_database_schema(conn):
    """Create the database schema if it doesn't exist."""
    cursor = conn.cursor()
    
    # Create problems table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            question TEXT,
            answer TEXT,
            solution_code TEXT,
            solution_language TEXT DEFAULT 'python',
            difficulty TEXT,
            category TEXT,
            tags TEXT,
            leetcode_link TEXT,
            leetcode_id INTEGER,
            key_idea TEXT,
            explanation TEXT,
            time_complexity TEXT,
            space_complexity TEXT,
            examples TEXT,
            constraints TEXT,
            times_reviewed INTEGER DEFAULT 0,
            success_count INTEGER DEFAULT 0,
            last_reviewed TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    # Create sessions table for persistent session storage
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            session_data TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    print("Database schema created successfully!")


def migrate_database_schema(conn):
    """Migrate existing database schema to include new columns."""
    cursor = conn.cursor()
    
    # Check if new columns exist, add them if missing
    cursor.execute("PRAGMA table_info(problems)")
    columns = [column[1] for column in cursor.fetchall()]
    
    new_columns = {
        'description': 'TEXT',
        'solution_code': 'TEXT',
        'solution_language': 'TEXT DEFAULT \'python\'',
        'examples': 'TEXT',
        'constraints': 'TEXT',
        'times_reviewed': 'INTEGER DEFAULT 0',
        'success_count': 'INTEGER DEFAULT 0',
        'last_reviewed': 'TIMESTAMP',
        'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
    }
    
    for column_name, column_type in new_columns.items():
        if column_name not in columns:
            try:
                cursor.execute(f'ALTER TABLE problems ADD COLUMN {column_name} {column_type}')
                print(f"Added column: {column_name}")
            except sqlite3.Error as e:
                print(f"Could not add column {column_name}: {e}")
    
    # Ensure sessions table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            session_data TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()


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
    """Add a custom problem to the database with automatic code formatting."""
    from code_validator import CodeValidator, ValidationLevel
    
    conn = get_connection()
    cur = conn.cursor()
    
    if tags is None:
        tags = []
    
    # Automatically format solution code if provided
    formatted_solution_code = solution_code
    if solution_code and solution_code.strip():
        try:
            validator = CodeValidator(ValidationLevel.COMPREHENSIVE)
            result = validator.validate_and_fix_code(solution_code, debug=False)
            formatted_solution_code = result.fixed_code
            print(f"✅ Auto-formatted code for problem: {title}")
        except Exception as e:
            print(f"⚠️ Could not format code for '{title}': {e}")
            # Use original code if formatting fails
            formatted_solution_code = solution_code
    
    cur.execute('''
        INSERT INTO problems 
        (title, difficulty, category, description, solution_code, tags, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    ''', (title, difficulty, category, description, formatted_solution_code, json.dumps(tags)))
    
    problem_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    return problem_id

def update_problem(problem_id: int, **kwargs):
    """Update a problem with new data and automatic code formatting."""
    from code_validator import CodeValidator, ValidationLevel
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Auto-format solution_code if it's being updated
    if 'solution_code' in kwargs and kwargs['solution_code']:
        try:
            validator = CodeValidator(ValidationLevel.COMPREHENSIVE)
            result = validator.validate_and_fix_code(kwargs['solution_code'], debug=False)
            kwargs['solution_code'] = result.fixed_code
            print(f"✅ Auto-formatted code for problem ID: {problem_id}")
        except Exception as e:
            print(f"⚠️ Could not format code for problem ID {problem_id}: {e}")
            # Keep original code if formatting fails
    
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
        if stats['times_reviewed'] and stats['times_reviewed'] > 0:
            stats['success_rate'] = (stats['success_count'] / stats['times_reviewed']) * 100
        else:
            stats['success_rate'] = 0
        return stats
    
    return {'times_reviewed': 0, 'success_count': 0, 'success_rate': 0, 'last_reviewed': None}


def get_problems_by_status(status: str) -> List[Dict]:
    """Get problems filtered by review status."""
    all_problems = get_all_problems()
    filtered_problems = []
    
    for problem in all_problems:
        stats = get_problem_stats(problem['id'])
        
        if status == "Not Seen Yet":
            # Never reviewed
            if stats['times_reviewed'] == 0:
                filtered_problems.append(problem)
        elif status == "Needs Review":
            # Has been reviewed but low success rate (or any failures)
            if stats['times_reviewed'] > 0 and stats['success_rate'] < 70:
                filtered_problems.append(problem)
        elif status == "Mastered":
            # High success rate
            if stats['times_reviewed'] > 0 and stats['success_rate'] >= 70:
                filtered_problems.append(problem)
    
    return filtered_problems


def get_dashboard_stats() -> Dict:
    """Get comprehensive dashboard statistics."""
    all_problems = get_all_problems()
    
    stats = {
        'total': len(all_problems),
        'not_seen_yet': 0,
        'needs_review': 0,
        'mastered': 0,
        'by_difficulty': {'Easy': 0, 'Medium': 0, 'Hard': 0},
        'by_category': {}
    }
    
    for problem in all_problems:
        problem_stats = get_problem_stats(problem['id'])
        
        # Status classification
        if problem_stats['times_reviewed'] == 0:
            stats['not_seen_yet'] += 1
        elif problem_stats['success_rate'] >= 70:
            stats['mastered'] += 1
        else:
            stats['needs_review'] += 1
        
        # Difficulty stats
        difficulty = problem.get('difficulty', 'Unknown')
        if difficulty in stats['by_difficulty']:
            stats['by_difficulty'][difficulty] += 1
        
        # Category stats
        category = problem.get('category', 'Unknown')
        if category not in stats['by_category']:
            stats['by_category'][category] = {'total': 0, 'not_seen': 0, 'needs_review': 0, 'mastered': 0}
        
        stats['by_category'][category]['total'] += 1
        if problem_stats['times_reviewed'] == 0:
            stats['by_category'][category]['not_seen'] += 1
        elif problem_stats['success_rate'] >= 70:
            stats['by_category'][category]['mastered'] += 1
        else:
            stats['by_category'][category]['needs_review'] += 1
    
    return stats


def save_session(session_id: str, session_data: Dict):
    """Save session data to database for persistence."""
    conn = get_connection()
    cur = conn.cursor()
    
    session_json = json.dumps(session_data)
    
    cur.execute('''
        INSERT OR REPLACE INTO sessions (session_id, session_data, last_updated)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    ''', (session_id, session_json))
    
    conn.commit()
    conn.close()


def load_session(session_id: str) -> Optional[Dict]:
    """Load session data from database."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute('''
        SELECT session_data FROM sessions 
        WHERE session_id = ?
        ORDER BY last_updated DESC
        LIMIT 1
    ''', (session_id,))
    
    row = cur.fetchone()
    conn.close()
    
    if row and row['session_data']:
        try:
            return json.loads(row['session_data'])
        except json.JSONDecodeError:
            return None
    
    return None


def clear_session(session_id: str):
    """Clear a specific session from the database."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
    
    conn.commit()
    conn.close()


def cleanup_old_sessions(days_old: int = 30):
    """Clean up sessions older than specified days."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute('''
        DELETE FROM sessions 
        WHERE last_updated < datetime('now', '-{} days')
    '''.format(days_old))
    
    deleted_count = cur.rowcount
    conn.commit()
    conn.close()
    
    return deleted_count


def fix_leetcode_links():
    """Fix existing LeetCode links by removing the numeric prefixes."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Get all problems with incorrect LeetCode links
    cur.execute('''
        SELECT id, leetcode_link, title 
        FROM problems 
        WHERE leetcode_link IS NOT NULL AND leetcode_link LIKE '%/problems/%-%-%'
    ''')
    
    problems = cur.fetchall()
    fixed_count = 0
    
    for problem in problems:
        problem_id, old_link, title = problem
        
        if old_link and '/problems/' in old_link:
            # Extract the problem slug part
            problem_part = old_link.split('/problems/')[-1].rstrip('/')
            
            # Remove numeric prefix (e.g., "0100-same-tree" -> "same-tree")
            import re
            new_slug = re.sub(r'^\d{4}-', '', problem_part)
            new_link = f"https://leetcode.com/problems/{new_slug}/"
            
            # Only update if the link actually changed
            if new_link != old_link:
                cur.execute('''
                    UPDATE problems 
                    SET leetcode_link = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_link, problem_id))
                
                fixed_count += 1
                print(f"Fixed link for '{title}': {old_link} -> {new_link}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Fixed {fixed_count} LeetCode links")
    return fixed_count


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


def reset_all_problem_stats():
    """Reset all problem statistics (times_reviewed, success_count) to 0."""
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Reset all problem statistics
        cur.execute('''
            UPDATE problems 
            SET times_reviewed = 0, 
                success_count = 0, 
                last_reviewed = NULL,
                updated_at = CURRENT_TIMESTAMP
        ''')
        
        # Clear all user_stats records
        cur.execute('DELETE FROM user_stats')
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error resetting problem stats: {e}")
        return False
    finally:
        conn.close()
