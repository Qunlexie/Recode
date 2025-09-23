#!/usr/bin/env python3
"""
Simple coding interview flashcard app.
Easy to add new questions in questions.py!
"""

import streamlit as st
import random
import json
from neetcode_150 import NEETCODE_150


def load_questions():
    """Load questions from file."""
    try:
        with open('questions.json', 'r') as f:
            questions = json.load(f)
    except FileNotFoundError:
        # Start with NeetCode problems if no file exists
        questions = []
        for q in NEETCODE_150:
            questions.append({
                "title": q["title"],
                "question": q["question"],
                "answer": q["answer"],
                "tags": ["Easy"],  # Default tag for NeetCode problems
                "type": "Flashcard"  # Default type
            })
        save_questions(questions)
        return questions
    
    # If file exists but is empty, load NeetCode problems
    if not questions:
        for q in NEETCODE_150:
            questions.append({
                "title": q["title"],
                "question": q["question"],
                "answer": q["answer"],
                "tags": ["Easy"],  # Default tag for NeetCode problems
                "type": "Flashcard"  # Default type
            })
        save_questions(questions)
    
    # Ensure all questions have a type field (for backward compatibility)
    for question in questions:
        if 'type' not in question:
            question['type'] = 'Flashcard'
    
    return questions


def save_questions(questions):
    """Save questions to file."""
    with open('questions.json', 'w') as f:
        json.dump(questions, f, indent=2)


def render_question(question_data, practice_mode):
    """Render question based on the selected practice mode."""
    if practice_mode == 'Flashcard':
        render_flashcard(question_data)
    elif practice_mode == 'Fill in the Blanks':
        render_fill_blanks_auto(question_data)
    elif practice_mode == 'Multiple Choice':
        render_multiple_choice_auto(question_data)
    else:
        render_flashcard(question_data)  # Default fallback


def generate_fill_blanks_template(answer_text):
    """Generate fill-in-the-blanks template from flashcard answer."""
    if not answer_text:
        return "No code template available."
    
    # Find code blocks
    parts = answer_text.split('```')
    result_parts = []
    
    for i, part in enumerate(parts):
        if i % 2 == 0:
            # Regular text - keep as is
            result_parts.append(part)
        else:
            # Code block - create blanks
            lines = part.split('\n', 1)
            if len(lines) > 1:
                language = lines[0].strip()
                code = lines[1]
                
                # Create blanks for key parts
                code_with_blanks = create_code_blanks(code)
                result_parts.append(f"```{language}\n{code_with_blanks}\n```")
            else:
                result_parts.append(f"```\n{part}\n```")
    
    return ''.join(result_parts)


def create_code_blanks(code):
    """Create blanks in code by replacing key terms with ___."""
    # Common patterns to replace with blanks
    replacements = [
        # Function definitions and variables
        (r'\bdef\s+(\w+)\s*\(', r'def \1('),
        (r'\bif\s+', 'if '),
        (r'\bfor\s+', 'for '),
        (r'\bwhile\s+', 'while '),
        (r'\breturn\s+', 'return '),
        
        # Common data structures and methods
        (r'\b{}\b', '___'),  # Empty dict
        (r'\b\[\]\b', '___'),  # Empty list
        (r'\bset\(\)\b', '___'),  # Empty set
        (r'\bCounter\b', '___'),
        (r'\bdefaultdict\b', '___'),
        (r'\.append\b', '.___'),
        (r'\.add\b', '.___'),
        (r'\.get\b', '.___'),
        (r'\.items\(\)\b', '.___()'),
        (r'\.keys\(\)\b', '.___()'),
        (r'\.values\(\)\b', '.___()'),
        
        # Common functions
        (r'\blen\b', '___'),
        (r'\bmax\b', '___'),
        (r'\bmin\b', '___'),
        (r'\bsorted\b', '___'),
        (r'\breversed\b', '___'),
        (r'\benumerate\b', '___'),
        (r'\brange\b', '___'),
        
        # Variables (simple heuristic)
        (r'\bseen\b', '___'),
        (r'\bresult\b', '___'),
        (r'\bcount\b', '___'),
        (r'\bfreq\b', '___'),
    ]
    
    import re
    result = code
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result)
    
    return result


