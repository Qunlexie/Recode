#!/usr/bin/env python3
"""
Recode - NeetCode 150 coding interview flashcard app.
Database-driven with 142+ problems and progress tracking.
"""

import streamlit as st
import time 

# Configure page layout and appearance - mobile-friendly
st.set_page_config(
    page_title="Recode - NeetCode 150",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="auto",  # Auto-collapse on mobile
    menu_items={
        'Get Help': 'https://github.com/neetcode-gh/leetcode',
        'Report a bug': None,
        'About': "Recode - Mobile-friendly NeetCode practice app"
    }
)
import random
import json
import sys
import os
import re
import ast
import black
from database_utils import (
    get_all_problems, get_random_problem, get_problem_by_id,
    filter_problems, get_all_categories, get_all_tags,
    update_problem_stats, add_custom_problem, update_problem,
    get_problem_stats, search_problems, get_dashboard_stats,
    save_session, load_session, clear_session,
    fix_leetcode_links, reset_all_problem_stats
)
from code_validator import CodeValidator, ValidationLevel
from code_masking import CodeMasker, DifficultyMode, MaskingMode
from session_manager import session_manager


@st.cache_data(ttl=600)  # Cache for 10 minutes - longer for mobile
def load_questions_cached():
    """Load questions from database with caching."""
    return get_all_problems()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_categories_and_tags():
    """Load categories and tags with caching."""
    return get_all_categories(), get_all_tags()

@st.cache_data(ttl=900)  # Cache for 15 minutes - long cache for mobile performance
def get_problem_counts():
    """Get problem count statistics with heavy caching."""
    questions = load_questions_cached()
    return {
        'total': len(questions),
        'easy': len([q for q in questions if q.get('difficulty') == 'Easy']),
        'medium': len([q for q in questions if q.get('difficulty') == 'Medium']),
        'hard': len([q for q in questions if q.get('difficulty') == 'Hard'])
    }

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_search_results(query: str):
    """Cache search results to avoid repeated database queries."""
    return search_problems(query)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_dashboard_stats():
    """Cache dashboard statistics for better performance."""
    return get_dashboard_stats()

@st.cache_data(ttl=120)  # Cache for 2 minutes (shorter due to stats changes)
def get_cached_problem_stats(problem_id: int):
    """Get problem stats with caching."""
    return get_problem_stats(problem_id)


def auto_scroll_to_top():
    """Add JavaScript to auto-scroll to top of page."""
    st.markdown("""
    <script>
        window.scrollTo(0, 0);
        // Ensure scroll happens after Streamlit renders
        setTimeout(function() { window.scrollTo(0, 0); }, 100);
    </script>
    """, unsafe_allow_html=True)


def move_to_next_problem(filtered_questions, randomize_questions):
    """Move to the next problem and reset answer state with auto-scroll."""
    # Add current question to history before moving to next
    if st.session_state.current_question_index == -1:
        # First question, add to history
        st.session_state.question_history.append(st.session_state.current_question)
        st.session_state.current_question_index = 0
    else:
        # Already have history, just increment index
        st.session_state.current_question_index += 1
    
    # Get next question based on randomization setting
    if randomize_questions:
        # Track seen questions in current filtered session
        if 'seen_in_current_filter' not in st.session_state:
            st.session_state.seen_in_current_filter = set()
        
        # Add current question to seen set
        current_id = st.session_state.current_question['id']
        st.session_state.seen_in_current_filter.add(current_id)
        
        # Find unseen questions in filtered set
        unseen_questions = [q for q in filtered_questions if q['id'] not in st.session_state.seen_in_current_filter]
        
        if unseen_questions:
            next_question = random.choice(unseen_questions)
        else:
            # All questions seen, reset and pick randomly
            st.session_state.seen_in_current_filter = set()
            next_question = random.choice(filtered_questions)
    else:
        # Sequential order - get next question in filtered list
        current_id = st.session_state.current_question['id']
        current_index = next((i for i, q in enumerate(filtered_questions) if q['id'] == current_id), 0)
        next_index = (current_index + 1) % len(filtered_questions)
        next_question = filtered_questions[next_index]
    
    st.session_state.current_question = next_question
    
    # Add to history if not already there
    if st.session_state.current_question_index >= len(st.session_state.question_history):
        st.session_state.question_history.append(next_question)
    
    # Reset answer state and increment progress
    st.session_state.show_answer = False
    st.session_state.current_question_answered = False  # Reset answered flag for new question
    st.session_state.session_progress['current'] += 1


def get_session_id():
    """Generate or retrieve a unique session ID for this browser."""
    import hashlib
    import time
    
    # Try to get session ID from browser storage using JavaScript
    session_id = st.query_params.get("session_id", None)
    
    if not session_id:
        # Generate new session ID based on timestamp and random seed
        timestamp = str(time.time())
        random_seed = str(random.randint(1000, 9999))
        session_id = hashlib.md5((timestamp + random_seed).encode()).hexdigest()[:16]
        
        # Set as query param to maintain across refreshes
        st.query_params["session_id"] = session_id
    
    return session_id


def save_persistent_session():
    """Save current session state to database."""
    session_id = get_session_id()
    
    # Extract important session state
    session_data = {
        'current_question_id': getattr(st.session_state.get('current_question', {}), 'get', lambda x, d=None: d)('id', None),
        'current_question': st.session_state.get('current_question', {}),
        'question_history': st.session_state.get('question_history', []),
        'current_question_index': st.session_state.get('current_question_index', -1),
        'show_answer': st.session_state.get('show_answer', False),
        'current_question_answered': st.session_state.get('current_question_answered', False),
        'session_progress': st.session_state.get('session_progress', {'current': 1, 'total': 1}),
        'dashboard_filter_active': st.session_state.get('dashboard_filter_active', False),
        'dashboard_filter_type': st.session_state.get('dashboard_filter_type', None),
        'last_filters': {
            'practice_mode': st.session_state.get('practice_mode_selector', 'Flashcard'),
            'randomize': st.session_state.get('randomize_questions', True),
            'enable_formatting': st.session_state.get('enable_formatting', True),
        },
        'timestamp': time.time()
    }
    
    try:
        save_session(session_id, session_data)
    except Exception as e:
        # Fail silently - don't break the app if session save fails
        print(f"Warning: Could not save session: {e}")


def load_persistent_session():
    """Load session state from database."""
    session_id = get_session_id()
    
    try:
        session_data = load_session(session_id)
        
        if session_data:
            # Restore session state
            if session_data.get('current_question'):
                st.session_state.current_question = session_data['current_question']
            
            if session_data.get('question_history'):
                st.session_state.question_history = session_data['question_history']
            
            if session_data.get('current_question_index') is not None:
                st.session_state.current_question_index = session_data['current_question_index']
            
            if session_data.get('show_answer') is not None:
                st.session_state.show_answer = session_data['show_answer']
            
            if session_data.get('current_question_answered') is not None:
                st.session_state.current_question_answered = session_data['current_question_answered']
            
            if session_data.get('session_progress'):
                st.session_state.session_progress = session_data['session_progress']
            
            if session_data.get('dashboard_filter_active') is not None:
                st.session_state.dashboard_filter_active = session_data['dashboard_filter_active']
            
            if session_data.get('dashboard_filter_type'):
                st.session_state.dashboard_filter_type = session_data['dashboard_filter_type']
            
            # Restore UI state
            last_filters = session_data.get('last_filters', {})
            if 'practice_mode' in last_filters:
                st.session_state.practice_mode_selector = last_filters['practice_mode']
            if 'randomize' in last_filters:
                st.session_state.randomize_questions = last_filters['randomize']
            if 'enable_formatting' in last_filters:
                st.session_state.enable_formatting = last_filters['enable_formatting']
            
            return True
    except Exception as e:
        print(f"Warning: Could not load session: {e}")
    
    return False


