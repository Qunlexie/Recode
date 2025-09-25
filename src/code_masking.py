#!/usr/bin/env python3
"""
Intelligent code masking system for Fill-in-the-Blanks mode.
Creates meaningful blanks in Python code for learning purposes.
"""

import ast
import re
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class DifficultyMode(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class MaskingMode(Enum):
    TOKEN = "token"  # Mask individual tokens (current behavior)
    LINE = "line"    # Mask entire lines
    MIXED = "mixed"  # Mix of tokens and lines

@dataclass
class BlankInfo:
    """Information about a blank in the code."""
    position: int      # Character position in original code
    length: int        # Length of original token/line
    token: str         # Original token or line content
    hint: str          # Hint for the blank
    category: str      # Type of token/line (keyword, variable, operator, logic, etc.)
    blank_id: int      # Numbered blank identifier
    is_line: bool = False      # True if this is a whole line blank
    line_number: int = 0       # Line number (for line blanks)
    context_before: str = ""   # Code context before the blank
    context_after: str = ""    # Code context after the blank
    explanation: str = ""      # Educational explanation of what's missing

@dataclass
class MaskedCode:
    """Result of code masking operation."""
    masked_code: str
    blanks: List[BlankInfo]
    answers: List[str]
    difficulty: DifficultyMode
    masking_mode: MaskingMode

class CodeMasker:
    """Intelligent code masking for educational purposes."""
    
    def __init__(self):
        # Define token categories and their importance for learning
        self.important_keywords = {
            'if', 'else', 'elif', 'for', 'while', 'return', 'def', 'class',
            'try', 'except', 'with', 'import', 'from', 'as', 'in', 'not',
            'and', 'or', 'is', 'None', 'True', 'False', 'break', 'continue'
        }
        
        self.operators = {
            '==', '!=', '<=', '>=', '<', '>', '+', '-', '*', '/', '//', '%',
            '=', '+=', '-=', '*=', '/=', '&', '|', '^', '~', '<<', '>>'
        }
        
        self.data_structures = {
            'list', 'dict', 'set', 'tuple', 'str', 'int', 'float', 'bool'
        }
        
        self.common_methods = {
            'append', 'pop', 'insert', 'remove', 'sort', 'reverse',
            'get', 'keys', 'values', 'items', 'add', 'update',
            'split', 'join', 'replace', 'strip', 'lower', 'upper',
            'len', 'range', 'enumerate', 'zip', 'map', 'filter'
        }

    def get_blank_count_for_difficulty(self, difficulty: DifficultyMode, max_possible: int) -> int:
        """Get number of blanks based on difficulty level."""
        if difficulty == DifficultyMode.EASY:
            return min(1, max_possible)
        elif difficulty == DifficultyMode.MEDIUM:
            return min(3, max_possible)
        else:  # HARD
            return min(5, max_possible)

    def analyze_code_tokens(self, code: str) -> List[Dict]:
        """Analyze code and identify maskable tokens with their importance."""
        tokens = []
        
        # Use regex to find meaningful tokens
        token_patterns = [
            (r'\b(?:if|else|elif|for|while|return|def|class|try|except|with|import|from|as|in|not|and|or|is|None|True|False|break|continue)\b', 'keyword', 10),
            (r'\b(?:list|dict|set|tuple|str|int|float|bool)\b', 'data_structure', 8),
            (r'\b(?:append|pop|insert|remove|sort|reverse|get|keys|values|items|add|update|split|join|replace|strip|lower|upper|len|range|enumerate|zip|map|filter)\b', 'method', 7),
            (r'(?:==|!=|<=|>=|<|>|\+=|-=|\*=|/=)', 'operator', 6),
            (r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', 'variable', 3),
            (r'\b\d+\b', 'number', 4),
            (r'[+\-*/]', 'arithmetic', 5)
        ]
        
        for pattern, category, importance in token_patterns:
            for match in re.finditer(pattern, code):
                tokens.append({
                    'start': match.start(),
                    'end': match.end(),
                    'token': match.group(),
                    'category': category,
                    'importance': importance,
                    'hint': self._generate_hint(match.group(), category)
                })
        
        # Sort by position and remove overlaps
        tokens.sort(key=lambda x: x['start'])
        filtered_tokens = []
        last_end = 0
        
        for token in tokens:
            if token['start'] >= last_end:
                filtered_tokens.append(token)
                last_end = token['end']
        
        return filtered_tokens

    def analyze_code_lines(self, code: str) -> List[Dict]:
        """Analyze code lines and identify which lines are good candidates for masking."""
        lines = code.split('\n')
        line_info = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue  # Skip empty lines and comments
            
            # Categorize lines by their purpose and importance
            importance = self._get_line_importance(stripped, i, lines)
            category = self._categorize_line(stripped)
            explanation = self._explain_line_purpose(stripped, category)
            
            line_info.append({
                'line_number': i,
                'content': line,
                'stripped': stripped,
                'category': category,
                'importance': importance,
                'explanation': explanation
            })
        
        return line_info
    
    def _get_line_importance(self, line: str, line_idx: int, all_lines: List[str]) -> int:
        """Rate the importance of a line for educational purposes (1-10)."""
        line = line.strip()
        
        # High importance (8-10): Key algorithmic steps
        if any(keyword in line for keyword in ['return', 'if', 'while', 'for']):
            return 9
        elif any(keyword in line for keyword in ['else:', 'elif']):
            return 8
        elif line.endswith(':') and ('def ' in line or 'class ' in line):
            return 7  # Function/class definitions are important but structural
        
        # Medium importance (5-7): Logic and operations
        elif '=' in line and not line.startswith('def '):
            if any(op in line for op in ['+=', '-=', '*=', '/=']):
                return 7  # Compound assignments
            else:
                return 6  # Regular assignments
        elif any(method in line for method in ['.append', '.pop', '.insert', '.remove']):
            return 7  # Data structure operations
        
        # Lower importance (3-5): Setup and simple operations
        elif 'import' in line or 'from' in line:
            return 3  # Imports are structural
        elif line.strip() == 'pass':
            return 2
        else:
            return 5  # Default medium importance
    
    def _categorize_line(self, line: str) -> str:
        """Categorize a line of code by its purpose."""
        line = line.strip()
        
        if line.startswith('def ') or line.startswith('class '):
            return 'definition'
        elif line.startswith('if ') or line.startswith('elif '):
            return 'conditional'
        elif line.startswith('else:'):
            return 'else_clause'
        elif line.startswith('for ') or line.startswith('while '):
            return 'loop'
        elif line.startswith('return '):
            return 'return_statement'
        elif '=' in line and not any(op in line for op in ['==', '!=', '<=', '>=']):
            return 'assignment'
        elif any(method in line for method in ['.append', '.pop', '.insert', '.remove', '.sort']):
            return 'data_operation'
        elif 'import' in line or 'from' in line:
            return 'import'
        else:
            return 'logic'
    
    def _explain_line_purpose(self, line: str, category: str) -> str:
        """Generate educational explanation for what this line does."""
        explanations = {
            'conditional': 'This line checks a condition and branches the code execution',
            'else_clause': 'This handles the alternative case when the condition is false',
            'loop': 'This line creates a loop to iterate through data or repeat operations',
            'return_statement': 'This line returns a value from the function',
            'assignment': 'This line assigns a value to a variable',
            'data_operation': 'This line performs an operation on a data structure',
            'definition': 'This line defines a function or class',
            'import': 'This line imports modules or functions',
            'logic': 'This line contains core algorithm logic'
        }
        return explanations.get(category, 'This line performs an important operation')

    def _generate_hint(self, token: str, category: str) -> str:
        """Generate a helpful hint for a token."""
        if category == 'keyword' and len(token) > 2:
            return f"{token[0]}{'_' * (len(token) - 1)}"
        elif category == 'method' and len(token) > 3:
            return f"{token[:2]}{'_' * (len(token) - 2)}"
        elif category == 'operator':
            return f"{'_' * len(token)} (comparison)" if token in ['==', '!=', '<=', '>=', '<', '>'] else f"{'_' * len(token)} (arithmetic)"
        elif category == 'data_structure':
            return f"{token[0]}{'_' * (len(token) - 1)} (type)"
        elif category == 'variable' and len(token) > 1:
            return f"{token[0]}{'_' * min(len(token) - 1, 3)}"
        elif category == 'number':
            return f"{'_' * len(token)} (number)"
        else:
            return f"{'_' * len(token)}"

    def create_masked_code(self, code: str, difficulty: DifficultyMode = DifficultyMode.MEDIUM, 
                          masking_mode: MaskingMode = MaskingMode.MIXED, session_seed: Optional[int] = None) -> MaskedCode:
        """Create masked version of code with structured blanks.
        
        Args:
            code: The source code to mask
            difficulty: Difficulty level determining number of blanks
            masking_mode: Whether to mask tokens, lines, or mixed
            session_seed: Random seed for consistent session-based variations
        """
        # Set random seed for reproducible but varying results per session
        if session_seed is not None:
            random.seed(session_seed)
        
        if masking_mode == MaskingMode.LINE:
            return self._create_line_masked_code(code, difficulty, session_seed)
        elif masking_mode == MaskingMode.TOKEN:
            return self._create_token_masked_code(code, difficulty, session_seed)
        else:  # MIXED
            return self._create_mixed_masked_code(code, difficulty, session_seed)
    
    def _create_line_masked_code(self, code: str, difficulty: DifficultyMode, session_seed: Optional[int]) -> MaskedCode:
        """Create masked code by removing entire lines."""
        lines_info = self.analyze_code_lines(code)
        max_blanks = self.get_blank_count_for_difficulty(difficulty, len(lines_info))
        
        # Select lines based on importance
        high_importance = [l for l in lines_info if l['importance'] >= 8]
        medium_importance = [l for l in lines_info if 5 <= l['importance'] < 8]
        low_importance = [l for l in lines_info if l['importance'] < 5]
        
        selected_lines = []
        remaining_blanks = max_blanks
        
        # Prioritize high importance lines for educational value
        if high_importance and remaining_blanks > 0:
            count = min(len(high_importance), max(1, remaining_blanks // 2))
            selected_lines.extend(random.sample(high_importance, count))
            remaining_blanks -= count
        
        if medium_importance and remaining_blanks > 0:
            count = min(len(medium_importance), remaining_blanks)
            selected_lines.extend(random.sample(medium_importance, count))
            remaining_blanks -= count
        
        # Sort by line number for processing
        selected_lines.sort(key=lambda x: x['line_number'])
        
        # Create masked code by replacing selected lines
        lines = code.split('\n')
        blanks = []
        answers = []
        
        for i, line_info in enumerate(selected_lines):
            blank_id = i + 1
            line_num = line_info['line_number']
            original_line = lines[line_num]
            
            # Create context clues
            context_before = ""
            context_after = ""
            if line_num > 0:
                context_before = lines[line_num - 1].strip()
            if line_num < len(lines) - 1:
                context_after = lines[line_num + 1].strip()
            
            # Generate better hints for lines
            hint = self._generate_line_hint(line_info['stripped'], line_info['category'])
            
            blank_info = BlankInfo(
                position=0,  # Will be calculated later
                length=len(original_line),
                token=original_line.strip(),
                hint=hint,
                category=line_info['category'],
                blank_id=blank_id,
                is_line=True,
                line_number=line_num,
                context_before=context_before,
                context_after=context_after,
                explanation=line_info['explanation']
            )
            
            blanks.append(blank_info)
            answers.append(original_line.strip())
            
            # Replace the line with a placeholder
            indent = len(original_line) - len(original_line.lstrip())
            placeholder = ' ' * indent + f"# ___[{blank_id}] - {line_info['category']} line missing here"
            lines[line_num] = placeholder
        
        masked_code = '\n'.join(lines)
        
        return MaskedCode(
            masked_code=masked_code,
            blanks=blanks,
            answers=answers,
            difficulty=difficulty,
            masking_mode=MaskingMode.LINE
        )
    
    def _create_token_masked_code(self, code: str, difficulty: DifficultyMode, session_seed: Optional[int]) -> MaskedCode:
        """Create masked code by removing individual tokens (original behavior)."""
        tokens = self.analyze_code_tokens(code)
        max_blanks = self.get_blank_count_for_difficulty(difficulty, len(tokens))
        
        # Group tokens by importance and randomly select within groups
        high_importance = [t for t in tokens if t['importance'] >= 8]
        medium_importance = [t for t in tokens if 5 <= t['importance'] < 8]
        low_importance = [t for t in tokens if t['importance'] < 5]
        
        selected_tokens = []
        remaining_blanks = max_blanks
        
        # Always include some high importance tokens
        if high_importance and remaining_blanks > 0:
            count = min(len(high_importance), max(1, remaining_blanks // 2))
            selected_tokens.extend(random.sample(high_importance, count))
            remaining_blanks -= count
        
        # Fill remaining with medium and low importance
        if medium_importance and remaining_blanks > 0:
            count = min(len(medium_importance), remaining_blanks)
            selected_tokens.extend(random.sample(medium_importance, count))
            remaining_blanks -= count
        
        # Fill any remaining with low importance
        if low_importance and remaining_blanks > 0:
            count = min(len(low_importance), remaining_blanks)
            selected_tokens.extend(random.sample(low_importance, count))
        
        # Sort selected tokens by position for consistent blank numbering
        selected_tokens.sort(key=lambda x: x['start'])
        
        # Create blanks and masked code
        blanks = []
        answers = []
        offset = 0
        masked_code = code
        
        for i, token in enumerate(selected_tokens):
            blank_id = i + 1
            blank_placeholder = f"___[{blank_id}]"
            
            # Adjust position for previous replacements
            start_pos = token['start'] + offset
            end_pos = token['end'] + offset
            
            # Create blank info
            blank_info = BlankInfo(
                position=start_pos,
                length=len(blank_placeholder),
                token=token['token'],
                hint=token['hint'],
                category=token['category'],
                blank_id=blank_id
            )
            
            blanks.append(blank_info)
            answers.append(token['token'])
            
            # Replace in code
            masked_code = (
                masked_code[:start_pos] + 
                blank_placeholder + 
                masked_code[end_pos:]
            )
            
            # Update offset for next replacements
            offset += len(blank_placeholder) - (token['end'] - token['start'])
        
        return MaskedCode(
            masked_code=masked_code,
            blanks=blanks,
            answers=answers,
            difficulty=difficulty,
            masking_mode=MaskingMode.TOKEN
        )
    
    def _create_mixed_masked_code(self, code: str, difficulty: DifficultyMode, session_seed: Optional[int]) -> MaskedCode:
        """Create masked code with a mix of line and token blanks."""
        # For mixed mode, create fewer line blanks and more token blanks
        if difficulty == DifficultyMode.EASY:
            line_count, token_count = 1, 1
        elif difficulty == DifficultyMode.MEDIUM:
            line_count, token_count = 1, 2  
        else:  # HARD
            line_count, token_count = 2, 3
        
        # Get line and token analyses
        lines_info = self.analyze_code_lines(code)
        tokens_info = self.analyze_code_tokens(code)
        
        # Select best lines for masking
        high_importance_lines = [l for l in lines_info if l['importance'] >= 8]
        medium_importance_lines = [l for l in lines_info if 5 <= l['importance'] < 8]
        
        selected_lines = []
        if high_importance_lines and line_count > 0:
            count = min(len(high_importance_lines), line_count)
            selected_lines.extend(random.sample(high_importance_lines, count))
            line_count -= count
        
        if medium_importance_lines and line_count > 0:
            count = min(len(medium_importance_lines), line_count)
            selected_lines.extend(random.sample(medium_importance_lines, count))
        
        # Select best tokens for masking (avoid lines that will be masked)
        masked_line_numbers = {l['line_number'] for l in selected_lines}
        available_tokens = [t for t in tokens_info 
                           if not any(line_num <= t['start'] <= line_num for line_num in masked_line_numbers)]
        
        high_importance_tokens = [t for t in available_tokens if t['importance'] >= 8]
        medium_importance_tokens = [t for t in available_tokens if 5 <= t['importance'] < 8]
        
        selected_tokens = []
        if high_importance_tokens and token_count > 0:
            count = min(len(high_importance_tokens), max(1, token_count // 2))
            selected_tokens.extend(random.sample(high_importance_tokens, count))
            token_count -= count
        
        if medium_importance_tokens and token_count > 0:
            count = min(len(medium_importance_tokens), token_count)
            selected_tokens.extend(random.sample(medium_importance_tokens, count))
        
        # Apply line masking first
        lines = code.split('\n')
        blanks = []
        answers = []
        blank_id = 1
        
        # Process line blanks
        selected_lines.sort(key=lambda x: x['line_number'])
        for line_info in selected_lines:
            line_num = line_info['line_number']
            original_line = lines[line_num]
            
            context_before = lines[line_num - 1].strip() if line_num > 0 else ""
            context_after = lines[line_num + 1].strip() if line_num < len(lines) - 1 else ""
            
            hint = self._generate_line_hint(line_info['stripped'], line_info['category'])
            
            blank_info = BlankInfo(
                position=0,
                length=len(original_line),
                token=original_line.strip(),
                hint=hint,
                category=line_info['category'],
                blank_id=blank_id,
                is_line=True,
                line_number=line_num,
                context_before=context_before,
                context_after=context_after,
                explanation=line_info['explanation']
            )
            
            blanks.append(blank_info)
            answers.append(original_line.strip())
            
            # Replace the line with a placeholder
            indent = len(original_line) - len(original_line.lstrip())
            placeholder = ' ' * indent + f"# ___[{blank_id}] - {line_info['category']} line missing here"
            lines[line_num] = placeholder
            blank_id += 1
        
        # Apply token masking to the remaining code
        working_code = '\n'.join(lines)
        selected_tokens.sort(key=lambda x: x['start'])
        
        offset = 0
        for token in selected_tokens:
            blank_placeholder = f"___[{blank_id}]"
            
            start_pos = token['start'] + offset
            end_pos = token['end'] + offset
            
            # Ensure we're not replacing inside a line comment
            if "# ___[" in working_code[max(0, start_pos-20):start_pos+20]:
                continue
            
            blank_info = BlankInfo(
                position=start_pos,
                length=len(blank_placeholder),
                token=token['token'],
                hint=token['hint'],
                category=token['category'],
                blank_id=blank_id
            )
            
            blanks.append(blank_info)
            answers.append(token['token'])
            
            working_code = (
                working_code[:start_pos] + 
                blank_placeholder + 
                working_code[end_pos:]
            )
            
            offset += len(blank_placeholder) - (token['end'] - token['start'])
            blank_id += 1
        
        return MaskedCode(
            masked_code=working_code,
            blanks=blanks,
            answers=answers,
            difficulty=difficulty,
            masking_mode=MaskingMode.MIXED
        )
    
    def _generate_line_hint(self, line: str, category: str) -> str:
        """Generate educational hints for entire lines."""
        hints = {
            'conditional': 'Control flow: Check a condition with if/elif',
            'else_clause': 'Alternative branch: Handle the else case',
            'loop': 'Iteration: Use for/while to repeat operations',
            'return_statement': 'Function output: Return the result',
            'assignment': 'Variable assignment: Store a value',
            'data_operation': 'Data manipulation: Modify the data structure',
            'definition': 'Function/Class definition',
            'import': 'Import statement',
            'logic': 'Core algorithm logic'
        }
        return hints.get(category, 'Important code line')

    def create_multiple_masks(self, code: str, count: int = 3) -> List[MaskedCode]:
        """Create multiple different masked versions for variety."""
        masks = []
        
        # Create one for each difficulty level
        for difficulty in DifficultyMode:
            mask = self.create_masked_code(code, difficulty)
            if mask.blanks:  # Only add if there are blanks
                masks.append(mask)
        
        # Add some random variations
        tokens = self.analyze_code_tokens(code)
        if len(tokens) > 3:
            for _ in range(min(count - len(masks), 3)):
                # Randomly select tokens
                selected_count = random.randint(2, min(6, len(tokens)))
                random_tokens = random.sample(tokens, selected_count)
                
                # Create mask manually
                random_tokens.sort(key=lambda x: x['start'])
                
                blanks = []
                answers = []
                offset = 0
                masked_code = code
                
                for i, token in enumerate(random_tokens):
                    blank_id = i + 1
                    blank_placeholder = f"___[{blank_id}]"
                    
                    start_pos = token['start'] + offset
                    end_pos = token['end'] + offset
                    
                    blank_info = BlankInfo(
                        position=start_pos,
                        length=len(blank_placeholder),
                        token=token['token'],
                        hint=token['hint'],
                        category=token['category'],
                        blank_id=blank_id
                    )
                    
                    blanks.append(blank_info)
                    answers.append(token['token'])
                    
                    masked_code = (
                        masked_code[:start_pos] + 
                        blank_placeholder + 
                        masked_code[end_pos:]
                    )
                    
                    offset += len(blank_placeholder) - (token['end'] - token['start'])
                
                mask = MaskedCode(
                    masked_code=masked_code,
                    blanks=blanks,
                    answers=answers,
                    difficulty=DifficultyMode.MEDIUM
                )
                masks.append(mask)
        
        return masks[:count]

def test_masking():
    """Test the masking system with sample code."""
    masker = CodeMasker()
    
    sample_code = """class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        prevMap = {}
        
        for i, n in enumerate(nums):
            diff = target - n
            if diff in prevMap:
                return [prevMap[diff], i]
            prevMap[n] = i"""
    
    print("Original Code:")
    print(sample_code)
    print("\n" + "="*50 + "\n")
    
    for difficulty in DifficultyMode:
        masked = masker.create_masked_code(sample_code, difficulty)
        print(f"{difficulty.value.upper()} Mode ({len(masked.blanks)} blanks):")
        print(masked.masked_code)
        print("\nAnswers:")
        for i, (blank, answer) in enumerate(zip(masked.blanks, masked.answers)):
            print(f"  [{blank.blank_id}] {answer} (hint: {blank.hint})")
        print("\n" + "-"*30 + "\n")

if __name__ == "__main__":
    test_masking()