def generate_multiple_choice_questions(answer_text):
    """Generate multiple choice questions from flashcard answer."""
    import re
    
    # Try to extract time complexity
    time_complexity = None
    time_match = re.search(r'Time[:\s]*O\(([^)]+)\)', answer_text, re.IGNORECASE)
    if time_match:
        time_complexity = time_match.group(1)
    
    # Try to extract space complexity
    space_complexity = None
    space_match = re.search(r'Space[:\s]*O\(([^)]+)\)', answer_text, re.IGNORECASE)
    if space_match:
        space_complexity = space_match.group(1)
    
    # Determine algorithm approach based on keywords
    approach = 'Hash Map / Dictionary'  # default
    if 'two pointer' in answer_text.lower() or 'left' in answer_text.lower() and 'right' in answer_text.lower():
        approach = 'Two Pointers'
    elif 'dynamic programming' in answer_text.lower() or 'dp' in answer_text.lower():
        approach = 'Dynamic Programming'
    elif 'binary search' in answer_text.lower():
        approach = 'Binary Search'
    elif 'stack' in answer_text.lower():
        approach = 'Stack'
    elif 'queue' in answer_text.lower():
        approach = 'Queue'
    elif 'tree' in answer_text.lower() or 'node' in answer_text.lower():
        approach = 'Tree'
    elif 'graph' in answer_text.lower() or 'bfs' in answer_text.lower() or 'dfs' in answer_text.lower():
        approach = 'Graph'
    
    # Generate questions based on what we found
    if time_complexity:
        time_options = ['O(1)', 'O(n)', 'O(n log n)', 'O(n²)', 'O(2^n)']
        try:
            correct_idx = time_options.index(f'O({time_complexity})')
        except ValueError:
            correct_idx = 1  # default to O(n)
        
        return {
            'question': 'What is the time complexity of this algorithm?',
            'options': time_options,
            'correct': correct_idx,
            'explanation': f'The algorithm has O({time_complexity}) time complexity as stated in the solution.'
        }
    
    elif space_complexity:
        space_options = ['O(1)', 'O(n)', 'O(log n)', 'O(n²)', 'O(2^n)']
        try:
            correct_idx = space_options.index(f'O({space_complexity})')
        except ValueError:
            correct_idx = 1  # default to O(n)
        
        return {
            'question': 'What is the space complexity of this algorithm?',
            'options': space_options,
            'correct': correct_idx,
            'explanation': f'The algorithm has O({space_complexity}) space complexity as stated in the solution.'
        }
    
    else:
        # Algorithm approach question
        approach_options = ['Brute Force', 'Hash Map / Dictionary', 'Two Pointers', 'Dynamic Programming', 'Binary Search']
        approach_map = {
            'Hash Map / Dictionary': 1,
            'Two Pointers': 2,
            'Dynamic Programming': 3,
            'Binary Search': 4,
            'Stack': 0,  # fallback to Brute Force
            'Queue': 0,
            'Tree': 0,
            'Graph': 0
        }
        correct_idx = approach_map.get(approach, 1)
        
        return {
            'question': 'What is the main approach used in this solution?',
            'options': approach_options,
            'correct': correct_idx,
            'explanation': f'The solution primarily uses {approach} approach based on the implementation.'
        }


def render_flashcard(question_data):
    """Render flashcard question."""
    question_text = question_data['question']
    if question_text:
        st.markdown(question_text)
    
    st.markdown("---")
    
    # Answer section
    if not st.session_state.show_answer:
        if st.button("👁️ Show Answer", use_container_width=True, type="primary"):
            st.session_state.show_answer = True
            st.rerun()
    else:
        st.subheader("✅ Answer")
        
        # Display answer with automatic syntax highlighting
        answer_text = question_data['answer']
        if answer_text:
            # Split the answer into parts and highlight code blocks
            parts = answer_text.split('```')
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    # Regular text
                    if part.strip():
                        st.markdown(part)
                else:
                    # Code block - extract language if specified
                    lines = part.split('\n', 1)
                    if len(lines) > 1:
                        language = lines[0].strip()
                        code = lines[1]
                        if language:
                            st.code(code, language=language)
                        else:
                            st.code(code)
                    else:
                        st.code(part)