def reset_persistent_session():
    """Reset the current session and clear from database."""
    session_id = get_session_id()
    
    # Clear from database
    try:
        clear_session(session_id)
    except Exception as e:
        print(f"Warning: Could not clear session from database: {e}")
    
    # Reset all problem statistics
    try:
        reset_all_problem_stats()
        print("✅ Reset all problem statistics")
    except Exception as e:
        print(f"Warning: Could not reset problem statistics: {e}")
    
    # Clear from Streamlit session state
    keys_to_clear = [
        'current_question', 'question_history', 'current_question_index',
        'show_answer', 'current_question_answered', 'session_progress', 
        'dashboard_filter_active', 'dashboard_filter_type', 'preloaded_next_question', 
        'fill_blanks_state', 'session_loaded'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def is_valid_python(code: str) -> bool:
    """Check if Python code is syntactically valid."""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def get_python_syntax_error(code: str) -> str:
    """Get detailed syntax error information."""
    try:
        ast.parse(code)
        return "No syntax errors"
    except SyntaxError as e:
        return str(e)


def normalize_solution(code: str) -> str:
    """Normalize solution code to consistent format."""
    if not code or not code.strip():
        return code
    
    # Clean the code first
    cleaned_code = code.strip()
    
    # Check if it already has proper structure
    has_class = cleaned_code.startswith("class Solution")
    has_imports = any(cleaned_code.startswith(imp) for imp in ["from typing", "import ", "from collections"])
    
    # Only add imports if they're missing
    if not has_imports:
        imports = "from typing import List, Optional\nfrom collections import deque, defaultdict, Counter\n\n"
    else:
        imports = ""
    
    # Only add class wrapper if it's missing and the code looks like a function
    if not has_class and ("def " in cleaned_code and not cleaned_code.startswith("class ")):
        # Add class wrapper with proper indentation
        lines = cleaned_code.split('\n')
        indented_lines = []
        for line in lines:
            if line.strip():  # Only indent non-empty lines
                indented_lines.append("    " + line)
            else:
                indented_lines.append(line)
        cleaned_code = "class Solution:\n" + "\n".join(indented_lines)
    
    return imports + cleaned_code


def format_python_code(code: str, debug: bool = False) -> str:
    """Format Python code using the advanced validator system."""
    if not code:
        return code
    
    try:
        # Use the new advanced validator
        validator = CodeValidator(ValidationLevel.COMPREHENSIVE)
        result = validator.validate_and_fix_code(code, debug=debug)
        
        if debug:
            st.write("🔍 **Advanced Validation Results:**")
            st.write(f"✅ Valid: {result.is_valid}")
            if result.errors:
                st.write(f"❌ Errors: {len(result.errors)}")
                for error in result.errors:
                    st.write(f"  - {error}")
            if result.warnings:
                st.write(f"⚠️ Warnings: {len(result.warnings)}")
                for warning in result.warnings:
                    st.write(f"  - {warning}")
            if result.suggestions:
                st.write(f"💡 Suggestions: {len(result.suggestions)}")
                for suggestion in result.suggestions:
                    st.write(f"  - {suggestion}")
        
        return result.fixed_code
        
    except Exception as e:
        # Ultimate fallback - return original code if everything fails
        if debug:
            st.write(f"❌ Complete formatting failure: {str(e)}")
        return code


def _is_formatable_code(code: str) -> bool:
    """Check if code looks like it can be safely formatted."""
    if not code or not code.strip():
        return False
    
    # Check for obvious issues that would break formatting
    lines = code.split('\n')
    
    # Check for unbalanced brackets/parentheses
    open_parens = code.count('(')
    close_parens = code.count(')')
    open_braces = code.count('{')
    close_braces = code.count('}')
    open_brackets = code.count('[')
    close_brackets = code.count(']')
    
    # Allow some imbalance (not perfect but reasonable)
    if abs(open_parens - close_parens) > 2:
        return False
    if abs(open_braces - close_braces) > 1:
        return False
    if abs(open_brackets - close_brackets) > 1:
        return False
    
    # Check for obvious syntax issues
    if 'def ' in code and ':' not in code:
        return False
    
    # Check for incomplete lines (trailing commas, etc.)
    for line in lines:
        stripped = line.strip()
        if stripped.endswith(('=', '+', '-', '*', '/', ',')) and not stripped.endswith(('==', '!=', '<=', '>=')):
            return False
    
    return True


def clean_python_code(code):
    """Clean up Python code formatting issues (legacy function for compatibility)."""
    return format_python_code(code)


def extract_code_from_answer(answer_text):
    """Extract Python code from markdown answer text."""
    if not answer_text:
        return None
    
    # Find code blocks
    parts = answer_text.split('```')
    for i, part in enumerate(parts):
        if i % 2 == 1:  # This is a code block
            lines = part.split('\n', 1)
            if len(lines) > 1:
                language = lines[0].strip().lower()
                code = lines[1]
                if language in ['python', 'py', '']:
                    # Clean and return the code
                    cleaned_code = clean_python_code(code)
                    return cleaned_code.strip()
    return None


def load_questions():
    """Load questions from database."""
    return get_all_problems()


def convert_db_problem_to_question_format(problem):
    """Convert database problem format to the expected question format."""
    # Build question text from description and examples
    question_text = problem.get('description', '')
    if problem.get('examples'):
        question_text += f"\n\n**Example:**\n```\n{problem['examples']}\n```"
    if problem.get('constraints'):
        question_text += f"\n\n**Constraints:**\n{problem['constraints']}"
    
    # Build answer text with enhanced information
    answer_text = ""
    if problem.get('solution_code'):
        language = problem.get('solution_language', 'python')
        cleaned_code = clean_python_code(problem['solution_code'])
        answer_text = f"```{language}\n{cleaned_code}\n```"
        
        # Add key idea and explanation if available
        if problem.get('key_idea'):
            answer_text += f"\n\n**💡 Key Insight:**\n{problem['key_idea']}"
        elif problem.get('explanation'):
            answer_text += f"\n\n**💡 Key Insight:**\n{problem['explanation']}"
        
        # Add complexity analysis
        if problem.get('time_complexity') or problem.get('space_complexity'):
            answer_text += "\n\n**📊 Complexity Analysis:**"
            if problem.get('time_complexity'):
                answer_text += f"\n**Time:** {problem['time_complexity']}"
            if problem.get('space_complexity'):
                answer_text += f"\n**Space:** {problem['space_complexity']}"
    
    return {
        'id': problem['id'],
        'title': problem['title'],
        'question': question_text,
        'answer': answer_text,
        'tags': problem.get('tags', []),
        'difficulty': problem.get('difficulty', 'Unknown'),
        'category': problem.get('category', 'Unknown'),
        'leetcode_id': problem.get('leetcode_id'),
        'leetcode_link': problem.get('leetcode_link'),
        'type': 'Flashcard'
    }


def render_question(question_data, practice_mode, enable_formatting=True):
    """Render question based on the selected practice mode."""
    if practice_mode == 'Flashcard':
        render_flashcard(question_data, enable_formatting)
    elif practice_mode == 'Fill in the Blanks':
        render_enhanced_fill_blanks(question_data)  # Use enhanced version
    else:
        render_flashcard(question_data, enable_formatting)  # Default fallback


def render_flashcard(question_data, enable_formatting=True):
    """Render mobile-friendly flashcard question."""
    # Mobile-optimized question display
    question_text = question_data['question']
    if question_text:
        # Clean and format question text for mobile
        formatted_question = question_text.replace('\n\n', '\n').strip()
        st.markdown(formatted_question)
    
    # Compact divider
    st.markdown("---")
    
    # Mobile-friendly flashcard reveal section
    if not st.session_state.show_answer:
        # Compact info message
        st.info("💭 Think through your solution first")
        
        # Large, touch-friendly reveal button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("👁️ Reveal Answer", use_container_width=True, type="primary"):
                st.session_state.show_answer = True
                st.rerun()
    else:
        # Compact success message
        st.success("✅ Solution")
        
        # Display answer with automatic syntax highlighting
        answer_text = question_data['answer']
        if answer_text:
            # Extract and display code with enhanced styling
            code_snippet = extract_code_from_answer(answer_text)
            if code_snippet:
                if enable_formatting:
                    try:
                        # Check if debug mode is forced
                        debug_mode = st.session_state.get('force_debug', False)
                        
                        # Validate and format the code
                        formatted_code = format_python_code(code_snippet, debug=debug_mode)
                        is_valid = is_valid_python(formatted_code)
                        
                        # Enhanced code display with container
                        st.markdown("**💻 Solution Code:**")
                        
                        # Show validation status with better styling
                        if not is_valid:
                            st.markdown("""
                            <div style="
                                background: rgba(251, 191, 36, 0.1);
                                padding: 0.5rem;
                                border-radius: 6px;
                                border-left: 4px solid #f59e0b;
                                margin-bottom: 1rem;
                            ">
                                ⚠️ <strong>Code Formatting Notice:</strong> Some formatting issues detected - displaying best version
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Add a diagnostic button for problematic code
                            if st.button("🔍 Diagnose Formatting Issue", key="diagnose_formatting"):
                                st.markdown("**Diagnostic Information:**")
                                
                                # Show original code
                                st.markdown("**Original Code:**")
                                st.code(code_snippet, language="python")
                                
                                # Show formatted code
                                st.markdown("**Formatted Code:**")
                                st.code(formatted_code, language="python")
                                
                                # Try to identify the specific issue
                                syntax_error = get_python_syntax_error(formatted_code)
                                if syntax_error == "No syntax errors":
                                    st.success("✅ Formatted code is actually valid!")
                                else:
                                    st.error(f"❌ Syntax Error: {syntax_error}")
                                
                                # Also check original code
                                original_error = get_python_syntax_error(code_snippet)
                                if original_error != "No syntax errors":
                                    st.warning(f"⚠️ Original code also has issues: {original_error}")
                                
                                # Show character analysis
                                st.markdown("**Character Analysis:**")
                                st.write(f"Original length: {len(code_snippet)}")
                                st.write(f"Formatted length: {len(formatted_code)}")
                                st.write(f"Has Unicode arrows (→): {'→' in code_snippet}")
                                st.write(f"Has Unicode symbols (≠): {'≠' in code_snippet}")
                                st.write(f"Has Unicode symbols (≤): {'≤' in code_snippet}")
                                st.write(f"Has Unicode symbols (≥): {'≥' in code_snippet}")
                                
                                # Quick fix suggestions
                                st.markdown("**Quick Fix Suggestions:**")
                                if '→' in code_snippet:
                                    st.info("💡 Found Unicode arrows (→) - these should be converted to ->")
                                if '≠' in code_snippet:
                                    st.info("💡 Found Unicode not-equals (≠) - these should be converted to !=")
                                if '≤' in code_snippet or '≥' in code_snippet:
                                    st.info("💡 Found Unicode comparison symbols (≤, ≥) - these should be converted to <=, >=")
                                
                                # Check for other common issues
                                st.markdown("**Code Structure Analysis:**")
                                
                                # Check for incomplete functions
                                if 'def ' in code_snippet and ':' not in code_snippet:
                                    st.warning("⚠️ Found function definitions without colons")
                                
                                # Check for unbalanced brackets
                                open_parens = code_snippet.count('(')
                                close_parens = code_snippet.count(')')
                                open_braces = code_snippet.count('{')
                                close_braces = code_snippet.count('}')
                                open_brackets = code_snippet.count('[')
                                close_brackets = code_snippet.count(']')
                                
                                if abs(open_parens - close_parens) > 0:
                                    st.warning(f"⚠️ Unbalanced parentheses: {open_parens} open, {close_parens} close")
                                if abs(open_braces - close_braces) > 0:
                                    st.warning(f"⚠️ Unbalanced braces: {open_braces} open, {close_braces} close")
                                if abs(open_brackets - close_brackets) > 0:
                                    st.warning(f"⚠️ Unbalanced brackets: {open_brackets} open, {close_brackets} close")
                                
                                # Check for incomplete lines
                                lines = code_snippet.split('\n')
                                incomplete_lines = []
                                for i, line in enumerate(lines):
                                    stripped = line.strip()
                                    if stripped.endswith(('=', '+', '-', '*', '/', ',')) and not stripped.endswith(('==', '!=', '<=', '>=')):
                                        incomplete_lines.append(f"Line {i+1}: {stripped}")
                                
                                if incomplete_lines:
                                    st.warning("⚠️ Found potentially incomplete lines:")
                                    for line in incomplete_lines:
                                        st.write(f"  - {line}")
                                
                                # Check for missing imports
                                if 'List[' in code_snippet or 'Optional[' in code_snippet:
                                    if 'from typing import' not in code_snippet:
                                        st.info("💡 Code uses typing hints but missing 'from typing import'")
                                
                                # Check for class vs function structure
                                if 'def ' in code_snippet and not code_snippet.strip().startswith('class '):
                                    st.info("💡 Code has functions but no class wrapper - may need 'class Solution:'")
                                
                                # Show what black actually changed
                                if formatted_code != code_snippet:
                                    st.markdown("**What Black Changed:**")
                                    st.write("The formatted code is different from the original. This suggests black made formatting changes.")
                                else:
                                    st.markdown("**What Black Changed:**")
                                    st.write("The formatted code is identical to the original. Black made no changes.")
                                
                                # Show a cleaned version
                                cleaned_version = code_snippet
                                for unicode_char, replacement in [('→', '->'), ('≠', '!='), ('≤', '<='), ('≥', '>=')]:
                                    cleaned_version = cleaned_version.replace(unicode_char, replacement)
                                
                                if cleaned_version != code_snippet:
                                    st.markdown("**Cleaned Version (Unicode replaced):**")
                                    st.code(cleaned_version, language="python")
                                    
                                    cleaned_valid = is_valid_python(cleaned_version)
                                    if cleaned_valid:
                                        st.success("✅ Cleaned version is valid!")
                                    else:
                                        st.error(f"❌ Cleaned version still has issues: {get_python_syntax_error(cleaned_version)}")
                                
                                # Try a different approach - maybe the issue is with the validation function
                                st.markdown("**Validation Test:**")
                                try:
                                    # Try parsing the formatted code directly
                                    ast.parse(formatted_code)
                                    st.success("✅ Formatted code parses successfully with ast.parse()")
                                except SyntaxError as e:
                                    st.error(f"❌ Formatted code fails ast.parse(): {str(e)}")
                                    
                                    # Parse the error message to find the problematic line
                                    error_msg = str(e)
                                    if "line" in error_msg:
                                        try:
                                            # Handle different error message formats
                                            if "line" in error_msg and ")" in error_msg:
                                                # Format: "expected an indented block (<unknown>, line 5)"
                                                line_part = error_msg.split("line")[1].split(")")[0].strip()
                                                line_num = int(line_part)
                                            else:
                                                # Format: "line 5: ..."
                                                line_num = int(error_msg.split("line")[1].split()[0])
                                            st.markdown("**Problematic Line Analysis:**")
                                            st.write(f"Error on line {line_num}")
                                            
                                            # Show the problematic line and context
                                            lines = formatted_code.split('\n')
                                            if line_num <= len(lines):
                                                st.write("**Problematic line:**")
                                                st.code(lines[line_num - 1], language="python")
                                                
                                                # Show context (3 lines before and after)
                                                start = max(0, line_num - 4)
                                                end = min(len(lines), line_num + 3)
                                                context_lines = lines[start:end]
                                                st.write("**Context (with line numbers):**")
                                                for i, line in enumerate(context_lines):
                                                    line_num_display = start + i + 1
                                                    if line_num_display == line_num:
                                                        st.code(f"{line_num_display:3d} | ❌ {line}", language="text")
                                                    else:
                                                        st.code(f"{line_num_display:3d} |    {line}", language="text")
                                                
                                                # Analyze the problematic line
                                                problem_line = lines[line_num - 1]
                                                st.markdown("**Line Analysis:**")
                                                if problem_line.strip().endswith(':'):
                                                    st.warning("⚠️ Line ends with colon but next line may not be indented")
                                                elif problem_line.strip().startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except:', 'finally:', 'with ')):
                                                    st.warning("⚠️ Control structure that expects indented block")
                                                elif not problem_line.strip():
                                                    st.warning("⚠️ Empty line where indented code is expected")
                                                else:
                                                    st.info(f"ℹ️ Line content: '{problem_line.strip()}'")
                                                
                                                # Provide quick fix suggestions
                                                st.markdown("**Quick Fix Suggestions:**")
                                                if problem_line.strip().endswith(':'):
                                                    st.info("💡 **Fix:** Add indented code after the colon, or add `pass` if the block should be empty")
                                                    st.code("    pass  # Add this after the colon", language="python")
                                                elif problem_line.strip().startswith(('def ', 'class ')):
                                                    st.info("💡 **Fix:** Add `pass` or proper function body after the definition")
                                                    st.code("    pass  # Add this after the function definition", language="python")
                                                elif not problem_line.strip():
                                                    st.info("💡 **Fix:** Remove empty line or add proper indented code")
                                                
                                                # Show a potential fix
                                                st.markdown("**Potential Fix:**")
                                                fixed_lines = lines.copy()
                                                if line_num <= len(fixed_lines):
                                                    if fixed_lines[line_num - 1].strip().endswith(':'):
                                                        # Add pass after colon
                                                        fixed_lines.insert(line_num, "    pass")
                                                    elif not fixed_lines[line_num - 1].strip():
                                                        # Remove empty line
                                                        fixed_lines.pop(line_num - 1)
                                                
                                                fixed_code = '\n'.join(fixed_lines)
                                                st.code(fixed_code, language="python")
                                                
                                                # Test the fix
                                                try:
                                                    ast.parse(fixed_code)
                                                    st.success("✅ Fixed code parses successfully!")
                                                except SyntaxError as fix_error:
                                                    st.error(f"❌ Fix didn't work: {str(fix_error)}")
                                        except Exception as parse_error:
                                            st.write("Could not parse line number from error message")
                                            st.write(f"Error parsing: {parse_error}")
                                            st.write(f"Full error message: {error_msg}")
                                            
                                            # Try alternative parsing methods
                                            import re
                                            line_match = re.search(r'line\s+(\d+)', error_msg)
                                            if line_match:
                                                line_num = int(line_match.group(1))
                                                st.write(f"Found line number using regex: {line_num}")
                                                
                                                # Show the problematic line and context
                                                lines = formatted_code.split('\n')
                                                if line_num <= len(lines):
                                                    st.write("**Problematic line:**")
                                                    st.code(lines[line_num - 1], language="python")
                                                    
                                                    # Show context (3 lines before and after)
                                                    start = max(0, line_num - 4)
                                                    end = min(len(lines), line_num + 3)
                                                    context_lines = lines[start:end]
                                                    st.write("**Context (with line numbers):**")
                                                    for i, line in enumerate(context_lines):
                                                        line_num_display = start + i + 1
                                                        if line_num_display == line_num:
                                                            st.code(f"{line_num_display:3d} | ❌ {line}", language="text")
                                                        else:
                                                            st.code(f"{line_num_display:3d} |    {line}", language="text")
                                
                                # Check if the issue is with our validation function
                                if is_valid_python(formatted_code):
                                    st.info("ℹ️ Our validation function says it's valid, but we're seeing issues")
                                else:
                                    st.info("ℹ️ Our validation function correctly identified the issue")
                        
                        # Display the formatted Python code with enhanced styling
                        st.markdown("""
                        <div style="
                            background: rgba(45, 55, 75, 0.1);
                            border-radius: 8px;
                            border: 1px solid rgba(255, 107, 107, 0.2);
                            padding: 0.5rem;
                            margin: 0.5rem 0;
                            max-height: 600px;
                            overflow-y: auto;
                        ">
                        """, unsafe_allow_html=True)
                        
                        st.code(formatted_code, language="python")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Clear debug mode after use
                        if debug_mode:
                            st.session_state.force_debug = False
                    except Exception as e:
                        # If formatting completely fails, show original code with styling
                        st.markdown("""
                        <div style="
                            background: rgba(251, 191, 36, 0.1);
                            padding: 0.5rem;
                            border-radius: 6px;
                            border-left: 4px solid #f59e0b;
                            margin-bottom: 1rem;
                        ">
                            ❌ <strong>Formatting failed:</strong> Displaying original code
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.code(code_snippet, language="python")
                else:
                    # Display code as-is without formatting but with enhanced styling
                    st.markdown("""
                    <div style="
                        background: rgba(45, 55, 75, 0.1);
                        border-radius: 8px;
                        border: 1px solid rgba(255, 107, 107, 0.2);
                        padding: 0.5rem;
                        margin: 0.5rem 0;
                        max-height: 600px;
                        overflow-y: auto;
                    ">
                    """, unsafe_allow_html=True)
                    
                    st.code(code_snippet, language="python")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Display any explanatory text after the code
            parts = answer_text.split('```')
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Regular text parts
                    if part.strip():
                        st.markdown(part)
        
        # Show test results if available
            
            # Note: The solution code is already displayed above, no need to show it again


def render_enhanced_fill_blanks(question_data):
    """Render enhanced fill-in-the-blanks with dynamic blanks that change every time."""
    question_text = question_data['question']
    if question_text:
        st.markdown(question_text)
    
    st.markdown("---")
    
    # Initialize session state for fill-blanks
    if 'fill_blanks_state' not in st.session_state:
        st.session_state.fill_blanks_state = {}
    
    problem_id = question_data['id']
    state_key = f"problem_{problem_id}"
    
    # Mobile-friendly header with compact controls
    st.markdown("### 🧩 Fill-in-the-Blanks")
    
    # Mobile-responsive controls in expander to save space
    with st.expander("⚙️ Settings", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            difficulty = st.selectbox(
                "Difficulty",
                ["easy", "medium", "hard"],
                index=1,
                key=f"difficulty_{problem_id}",
                help="Easy: 1 blank, Medium: 3 blanks, Hard: 5 blanks"
            )
        
        with col2:
            masking_mode = st.selectbox(
                "Mode",
                ["mixed", "line", "token"],
                index=0,
                key=f"masking_mode_{problem_id}",
                help="Mixed: Lines + tokens, Line: Whole lines, Token: Individual words"
            )
        
        with col3:
            if st.button("🔄 New", key=f"new_blanks_{problem_id}", help="Generate new blanks", use_container_width=True):
                # Force new variation
                if state_key in st.session_state.fill_blanks_state:
                    del st.session_state.fill_blanks_state[state_key]
                st.rerun()
    
    # Extract code from answer
    code_snippet = extract_code_from_answer(question_data['answer'])
    
    if not code_snippet:
        st.warning("No code found in this problem to create blanks.")
        return
    
    # Get or create masked code
    if state_key not in st.session_state.fill_blanks_state:
        # Create new masked version with session-based seed
        difficulty_mode = DifficultyMode(difficulty)
        masking_mode_enum = MaskingMode(masking_mode)
        session_seed = session_manager.get_new_variation_seed(problem_id, difficulty)
        
        masker = CodeMasker()
        masked_result = masker.create_masked_code(code_snippet, difficulty_mode, masking_mode_enum, session_seed)
        
        st.session_state.fill_blanks_state[state_key] = {
            'masked_code': masked_result.masked_code,
            'blanks': masked_result.blanks,
            'answers': masked_result.answers,
            'difficulty': difficulty,
            'masking_mode': masking_mode,
            'user_inputs': [''] * len(masked_result.blanks),
            'submitted': False,
            'results': [],
            'session_info': session_manager.get_session_info(problem_id)
        }
    
    state = st.session_state.fill_blanks_state[state_key]
    
    # Show session info
    session_info = state['session_info']
    st.caption(f"🎯 Attempt #{session_info.get('attempt_number', 1)} • {len(state['blanks'])} blanks • Blanks change every time!")
    
    # Display masked code
    st.markdown("**💻 Code with Blanks:**")
    
    # Enhanced code display with container
    st.markdown("""
    <div style="
        background: rgba(45, 55, 75, 0.1);
        border-radius: 8px;
        border: 1px solid rgba(255, 107, 107, 0.2);
        padding: 0.5rem;
        margin: 0.5rem 0;
        max-height: 400px;
        overflow-y: auto;
    ">
    """, unsafe_allow_html=True)
    
    st.code(state['masked_code'], language="python")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Enhanced input section with better layout for line blanks
    st.markdown("**📝 Fill in the Blanks:**")
    
    # Different layouts for line vs token blanks
    line_blanks = [b for b in state['blanks'] if hasattr(b, 'is_line') and b.is_line]
    token_blanks = [b for b in state['blanks'] if not (hasattr(b, 'is_line') and b.is_line)]
    
    # Handle line blanks first (full width)
    if line_blanks:
        st.markdown("**🔍 Missing Lines:**")
        for i, blank in enumerate([b for b in state['blanks'] if hasattr(b, 'is_line') and b.is_line]):
            blank_idx = state['blanks'].index(blank)
            
            # Show context for line blanks
            if hasattr(blank, 'context_before') and blank.context_before:
                st.caption(f"Code before: `{blank.context_before}`")
            
            # Enhanced hint display for lines
            hint_text = f"{blank.hint}"
            if hasattr(blank, 'explanation') and blank.explanation:
                hint_text += f" - {blank.explanation}"
            
            state['user_inputs'][blank_idx] = st.text_area(
                f"Line [{blank.blank_id}] - {blank.category}",
                value=state['user_inputs'][blank_idx],
                key=f"line_blank_{problem_id}_{blank.blank_id}_{state['session_info']['attempt_number']}",
                help=hint_text,
                height=80,
                placeholder=f"Enter the missing {blank.category} line here..."
            )
            
            if hasattr(blank, 'context_after') and blank.context_after:
                st.caption(f"Code after: `{blank.context_after}`")
            
            # Show individual feedback if submitted
            if state['submitted'] and blank_idx < len(state['results']):
                if state['results'][blank_idx]:
                    st.success(f"✅ Correct line!")
                else:
                    st.error(f"❌ Expected: `{state['answers'][blank_idx]}`")
            
            st.markdown("---")
    
    # Handle token blanks (mobile-friendly columns)
    if token_blanks:
        st.markdown("**🎯 Missing Tokens:**")
        cols = st.columns(min(len(token_blanks), 3))  # Max 3 columns for mobile
        
        token_counter = 0
        for i, blank in enumerate(state['blanks']):
            if hasattr(blank, 'is_line') and blank.is_line:
                continue
                
            col_idx = token_counter % len(cols)
            token_counter += 1
            
            with cols[col_idx]:
                # Show hint and category
                hint_text = f"Hint: {blank.hint}" if blank.hint != '_' * len(blank.token) else f"Type: {blank.category}"
                
                state['user_inputs'][i] = st.text_input(
                    f"Token [{blank.blank_id}]",
                    value=state['user_inputs'][i],
                    key=f"token_blank_{problem_id}_{blank.blank_id}_{state['session_info']['attempt_number']}",
                    help=hint_text,
                    placeholder=f"{blank.category}"
                )
                
                # Show individual feedback if submitted
                if state['submitted'] and i < len(state['results']):
                    if state['results'][i]:
                        st.success(f"✅ Correct!")
                    else:
                        st.error(f"❌ Expected: `{state['answers'][i]}`")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔍 Check Answers", use_container_width=True, type="primary", key=f"check_{problem_id}_{state['session_info']['attempt_number']}"):
            # Check answers
            results = []
            for i, (user_input, correct_answer) in enumerate(zip(state['user_inputs'], state['answers'])):
                results.append(user_input.strip() == correct_answer.strip())
            
            state['results'] = results
            state['submitted'] = True
            
            # Calculate score
            score = sum(results)
            total = len(results)
            
            if score == total:
                st.balloons()
                st.success(f"🎉 Perfect! {score}/{total} correct!")
                # Update problem stats
                update_problem_stats(problem_id, success=True)
            else:
                st.info(f"📊 Score: {score}/{total} correct. Keep practicing!")
                if score > 0:
                    update_problem_stats(problem_id, success=False)
            
            st.rerun()
    
    with col2:
        if st.button("💡 Show Hints", use_container_width=True, key=f"hints_{problem_id}"):
            st.info("💡 Hints are shown below each input field!")
    
    with col3:
        if st.button("🔍 Show Solution", use_container_width=True, key=f"solution_{problem_id}"):
            st.session_state.show_answer = True
            st.rerun()
    
    # Show complete solution if requested
    if st.session_state.get('show_answer', False):
        st.markdown("---")
        st.success("✅ Complete Solution:")
        
        # Display the original code with enhanced styling
        st.markdown("**💻 Original Code:**")
        st.markdown("""
        <div style="
            background: rgba(34, 197, 94, 0.1);
            border-radius: 8px;
            border: 1px solid rgba(34, 197, 94, 0.2);
            padding: 0.5rem;
            margin: 0.5rem 0;
        ">
        """, unsafe_allow_html=True)
        
        st.code(code_snippet, language="python")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Show key insights if available
        if question_data.get('key_idea'):
            st.markdown("**💡 Key Insight:**")
            st.info(question_data['key_idea'])
        
        # Show complexity analysis if available
        if question_data.get('time_complexity') or question_data.get('space_complexity'):
            st.markdown("**📊 Complexity Analysis:**")
            if question_data.get('time_complexity'):
                st.write(f"**Time:** {question_data['time_complexity']}")
            if question_data.get('space_complexity'):
                st.write(f"**Space:** {question_data['space_complexity']}")


def main():
    """Simple flashcard app."""
    
    # Add custom CSS for better styling and responsiveness
    st.markdown("""
    <style>
    /* Mobile-first responsive design */
    .main > div {
        padding-top: 0.5rem;
        max-width: 100%;
    }
    
    /* Touch-friendly buttons - minimum 44px height for iOS */
    .stButton > button {
        width: 100%;
        min-height: 44px;
        border-radius: 12px;
        border: none;
        padding: 0.75rem 1rem;
        font-size: 16px;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Primary button styling */
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Code block - mobile optimized */
    .stCode {
        max-height: 300px;
        overflow-y: auto;
        border-radius: 8px;
        font-size: 14px;
    }
    
    /* Mobile-specific optimizations */
    @media (max-width: 768px) {
        .main > div {
            padding: 0.25rem 0.5rem;
        }
        
        /* Larger touch targets */
        .stButton > button {
            font-size: 16px;
            padding: 0.875rem 1rem;
            margin: 0.25rem 0;
        }
        
        /* Prevent zoom on iOS input fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {
            font-size: 16px !important;
            padding: 0.75rem;
        }
        
        /* Compact columns */
        .stColumns > div {
            padding: 0.25rem;
        }
        
        /* Responsive headers */
        h1 { font-size: 1.75rem !important; }
        h2 { font-size: 1.5rem !important; }
        h3 { font-size: 1.25rem !important; }
    }
    
    /* Extra small screens */
    @media (max-width: 480px) {
        .main > div {
            padding: 0.25rem;
        }
        
        .stButton > button {
            font-size: 15px;
            padding: 0.75rem 0.875rem;
        }
        
        .stCode {
            max-height: 250px;
            font-size: 13px;
        }
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background-color: #667eea;
        border-radius: 4px;
    }
    
    /* Better expander styling */
    .streamlit-expanderHeader {
        font-size: 16px !important;
        padding: 0.75rem !important;
        background-color: rgba(255, 107, 107, 0.05);
        border-radius: 8px;
    }
    
    /* Visual separators */
    .section-divider {
        border-top: 2px solid rgba(255, 107, 107, 0.2);
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Load questions from database (cached)
    db_problems = load_questions_cached()
    
    # Convert database format to question format
    questions = [convert_db_problem_to_question_format(p) for p in db_problems]
    
    # Get all available tags and categories (cached)
    all_categories, all_tags = load_categories_and_tags()
    
    # Enhanced header with responsive design
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; padding: 1rem;">
        <h1 style="
            color: #FF6B6B; 
            font-family: monospace; 
            font-size: clamp(2rem, 5vw, 3rem);
            margin: 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">💻 Recode</h1>
        <p style="
            color: #FAFAFA; 
            font-size: clamp(1rem, 2.5vw, 1.2rem);
            margin: 0.5rem 0;
            opacity: 0.9;
        ">Master the NeetCode 150 • Track your progress • Build confidence</p>
    </div>
    <div class="section-divider"></div>
    """, unsafe_allow_html=True)
    
    # Mobile-friendly mode switcher
    st.markdown("**📚 Practice Mode**")
    practice_mode = st.selectbox(
        "Choose your learning style:",
        ["Flashcard", "Fill in the Blanks"],
        help="💡 Flashcard: Reveal solutions • Fill Blanks: Complete code",
        label_visibility="collapsed",
        key="practice_mode_selector"
    )
    
    # Mobile-friendly toggles in columns
    col1, col2 = st.columns(2)
    with col1:
        randomize_questions = st.checkbox("🎲 Random", 
                                        value=True,
                                        help="Randomize question order")
    with col2:
        enable_formatting = st.checkbox("🎨 Format Code", 
                                      value=True,
                                      help="Auto-format code display")
    
    # Simplified sidebar for better Streamlit performance
    with st.sidebar:
        # Clickable progress stats
        dashboard_stats = get_cached_dashboard_stats()
        st.markdown("### 📊 Progress")
        
        # Top row: Total and Mastered
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"**Total**\n{dashboard_stats['total']}", use_container_width=True, key="filter_total"):
                st.session_state.dashboard_filter_active = True
                st.session_state.dashboard_filter_type = "All"
                # Reset seen questions for new filter
                st.session_state.seen_in_current_filter = set()
                st.rerun()
        with col2:
            if st.button(f"**Mastered**\n{dashboard_stats['mastered']}", use_container_width=True, key="filter_mastered"):
                st.session_state.dashboard_filter_active = True
                st.session_state.dashboard_filter_type = "Mastered"
                # Reset seen questions for new filter
                st.session_state.seen_in_current_filter = set()
                st.rerun()
        
        # Bottom row: Unseen and Needs Review
        col3, col4 = st.columns(2)
        with col3:
            if st.button(f"**Unseen**\n{dashboard_stats['not_seen_yet']}", use_container_width=True, key="filter_unseen"):
                st.session_state.dashboard_filter_active = True
                st.session_state.dashboard_filter_type = "New"
                # Reset seen questions for new filter
                st.session_state.seen_in_current_filter = set()
                st.rerun()
        with col4:
            if st.button(f"**Review**\n{dashboard_stats['needs_review']}", use_container_width=True, key="filter_review"):
                st.session_state.dashboard_filter_active = True
                st.session_state.dashboard_filter_type = "Needs Review"
                # Reset seen questions for new filter
                st.session_state.seen_in_current_filter = set()
                st.rerun()
        
        # Show active filter and clear button
        if st.session_state.get('dashboard_filter_active', False):
            filter_type = st.session_state.get('dashboard_filter_type', 'All')
            st.caption(f"🔍 Filtered by: {filter_type}")
            if st.button("❌ Clear Filter", use_container_width=True, key="clear_dashboard_filter"):
                st.session_state.dashboard_filter_active = False
                st.session_state.dashboard_filter_type = None
                st.rerun()
        
        # Simple search with caching
        st.markdown("### 🔍 Search")
        search_query = st.text_input("Search problems:", placeholder="e.g., Two Sum", key="sidebar_search")
        if search_query:
            # Use cached search results for better performance
            search_results = get_cached_search_results(search_query)
            search_questions = [convert_db_problem_to_question_format(p) for p in search_results]
            if search_questions:
                st.info(f"Found {len(search_questions)} matches")
                if st.button("Use Search Results", use_container_width=True):
                    filtered_questions = search_questions
            else:
                st.warning("No matches found")
        
        # Simple filters
        st.markdown("### 🔍 Filters")
        difficulty_options = ["All", "Easy", "Medium", "Hard"]
        selected_difficulty = st.selectbox("Difficulty", difficulty_options, key="filter_difficulty")
        
        category_options = ["All"] + all_categories
        selected_category = st.selectbox("Category", category_options, key="filter_category")
        
        status_options = ["All", "New", "Needs Review", "Mastered"]
        selected_status = st.selectbox("Status", status_options, key="filter_status")
        
        if all_tags:
            selected_tags = st.multiselect("Tags:", sorted(all_tags), key="filter_tags")
        else:
            selected_tags = []
        
        # Simple add question form with code validation
        st.markdown("### ➕ Add Question")
        with st.form("add_question"):
            title = st.text_input("Title", placeholder="e.g., Two Sum")
            question = st.text_area("Question", placeholder="Problem description...", height=80)
            answer = st.text_area("Solution", placeholder="Code solution...", height=100)
            
            # Enhanced code validation for new problems
            if answer and answer.strip():
                # Extract code from answer if it's in markdown format
                code_snippet = extract_code_from_answer(answer) or answer.strip()
                
                # Comprehensive validation check
                if code_snippet:
                    try:
                        validator = CodeValidator(ValidationLevel.COMPREHENSIVE)
                        result = validator.validate_and_fix_code(code_snippet, debug=False)
                        
                        if result.is_valid:
                            st.success("✅ Code syntax is valid and properly formatted")
                            if result.warnings:
                                st.info(f"ℹ️ Warnings: {', '.join(result.warnings)}")
                        else:
                            st.error(f"❌ Code has syntax errors: {', '.join(result.errors)}")
                            if st.button("🔧 Preview Fixed Code", key="preview_fix"):
                                st.code(result.fixed_code, language="python")
                                if result.warnings:
                                    st.info(f"Warnings: {', '.join(result.warnings)}")
                                if result.suggestions:
                                    st.info(f"Suggestions: {', '.join(result.suggestions)}")
                    except Exception as e:
                        st.error(f"Validation error: {str(e)}")
                        # Fallback to basic validation
                        is_valid = is_valid_python(code_snippet)
                        if is_valid:
                            st.success("✅ Code syntax is valid (basic check)")
                        else:
                            st.warning("⚠️ Code has syntax issues - will be auto-fixed when saved")
            
            col1, col2 = st.columns(2)
            with col1:
                difficulty = st.selectbox("Difficulty", ["", "Easy", "Medium", "Hard"], key="add_problem_difficulty")
            with col2:
                category_options = ["", "Array", "Hash Map", "Two Pointers", "Binary Search", "Tree", "Graph", "Dynamic Programming", "Greedy", "Sorting"]
                for tag in sorted(all_tags):
                    if tag not in category_options and tag not in ["Easy", "Medium", "Hard"]:
                        category_options.append(tag)
                category = st.selectbox("Category", category_options, key="add_problem_category")
            
            existing_tags = sorted([tag for tag in all_tags if tag not in ["Easy", "Medium", "Hard"]])
            if existing_tags:
                additional_tags = st.multiselect("Tags:", existing_tags)
            else:
                additional_tags = []
            
            new_tag = st.text_input("New tag:", placeholder="Type new tag")
            if new_tag and new_tag.strip():
                additional_tags.append(new_tag.strip())
            
            if st.form_submit_button("Add Question", use_container_width=True):
                if title and question and answer:
                    tags = []
                    if difficulty:
                        tags.append(difficulty)
                    if category:
                        tags.append(category)
                    if additional_tags:
                        tags.extend(additional_tags)
                    
                    # Backend will automatically format the code
                    problem_id = add_custom_problem(
                        title=title,
                        difficulty=difficulty,
                        category=category,
                        description=question,
                        solution_code=answer,
                        tags=tags
                    )
                    
                    st.success(f"Added! (ID: {problem_id})")
                    st.rerun()
                else:
                    st.error("Please fill all fields")
        
    
        # Apply filters using database functions
        filtered_db_problems = filter_problems(
            difficulty=selected_difficulty if selected_difficulty != "All" else None,
            category=selected_category if selected_category != "All" else None,
            tags=selected_tags if selected_tags else None
        )
        
        # Convert filtered database problems to question format
        filtered_questions = [convert_db_problem_to_question_format(p) for p in filtered_db_problems]
        
        # Apply status filter (post-processing) - check both sidebar filter and dashboard filter
        status_to_filter = selected_status
        if st.session_state.get('dashboard_filter_active', False):
            status_to_filter = st.session_state.get('dashboard_filter_type', selected_status)
        
        if status_to_filter != "All":
            if status_to_filter == "New":
                # Problems that haven't been reviewed
                filtered_questions = [q for q in filtered_questions if get_problem_stats(q['id'])['times_reviewed'] == 0]
            elif status_to_filter == "Needs Review":
                # Problems that have been reviewed but have low success rate
                filtered_questions = [q for q in filtered_questions if get_problem_stats(q['id'])['success_rate'] < 70]
            elif status_to_filter == "Mastered":
                # Problems with high success rate
                filtered_questions = [q for q in filtered_questions if get_problem_stats(q['id'])['success_rate'] >= 70]
    
    # Show filter results
    if len(filtered_questions) < len(questions):
        st.info(f"🔍 Showing {len(filtered_questions)} of {len(questions)} questions")
    
    # Main flashcard area
    if not filtered_questions:
        if selected_tags:
            st.warning(f"No questions found with the selected tags: {', '.join(selected_tags)}")
        else:
            st.warning("No questions available. Add some questions in the sidebar!")
        return
    
    # Initialize session state with persistence support
    session_loaded = False
    if 'session_loaded' not in st.session_state:
        # Try to load persistent session on first run
        session_loaded = load_persistent_session()
        st.session_state.session_loaded = True
    
    # Initialize missing session state values
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = random.choice(filtered_questions)
    if 'question_history' not in st.session_state:
        st.session_state.question_history = []
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = -1
    if 'current_question_answered' not in st.session_state:
        st.session_state.current_question_answered = False
    
    # Ensure current question is in the filtered set
    current_question_id = st.session_state.current_question.get('id')
    if current_question_id and not any(q['id'] == current_question_id for q in filtered_questions):
        # Current question is not in filtered set, pick a new one
        st.session_state.current_question = random.choice(filtered_questions)
        st.session_state.show_answer = False
        st.session_state.current_question_answered = False
    
    # If session was loaded, show a welcome back message
    if session_loaded:
        st.success("🎉 Welcome back! Your session has been restored.", icon="🔄")
    
    question_data = st.session_state.current_question
    
    # Add review status controls to sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("📝 Review Status Controls")
        st.info("Change the review status of the current question at any time")
        
        # Get current question stats
        current_stats = get_problem_stats(question_data['id'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Mark as Mastered", use_container_width=True):
                # Set success rate to 100% by adding successful reviews
                update_problem_stats(question_data['id'], success=True)
                st.success("Question marked as mastered! 🎉")
                st.rerun()
        
        with col2:
            if st.button("❌ Mark as Needs Review", use_container_width=True):
                # Set success rate to 0% by adding failed reviews
                update_problem_stats(question_data['id'], success=False)
                st.info("Question marked as needs review 📚")
                st.rerun()
        
        # Show current status
        st.caption(f"**Current Status:** {current_stats['times_reviewed']} reviews, {current_stats['success_rate']:.0f}% success rate")
        
        # Enhanced Code Validation Tools
        st.markdown("---")
        st.subheader("🔧 Advanced Code Tools")
        
        code_snippet = extract_code_from_answer(question_data['answer'])
        if code_snippet:
            # Validation level selector
            validation_level = st.selectbox(
                "Validation Level",
                ["Basic", "Strict", "Comprehensive"],
                index=2,
                help="Choose validation thoroughness",
                key="validation_level"
            )
            
            level_map = {
                "Basic": ValidationLevel.BASIC,
                "Strict": ValidationLevel.STRICT,
                "Comprehensive": ValidationLevel.COMPREHENSIVE
            }
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🎨 Format & Validate", use_container_width=True):
                    validator = CodeValidator(level_map[validation_level])
                    result = validator.validate_and_fix_code(code_snippet, debug=False)

                    st.markdown("**Validation Results:**")
                    if result.is_valid:
                        st.success("✅ Code is valid!")
                    else:
                        st.error(f"❌ Code has {len(result.errors)} errors")
                        for error in result.errors:
                            st.write(f"  - {error}")

                    if result.warnings:
                        st.warning(f"⚠️ {len(result.warnings)} warnings:")
                        for warning in result.warnings:
                            st.write(f"  - {warning}")

                    st.markdown("**Cleaned Code:**")
                    st.code(result.fixed_code, language="python")

                    if result.suggestions:
                        st.markdown("**Suggestions:**")
                        for suggestion in result.suggestions:
                            st.info(f"💡 {suggestion}")
            
            with col2:
                if st.button("🔍 Debug Analysis", use_container_width=True):
                    validator = CodeValidator(level_map[validation_level])
                    result = validator.validate_and_fix_code(code_snippet, debug=True)
                    
                    # Show detailed analysis
                    st.markdown("**Detailed Analysis:**")
                    st.write(f"**Original Length:** {len(code_snippet)}")
                    st.write(f"**Cleaned Length:** {len(result.fixed_code)}")
                    st.write(f"**Code Changed:** {result.fixed_code != code_snippet}")
                    
                    # Show character analysis
                    st.markdown("**Character Analysis:**")
                    unicode_chars = ['→', '≤', '≥', '≠', '∞', '∅']
                    for char in unicode_chars:
                        if char in code_snippet:
                            st.write(f"  - Found '{char}' → replaced with valid Python")
            
            # Note: Code validation and formatting now happens automatically in the backend
            st.info("ℹ️ Code validation and formatting happens automatically when problems are saved.")
            
            # Show raw code for comparison
            with st.expander("📄 Show Raw Code"):
                st.markdown("**Raw Code from Database:**")
                st.code(code_snippet, language="python")
                
                # Show character analysis
                st.markdown("**Character Analysis:**")
                st.write(f"Length: {len(code_snippet)}")
                unicode_chars = ['→', '≤', '≥', '≠', '∞', '∅', '∈', '∉', '∧', '∨', '¬']
                found_unicode = [char for char in unicode_chars if char in code_snippet]
                if found_unicode:
                    st.write(f"Found Unicode characters: {', '.join(found_unicode)}")
                else:
                    st.write("No problematic Unicode characters found")
        else:
            st.warning("No code found in current question")
        
        # Batch cleaning removed - code validation now happens automatically in backend
        st.markdown("---")
        st.info("ℹ️ **Code validation and formatting is now handled automatically** when problems are added or updated. No manual cleaning needed!")
    
    # Create responsive two-column layout
    col_main, col_meta = st.columns([3, 1], gap="large")
    
    with col_main:
        # Main problem container
        with st.container():
            # Problem header with better styling
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(255, 107, 107, 0.05));
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid #FF6B6B;
                margin-bottom: 1rem;
            ">
                <h2 style="margin: 0; color: #FF6B6B; font-size: 1.8rem;">❓ {question_data['title']}</h2>
            """, unsafe_allow_html=True)
            
            # Show position based on mode
            if randomize_questions:
                # In random mode, show session progress instead of list position
                session_position = len(st.session_state.question_history) + 1
                st.caption(f"🎲 Random mode • Question {session_position} of session")
            else:
                # In sequential mode, show position in filtered list
                current_question_id = question_data.get('id')
                current_position = 1
                if current_question_id:
                    for i, q in enumerate(filtered_questions):
                        if q['id'] == current_question_id:
                            current_position = i + 1
                            break
                st.caption(f"📍 Position: {current_position} of {len(filtered_questions)} in current filter")
            
            # Problem metadata in a clean row
            meta_col1, meta_col2, meta_col3 = st.columns([1, 1, 2])
            
            with meta_col1:
                # Display LeetCode link if available
                if question_data.get('leetcode_link'):
                    st.markdown(f"🔗 [**LeetCode**]({question_data['leetcode_link']})")
            
            with meta_col2:
                # Show difficulty prominently
                difficulty = None
                if 'tags' in question_data and question_data['tags']:
                    for tag in question_data['tags']:
                        if tag in ['Easy', 'Medium', 'Hard']:
                            difficulty = tag
                            break
                
                if difficulty:
                    difficulty_colors = {'Easy': '#22c55e', 'Medium': '#f59e0b', 'Hard': '#ef4444'}
                    color = difficulty_colors.get(difficulty, '#6b7280')
                    st.markdown(f'<span style="color: {color}; font-weight: bold;">●</span> **{difficulty}**', unsafe_allow_html=True)
            
            with meta_col3:
                # Display category and tags in a clean format
                if 'tags' in question_data and question_data['tags']:
                    tag_colors = {
                        'Easy': '🟢', 'Medium': '🟡', 'Hard': '🔴',
                        'Array': '🔵', 'Hash Map': '🟣', 'Two Pointers': '🟠',
                        'Binary Search': '🔵', 'Tree': '🟢', 'Graph': '🟣',
                        'Dynamic Programming': '🟠', 'Greedy': '🟡', 'Sorting': '🔵'
                    }
                    
                    non_difficulty_tags = [tag for tag in question_data['tags'] if tag not in ['Easy', 'Medium', 'Hard']]
                    if non_difficulty_tags:
                        tag_display = []
                        for tag in non_difficulty_tags[:3]:  # Limit to 3 main tags
                            color = tag_colors.get(tag, '⚪')
                            tag_display.append(f"{color} {tag}")
                        
                        st.markdown("**Tags:** " + " ".join(tag_display))
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Problem content area
        with st.container():
            render_question(question_data, practice_mode, enable_formatting)
    
    with col_meta:
        # Enhanced progress card
        with st.container():
            st.markdown("""
            <div style="
                background: rgba(255, 107, 107, 0.05);
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid rgba(255, 107, 107, 0.1);
                margin-bottom: 1rem;
            ">
                <h3 style="margin: 0 0 1rem 0; color: #FF6B6B;">📊 Progress</h3>
            </div>
            """, unsafe_allow_html=True)
            
        # Get problem stats from database
        stats = get_problem_stats(question_data['id'])
        
        # Display metrics in cards
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.markdown(f"""
            <div class="metric-container" style="text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; color: #FF6B6B;">{stats['times_reviewed']}</div>
                <div style="font-size: 0.8rem; opacity: 0.8;">Reviews</div>
            </div>
            """, unsafe_allow_html=True)
            
        with metric_col2:
            success_rate = (stats['success_count'] / stats['times_reviewed'] * 100) if stats['times_reviewed'] > 0 else 0
            success_color = "#22c55e" if success_rate >= 70 else "#f59e0b" if success_rate >= 40 else "#ef4444"
            st.markdown(f"""
            <div class="metric-container" style="text-align: center;">
                <div style="font-size: 2rem; font-weight: bold; color: {success_color};">{success_rate:.0f}%</div>
                <div style="font-size: 0.8rem; opacity: 0.8;">Success</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Session progress with better styling
        if 'session_progress' not in st.session_state:
            st.session_state.session_progress = {'current': 1, 'total': len(filtered_questions)}
        
        # Update total to match filtered questions and reset current position if filter changed
        if st.session_state.session_progress['total'] != len(filtered_questions):
            st.session_state.session_progress['total'] = len(filtered_questions)
            st.session_state.session_progress['current'] = 1
        
        # Calculate progress based on mode
        if randomize_questions:
            # In random mode, show session progress
            session_position = len(st.session_state.question_history) + 1
            # Estimate total based on filtered questions (could be infinite in random mode)
            estimated_total = len(filtered_questions) if len(filtered_questions) > 0 else 1
            progress = min(session_position / estimated_total, 1.0)  # Cap at 100%
            st.markdown("**Session Progress**")
            st.progress(progress)
            st.caption(f"Question {session_position} of session (🎲 Random)")
        else:
            # In sequential mode, show position in filtered list
            current_question_id = st.session_state.current_question.get('id')
            current_position = 1
            if current_question_id:
                for i, q in enumerate(filtered_questions):
                    if q['id'] == current_question_id:
                        current_position = i + 1
                        break
            
            progress = current_position / len(filtered_questions) if len(filtered_questions) > 0 else 0
            st.markdown("**Session Progress**")
            st.progress(progress)
            st.caption(f"Question {current_position} of {len(filtered_questions)}")
        
        # Session info with icons
        st.markdown("---")
        if len(st.session_state.question_history) > 0:
            st.markdown(f"📚 **History:** {len(st.session_state.question_history)} questions")
        
        mode_icon = "🎲" if randomize_questions else "📋"
        mode_text = "Random" if randomize_questions else "Sequential"
        st.markdown(f"{mode_icon} **Mode:** {mode_text}")
        
        # Action buttons with better styling
        st.markdown("---")
        st.markdown("**🎯 Actions**")
        
        # Confidence tracking (always visible, not just after revealing solution)
        if not st.session_state.get('current_question_answered', False):
            st.markdown("**How confident are you?**")
            col_success, col_fail = st.columns(2)
            with col_success:
                if st.button("✅ Got it!", use_container_width=True, type="primary"):
                    # Mark as answered to prevent multiple clicks
                    st.session_state.current_question_answered = True
                    
                    # Update problem stats
                    update_problem_stats(question_data['id'], success=True)
                    
                    # Clear related caches to show updated stats immediately
                    get_cached_problem_stats.clear()
                    get_cached_dashboard_stats.clear()
                    
                    # Automatically move to next problem
                    move_to_next_problem(filtered_questions, randomize_questions)
                    
                    # Save persistent session
                    save_persistent_session()
                    
                    # Auto-scroll to top for next problem
                    auto_scroll_to_top()
                    
                    st.success("Great job! 🎉 Moving to next problem...")
                    st.rerun()
                    
            with col_fail:
                if st.button("❌ Need review", use_container_width=True):
                    # Mark as answered to prevent multiple clicks
                    st.session_state.current_question_answered = True
                    
                    # Update problem stats
                    update_problem_stats(question_data['id'], success=False)
                    
                    # Clear related caches to show updated stats immediately
                    get_cached_problem_stats.clear()
                    get_cached_dashboard_stats.clear()
                    
                    # Automatically move to next problem
                    move_to_next_problem(filtered_questions, randomize_questions)
                    
                    # Save persistent session
                    save_persistent_session()
                    
                    # Auto-scroll to top for next problem
                    auto_scroll_to_top()
                    
                    st.info("No worries! Practice makes perfect 💪 Moving to next problem...")
                    st.rerun()
        
        # Navigation buttons
        col_back, col_next, col_reset = st.columns([1, 1, 1])
        
        with col_back:
            # Go back button (only show if there's history)
            if len(st.session_state.question_history) > 0:
                if st.button("⬅️ Back", use_container_width=True):
                    # Go back to previous question
                    st.session_state.current_question_index -= 1
                    st.session_state.current_question = st.session_state.question_history[st.session_state.current_question_index]
                    st.session_state.show_answer = False
                    st.session_state.session_progress['current'] -= 1
                    st.rerun()
            else:
                st.button("⬅️ Back", use_container_width=True, disabled=True)
        
        with col_next:
            # Check if we can go to next question
            can_go_next = True
            if randomize_questions:
                # In random mode, check if all questions in filtered set have been seen
                if 'seen_in_current_filter' not in st.session_state:
                    st.session_state.seen_in_current_filter = set()
                
                current_id = st.session_state.current_question['id']
                st.session_state.seen_in_current_filter.add(current_id)
                
                unseen_questions = [q for q in filtered_questions if q['id'] not in st.session_state.seen_in_current_filter]
                can_go_next = len(unseen_questions) > 0
            else:
                # In sequential mode, always allow next (it cycles)
                can_go_next = True
            
            # Next question button
            if st.button("➡️ Next", use_container_width=True, type="primary", disabled=not can_go_next):
                # Add current question to history before moving to next
                if st.session_state.current_question_index == -1:
                    # First question, add to history
                    st.session_state.question_history.append(st.session_state.current_question)
                    st.session_state.current_question_index = 0
                else:
                    # Already have history, just increment index
                    st.session_state.current_question_index += 1
                
                # Get next question based on randomization setting
                if randomize_questions:
                    # Track seen questions in current filtered session
                    if 'seen_in_current_filter' not in st.session_state:
                        st.session_state.seen_in_current_filter = set()
                    
                    # Add current question to seen set
                    current_id = st.session_state.current_question['id']
                    st.session_state.seen_in_current_filter.add(current_id)
                    
                    # Find unseen questions in filtered set
                    unseen_questions = [q for q in filtered_questions if q['id'] not in st.session_state.seen_in_current_filter]
                    
                    if unseen_questions:
                        next_question = random.choice(unseen_questions)
                    else:
                        # All questions seen, reset and pick randomly
                        st.session_state.seen_in_current_filter = set()
                        next_question = random.choice(filtered_questions)
                else:
                    # Sequential order - get next question in filtered list
                    current_id = st.session_state.current_question['id']
                    current_index = next((i for i, q in enumerate(filtered_questions) if q['id'] == current_id), 0)
                    next_index = (current_index + 1) % len(filtered_questions)
                    next_question = filtered_questions[next_index]
                
                st.session_state.current_question = next_question
                
                # Add to history if not already there
                if st.session_state.current_question_index >= len(st.session_state.question_history):
                    st.session_state.question_history.append(next_question)
                
                st.session_state.show_answer = False
                st.session_state.session_progress['current'] += 1
                st.rerun()
        
        with col_reset:
            # Reset navigation button
            if st.button("🔄 Reset Session", use_container_width=True):
                # Reset persistent session
                reset_persistent_session()
                
                # Clear cached dashboard stats to show updated progress immediately
                get_cached_dashboard_stats.clear()
                get_cached_problem_stats.clear()
                
                # Initialize fresh session
                st.session_state.question_history = []
                st.session_state.current_question_index = -1
                st.session_state.current_question = random.choice(filtered_questions)
                st.session_state.show_answer = False
                st.session_state.current_question_answered = False
                st.session_state.session_progress = {'current': 1, 'total': len(filtered_questions)}
                st.success("🔄 Session reset! All progress cleared. Starting fresh.")
                st.rerun()
    
    # Edit question button (moved to left column)
    with col1:
        if st.button("✏️ Edit This Question", use_container_width=True):
            st.session_state.edit_mode = True
            st.session_state.editing_question = question_data
            st.rerun()
        
        # Enrichment button
        if st.button("✨ Improve This Problem", use_container_width=True):
            st.session_state.enrich_mode = True
            st.session_state.enriching_question = question_data
            st.rerun()
    
    # Edit mode
    if st.session_state.get('edit_mode', False):
        editing_question = st.session_state.editing_question
        
        st.markdown("---")
        st.subheader("✏️ Edit Question")
        
        with st.form("edit_question"):
            new_title = st.text_input("Question Title", value=editing_question['title'])
            new_question = st.text_area("Question", value=editing_question['question'], height=200)
            new_answer = st.text_area("Answer", value=editing_question['answer'], height=200)
            
            # Edit tags
            st.write("**Edit Tags:**")
            current_tags = editing_question.get('tags', [])
            
            # Use the already calculated all_tags
            
            col1, col2 = st.columns(2)
            with col1:
                current_difficulty = next((tag for tag in current_tags if tag in ["Easy", "Medium", "Hard"]), "")
                difficulty = st.selectbox("Difficulty", ["", "Easy", "Medium", "Hard"], 
                                        index=["", "Easy", "Medium", "Hard"].index(current_difficulty) if current_difficulty else 0,
                                        key="edit_problem_difficulty")
            with col2:
                category_options = ["", "Array", "Hash Map", "Two Pointers", "Binary Search", "Tree", "Graph", "Dynamic Programming", "Greedy", "Sorting"]
                # Add existing custom categories
                for tag in sorted(all_tags):
                    if tag not in category_options and tag not in ["Easy", "Medium", "Hard"]:
                        category_options.append(tag)
                current_category = next((tag for tag in current_tags if tag in category_options), "")
                category = st.selectbox("Category", category_options,
                                      index=category_options.index(current_category) if current_category else 0,
                                      key="edit_problem_category")
            
            # Additional tags
            existing_tags = sorted([tag for tag in all_tags if tag not in ["Easy", "Medium", "Hard"]])
            current_additional = [tag for tag in current_tags if tag not in ["Easy", "Medium", "Hard"] and tag in existing_tags]
            if existing_tags:
                additional_tags = st.multiselect("Additional Tags:", existing_tags, default=current_additional)
            else:
                additional_tags = []
            
            # New tag
            other_tags = [tag for tag in current_tags if tag not in ["Easy", "Medium", "Hard"] and tag not in existing_tags]
            new_tag = st.text_input("Add new tag:", value=", ".join(other_tags) if other_tags else "", 
                                  placeholder="Type a new tag name")
            if new_tag and new_tag.strip():
                additional_tags.extend([tag.strip() for tag in new_tag.split(",") if tag.strip()])
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                    # Build new tags list
                    new_tags = []
                    if difficulty:
                        new_tags.append(difficulty)
                    if category:
                        new_tags.append(category)
                    if additional_tags:
                        new_tags.extend(additional_tags)
                    
                    # Update the problem in the database
                    update_problem(editing_question['id'], 
                                 title=new_title,
                                 description=new_question,
                                 solution_code=new_answer,
                                 tags=new_tags)
                    
                    st.session_state.edit_mode = False
                    st.session_state.current_question = {
                        'title': new_title,
                        'question': new_question,
                        'answer': new_answer,
                        'tags': new_tags
                    }
                    st.success("Question updated!")
                    st.rerun()
            
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.edit_mode = False
                    st.rerun()
    
    # Enrichment mode
    if st.session_state.get('enrich_mode', False):
        enriching_question = st.session_state.enriching_question
        
        st.markdown("---")
        st.subheader("✨ Improve Problem")
        st.info("Help improve this problem by adding better examples, test cases, or explanations!")
        
        with st.form("enrich_question"):
            st.write(f"**Current Problem:** {enriching_question['title']}")
            
            # Current content display
            with st.expander("📝 Current Problem Content"):
                st.write("**Description:**")
                st.write(enriching_question['question'])
                st.write("**Solution:**")
                st.write(enriching_question['answer'])
            
            # Enrichment options
            st.write("**What would you like to improve?**")
            
            col1, col2 = st.columns(2)
            with col1:
                improve_examples = st.checkbox("Add Better Examples")
                improve_explanation = st.checkbox("Improve Explanation")
            with col2:
                improve_test_cases = st.checkbox("Add Test Cases")
                improve_solution = st.checkbox("Improve Solution Code")
            
            # Input fields based on selections
            new_examples = ""
            new_explanation = ""
            new_test_cases = ""
            new_solution = ""
            
            if improve_examples:
                new_examples = st.text_area("Better Examples:", 
                    placeholder="Add more comprehensive examples with expected outputs...")
            
            if improve_explanation:
                new_explanation = st.text_area("Improved Explanation:", 
                    placeholder="Add step-by-step explanation or algorithm approach...")
            
            if improve_test_cases:
                new_test_cases = st.text_area("Test Cases:", 
                    placeholder="Add edge cases and test scenarios...")
            
            if improve_solution:
                new_solution = st.text_area("Improved Solution:", 
                    placeholder="Add better solution code with comments...")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("💾 Save Improvements", use_container_width=True):
                    # Update the problem with improvements
                    updates = {}
                    
                    if new_examples:
                        current_desc = enriching_question['question']
                        updates['description'] = current_desc + f"\n\n**Additional Examples:**\n{new_examples}"
                    
                    if new_explanation:
                        current_desc = updates.get('description', enriching_question['question'])
                        updates['description'] = current_desc + f"\n\n**Explanation:**\n{new_explanation}"
                    
                    if new_test_cases:
                        current_desc = updates.get('description', enriching_question['question'])
                        updates['description'] = current_desc + f"\n\n**Test Cases:**\n{new_test_cases}"
                    
                    if new_solution:
                        updates['solution_code'] = new_solution
                    
                    if updates:
                        update_problem(enriching_question['id'], **updates)
                        st.success("✨ Problem improved successfully!")
                        st.session_state.enrich_mode = False
                        st.rerun()
                    else:
                        st.warning("Please select at least one improvement option.")
            
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.enrich_mode = False
                    st.rerun()


# Run main function
if __name__ == '__main__':
    main()