def render_fill_blanks(question_data):
    """Render fill-in-the-blanks question."""
    question_text = question_data['question']
    if question_text:
        st.markdown(question_text)
    
    st.markdown("---")
    
    # Show the template with blanks
    st.subheader("📝 Fill in the Blanks")
    
    template = question_data['answer']
    if template:
        # Display the template with blanks
        parts = template.split('```')
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Regular text
                if part.strip():
                    st.markdown(part)
            else:
                # Code block with blanks
                lines = part.split('\n', 1)
                if len(lines) > 1:
                    language = lines[0].strip()
                    code = lines[1]
                    st.code(code, language=language)
                else:
                    st.code(part)
    
    # Show answer button
    if not st.session_state.show_answer:
        if st.button("👁️ Show Filled Solution", use_container_width=True, type="primary"):
            st.session_state.show_answer = True
            st.rerun()
    else:
        st.subheader("✅ Filled Solution")
        
        # Parse and display the filled solution
        filled_template = template
        # Replace ___ with the actual answers (this would need to be parsed from comments)
        # For now, just show the template again
        st.markdown("*The filled solution would be displayed here*")
        
        # Display the template with answers filled in
        parts = template.split('```')
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Regular text
                if part.strip():
                    st.markdown(part)
            else:
                # Code block - show with answers
                lines = part.split('\n', 1)
                if len(lines) > 1:
                    language = lines[0].strip()
                    code = lines[1]
                    # Replace ___ with answers (simplified for demo)
                    filled_code = code.replace('___', '**[ANSWER]**')
                    st.code(filled_code, language=language)
                else:
                    st.code(part)


def render_fill_blanks_auto(question_data):
    """Render auto-generated fill-in-the-blanks from flashcard."""
    question_text = question_data['question']
    if question_text:
        st.markdown(question_text)
    
    st.markdown("---")
    
    # Show the auto-generated template with blanks
    st.subheader("📝 Fill in the Blanks")
    st.info("💡 This template was automatically generated from the solution. Fill in the blanks!")
    
    # Generate template from the answer
    template = generate_fill_blanks_template(question_data['answer'])
    
    if template:
        # Display the template with blanks
        parts = template.split('```')
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Regular text
                if part.strip():
                    st.markdown(part)
            else:
                # Code block with blanks
                lines = part.split('\n', 1)
                if len(lines) > 1:
                    language = lines[0].strip()
                    code = lines[1]
                    st.code(code, language=language)
                else:
                    st.code(part)
    
    # Show answer button
    if not st.session_state.show_answer:
        if st.button("👁️ Show Complete Solution", use_container_width=True, type="primary"):
            st.session_state.show_answer = True
            st.rerun()
    else:
        st.subheader("✅ Complete Solution")
        
        # Display the original answer
        answer_text = question_data['answer']
        if answer_text:
            parts = answer_text.split('```')
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    if part.strip():
                        st.markdown(part)
                else:
                    lines = part.split('\n', 1)
                    if len(lines) > 1:
                        language = lines[0].strip()
                        code = lines[1]
                        if language:
                            st.code(code, language=language)
                        else:
                            st.code(code)
                    else:
                        st.code(part)


def render_multiple_choice_auto(question_data):
    """Render auto-generated multiple choice from flashcard."""
    question_text = question_data['question']
    if question_text:
        st.markdown(question_text)
    
    st.markdown("---")
    
    # Generate multiple choice question from answer
    mc_question = generate_multiple_choice_questions(question_data['answer'])
    
    st.subheader("📋 Multiple Choice Quiz")
    st.info("💡 This quiz was automatically generated from the solution analysis!")
    
    # Display the generated question
    st.write(f"**{mc_question['question']}**")
    
    if 'user_answer' not in st.session_state:
        st.session_state.user_answer = None
    
    # Create radio buttons for options
    option_labels = [f"{chr(65+i)}) {opt}" for i, opt in enumerate(mc_question['options'])]
    selected = st.radio("Select an answer:", 
                       option_labels,
                       key=f"mc_auto_{question_data['title']}")
    
    if selected:
        st.session_state.user_answer = ord(selected[0]) - 65  # Convert A,B,C,D to 0,1,2,3
    
    # Show submit button
    if st.button("✅ Submit Answer", use_container_width=True):
        if st.session_state.user_answer is not None:
            if st.session_state.user_answer == mc_question['correct']:
                st.success("🎉 Correct!")
            else:
                correct_letter = chr(65 + mc_question['correct'])
                st.error(f"❌ Incorrect. The correct answer is {correct_letter})")
            
            # Show explanation
            st.markdown("---")
            st.subheader("📖 Explanation")
            st.markdown(f"**Correct Answer:** {chr(65 + mc_question['correct'])})")
            for i, opt in enumerate(mc_question['options']):
                if i == mc_question['correct']:
                    st.markdown(f"**{chr(65+i)})** {opt} ✅")
                else:
                    st.markdown(f"**{chr(65+i)})** {opt}")
            
            st.markdown(f"**Explanation:** {mc_question['explanation']}")


def render_multiple_choice(question_data):
    """Render multiple choice question (legacy function for backward compatibility)."""
    question_text = question_data['question']
    if question_text:
        st.markdown(question_text)
    
    st.markdown("---")
    
    # Parse multiple choice options
    options_text = question_data['answer']
    if options_text:
        # Split by lines and parse options
        lines = [line.strip() for line in options_text.split('\n') if line.strip()]
        options = []
        correct_answer = None
        
        for line in lines:
            if line.startswith(('A)', 'B)', 'C)', 'D)', 'E)')):
                option_text = line[2:].strip()
                if '(CORRECT)' in option_text:
                    option_text = option_text.replace('(CORRECT)', '').strip()
                    correct_answer = line[0]
                options.append((line[0], option_text))
        
        # Display options
        st.subheader("📋 Choose Your Answer")
        
        if 'user_answer' not in st.session_state:
            st.session_state.user_answer = None
        
        # Create radio buttons for options
        selected = st.radio("Select an answer:", 
                           [f"{opt[0]}) {opt[1]}" for opt in options],
                           key=f"mc_{question_data['title']}")
        
        if selected:
            st.session_state.user_answer = selected[0]
        
        # Show submit button
        if st.button("✅ Submit Answer", use_container_width=True):
            if st.session_state.user_answer:
                if st.session_state.user_answer == correct_answer:
                    st.success("🎉 Correct!")
                else:
                    st.error(f"❌ Incorrect. The correct answer is {correct_answer})")
                
                # Show explanation
                st.markdown("---")
                st.subheader("📖 Explanation")
                st.markdown(f"**Correct Answer:** {correct_answer})")
                for opt in options:
                    if opt[0] == correct_answer:
                        st.markdown(f"**{opt[0]})** {opt[1]} ✅")
                    else:
                        st.markdown(f"**{opt[0]})** {opt[1]}")


def main():
    """Simple flashcard app."""
    st.set_page_config(
        page_title="Coding Interview Flashcards",
        page_icon="🃏",
        layout="centered"
    )
    
    # Load questions
    questions = load_questions()
    
    # Tag filtering (moved outside sidebar for global access)
    all_tags = set()
    for q in questions:
        if 'tags' in q:
            all_tags.update(q['tags'])
    
    st.title("🎯 Coding Interview Practice")
    st.markdown("*Switch between different question formats for the same problems*")
    
    # Mode switcher
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        practice_mode = st.selectbox("Practice Mode", 
                                   ["Flashcard", "Fill in the Blanks", "Multiple Choice"],
                                   help="Choose how you want to practice the same questions")
    
    # Sidebar for adding questions and filtering
    with st.sidebar:
        st.header("➕ Add New Question")
        
        with st.form("add_question"):
            title = st.text_input("Question Title", placeholder="e.g., Two Sum")
            question = st.text_area("Question", placeholder="Enter your question here...\n\nExample:\nGiven an array nums and integer k, return k most frequent elements.\n\nInput: nums = [1,1,1,2,2,3], k = 2\nOutput: [1,2]", height=150)
            answer = st.text_area("Answer", placeholder="Enter your complete answer with solution...\n\nExample:\n```python\ndef topKFrequent(nums, k):\n    count = Counter(nums)\n    bucket = [[] for _ in range(max(count.values()) + 1)]\n    for num, freq in count.items():\n        bucket[freq].append(num)\n    # ... rest of solution\n```\n\nTime: O(n), Space: O(n)", height=200)
            
            # Tags section
            st.write("**Tags (optional):**")
            
            # Use the already calculated all_tags
            
            col1, col2 = st.columns(2)
            with col1:
                difficulty = st.selectbox("Difficulty", ["", "Easy", "Medium", "Hard"])
            with col2:
                category_options = ["", "Array", "Hash Map", "Two Pointers", "Binary Search", "Tree", "Graph", "Dynamic Programming", "Greedy", "Sorting"]
                # Add existing custom categories
                for tag in sorted(all_tags):
                    if tag not in category_options and tag not in ["Easy", "Medium", "Hard"]:
                        category_options.append(tag)
                category = st.selectbox("Category", category_options)
            
            # Custom tags with ability to add new ones
            st.write("**Additional Tags:**")
            existing_tags = sorted([tag for tag in all_tags if tag not in ["Easy", "Medium", "Hard"]])
            if existing_tags:
                additional_tags = st.multiselect("Select existing tags:", existing_tags)
            else:
                additional_tags = []
            
            new_tag = st.text_input("Add new tag:", placeholder="Type a new tag name")
            if new_tag and new_tag.strip():
                additional_tags.append(new_tag.strip())
            
            if st.form_submit_button("Add Question", use_container_width=True):
                if title and question and answer:
                    # Build tags list
                    tags = []
                    if difficulty:
                        tags.append(difficulty)
                    if category:
                        tags.append(category)
                    if additional_tags:
                        tags.extend(additional_tags)
                    
                    new_question = {
                        "title": title,
                        "question": question,
                        "answer": answer,
                        "tags": tags
                    }
                    questions.append(new_question)
                    save_questions(questions)
                    st.success("Question added!")
                    st.rerun()
                else:
                    st.error("Please fill in all fields")
        
        st.markdown("---")
        st.write(f"**Total Questions:** {len(questions)}")
        
        # Tag filtering
        st.subheader("🏷️ Filter by Tags")
        
        if all_tags:
            selected_tags = st.multiselect("Select tags to filter:", sorted(all_tags))
        else:
            selected_tags = []
    
    # Apply filtering based on selected tags
    if selected_tags:
        filtered_questions = [q for q in questions if 'tags' in q and any(tag in q['tags'] for tag in selected_tags)]
        st.info(f"🔍 Showing {len(filtered_questions)} questions with tags: {', '.join(selected_tags)}")
    else:
        filtered_questions = questions
    
    # Main flashcard area
    if not filtered_questions:
        if selected_tags:
            st.warning(f"No questions found with the selected tags: {', '.join(selected_tags)}")
        else:
            st.warning("No questions available. Add some questions in the sidebar!")
        return
    
    # Initialize session state
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = random.choice(filtered_questions)
    
    question_data = st.session_state.current_question
    
    # Question
    st.markdown("---")
    st.subheader(f"❓ {question_data['title']}")
    
    # Display tags if they exist
    if 'tags' in question_data and question_data['tags']:
        tag_colors = {
            'Easy': '🟢', 'Medium': '🟡', 'Hard': '🔴',
            'Array': '🔵', 'Hash Map': '🟣', 'Two Pointers': '🟠',
            'Binary Search': '🔵', 'Tree': '🟢', 'Graph': '🟣',
            'Dynamic Programming': '🟠', 'Greedy': '🟡', 'Sorting': '🔵'
        }
        
        tag_display = []
        for tag in question_data['tags']:
            color = tag_colors.get(tag, '⚪')
            tag_display.append(f"{color} {tag}")
        
        st.write("**Tags:** " + " ".join(tag_display))
    
    # Render question based on the selected practice mode
    render_question(question_data, practice_mode)
    
    # Action buttons (show for all modes)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 New Question", use_container_width=True):
            st.session_state.show_answer = False
            st.session_state.current_question = random.choice(filtered_questions)
            st.rerun()
    
    with col2:
        if st.button("✏️ Edit This Question", use_container_width=True):
            st.session_state.edit_mode = True
            st.session_state.editing_question = question_data
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
                                        index=["", "Easy", "Medium", "Hard"].index(current_difficulty) if current_difficulty else 0)
            with col2:
                category_options = ["", "Array", "Hash Map", "Two Pointers", "Binary Search", "Tree", "Graph", "Dynamic Programming", "Greedy", "Sorting"]
                # Add existing custom categories
                for tag in sorted(all_tags):
                    if tag not in category_options and tag not in ["Easy", "Medium", "Hard"]:
                        category_options.append(tag)
                current_category = next((tag for tag in current_tags if tag in category_options), "")
                category = st.selectbox("Category", category_options,
                                      index=category_options.index(current_category) if current_category else 0)
            
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
                    
                    # Find and update the question in the list
                    for i, q in enumerate(questions):
                        if (q['title'] == editing_question['title'] and 
                            q['question'] == editing_question['question'] and 
                            q['answer'] == editing_question['answer']):
                            questions[i] = {
                                'title': new_title,
                                'question': new_question,
                                'answer': new_answer,
                                'tags': new_tags
                            }
                            break
                    
                    save_questions(questions)
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


if __name__ == '__main__':
    main()
