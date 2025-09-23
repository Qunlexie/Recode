"""
Streamlit web interface for the coding interview revision system.
"""

import streamlit as st
import random
from core import ProblemBank, QuizEngine


class WebInterface:
    """Streamlit web interface for the quiz system."""
    
    def __init__(self, problem_bank_file: str):
        self.problem_bank = ProblemBank(problem_bank_file)
        self.quiz_engine = QuizEngine(self.problem_bank)
    
    def run(self):
        """Main Streamlit app."""
        st.set_page_config(
            page_title="Coding Interview Revision System",
            page_icon="🎯",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Mobile-friendly CSS
        st.markdown("""
        <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 100%;
        }
        .stButton > button {
            width: 100%;
            border-radius: 20px;
            height: 3rem;
            font-size: 1.1rem;
            margin-bottom: 1rem;
        }
        .stTextArea textarea {
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        .stCodeBlock {
            font-size: 14px;
        }
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .stSidebar {
                width: 100%;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.title("🎯 Coding Interview Revision System")
        st.markdown("*Quick practice for core coding concepts!*")
        
        # Initialize session state
        if 'quiz_mode' not in st.session_state:
            st.session_state.quiz_mode = None
        if 'current_problem' not in st.session_state:
            st.session_state.current_problem = None
        if 'quiz_data' not in st.session_state:
            st.session_state.quiz_data = None
        
        # Sidebar for navigation
        with st.sidebar:
            st.header("📚 Navigation")
            
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.quiz_mode = None
                st.rerun()
            
            st.subheader("🎯 Practice Modes")
            if st.button("🃏 Flashcard Mode", use_container_width=True):
                self.show_flashcard_selection()
            
            if st.button("🧪 Unit Test Mode", use_container_width=True):
                self.show_unit_test_selection()
            
            if st.button("📚 Explain Mode", use_container_width=True):
                self.show_explain_selection()
            
            if st.button("🎲 Random Practice", use_container_width=True):
                self.start_random_practice()
            
            st.subheader("📊 Progress")
            self.show_score_summary()
        
        # Main content area
        if st.session_state.quiz_mode == 'flashcard':
            self.show_flashcard_mode()
        elif st.session_state.quiz_mode == 'unit_test':
            self.show_unit_test_mode()
        elif st.session_state.quiz_mode == 'explain':
            self.show_explain_mode()
        else:
            self.show_home()
    
    def show_home(self):
        """Show the home page."""
        st.header("Welcome to Your Coding Interview Practice!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📚 Available Concepts")
            concepts = self.problem_bank.get_all_concepts()
            for concept in concepts:
                st.write(f"• {concept}")
        
        with col2:
            st.subheader("🏷️ Available Patterns")
            patterns = self.problem_bank.get_all_patterns()
            for pattern in patterns:
                st.write(f"• {pattern}")
        
        st.subheader("🚀 Quick Start")
        st.markdown("""
        1. **Flashcard Mode**: Test your knowledge of key code snippets
        2. **Unit Test Mode**: Practice handling edge cases
        3. **Explain Mode**: Review concepts and common pitfalls
        4. **Random Practice**: Get a surprise challenge!
        """)
        
        # Show problem statistics
        st.subheader("📊 Problem Bank Statistics")
        total_problems = len(self.problem_bank.problems)
        
        # Count by difficulty
        difficulties = {}
        for problem in self.problem_bank.problems.values():
            diff = problem.tags.get('difficulty', 'unknown')
            difficulties[diff] = difficulties.get(diff, 0) + 1
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Problems", total_problems)
        with col2:
            st.metric("Easy Problems", difficulties.get('easy', 0))
        with col3:
            st.metric("Hard Problems", difficulties.get('hard', 0))
    
    def show_flashcard_selection(self):
        """Show flashcard problem selection."""
        st.session_state.quiz_mode = 'flashcard_selection'
        st.rerun()
    
    def show_unit_test_selection(self):
        """Show unit test problem selection."""
        st.session_state.quiz_mode = 'unit_test_selection'
        st.rerun()
    
    def show_explain_selection(self):
        """Show explain problem selection."""
        st.session_state.quiz_mode = 'explain_selection'
        st.rerun()
    
    def show_flashcard_mode(self):
        """Show flashcard mode interface."""
        if not st.session_state.quiz_data:
            self.select_problem_for_mode('flashcard')
            return
        
        st.header("🃏 Flashcard Mode")
        
        data = st.session_state.quiz_data
        st.subheader(data['problem_title'])
        st.write(f"**Concept:** {data['concept']}")
        
        st.markdown("---")
        
        st.subheader("❓ Question")
        st.write(data['question'])
        
        if data['context']:
            st.info(f"💭 Context: {data['context']}")
        
        # Answer input
        user_answer = st.text_input("Your Answer:", placeholder="Type your answer here...")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Check Answer"):
                if user_answer:
                    result = self.quiz_engine.check_flashcard_answer(user_answer)
                    
                    if result['correct']:
                        st.success("✅ Correct!")
                    else:
                        st.error("❌ Incorrect!")
                        st.write(f"Your answer: {result['user_answer']}")
                        st.write(f"Correct answer: {result['correct_answer']}")
                    
                    st.write(f"Score: {result['score']}/{result['total']}")
                    
                    # Reset for next question
                    st.session_state.quiz_data = None
                    if st.button("🔄 Next Question"):
                        st.rerun()
        
        with col2:
            if st.button("👁️ Show Answer"):
                st.write(f"✅ Correct Answer: {data['correct_answer']}")
                st.session_state.quiz_data = None
    
    def show_unit_test_mode(self):
        """Show unit test mode interface."""
        if not st.session_state.quiz_data:
            self.select_problem_for_mode('unit_test')
            return
        
        st.header("🧪 Unit Test Mode")
        
        data = st.session_state.quiz_data
        st.subheader(data['problem_title'])
        st.write(f"**Concept:** {data['concept']}")
        
        st.markdown("---")
        
        st.subheader("📝 Test Case")
        st.code(data['test_input'])
        st.write(f"**Description:** {data['test_description']}")
        st.write(f"**Expected Output:** {data['expected_output']}")
        
        # Code editor
        st.subheader("✏️ Modify the Code")
        st.write("Update the code snippet to handle this edge case:")
        
        # Get the original snippet
        problem_id = data['problem_title'].lower().replace(' ', '_')
        if problem_id in self.problem_bank.problems:
            original_snippet = self.problem_bank.problems[problem_id].snippet
        else:
            original_snippet = "def solution():\n    pass"
        
        modified_code = st.text_area(
            "Code:",
            value=original_snippet,
            height=300,
            help="Modify this code to handle the test case above"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧪 Run Test"):
                if modified_code:
                    result = self.quiz_engine.run_test_case(modified_code)
                    
                    if 'error' in result:
                        st.error(f"❌ Error: {result['error']}")
                    else:
                        if result['correct']:
                            st.success("✅ Test Passed!")
                        else:
                            st.error("❌ Test Failed!")
                        
                        st.write(f"Result: {result['result']}")
                        st.write(f"Expected: {result['expected']}")
                        st.write(f"Score: {result['score']}/{result['total']}")
        
        with col2:
            if st.button("👁️ Show Solution"):
                if problem_id in self.problem_bank.problems:
                    st.code(self.problem_bank.problems[problem_id].snippet)
                st.session_state.quiz_data = None
    
    def show_explain_mode(self):
        """Show explain mode interface."""
        if not st.session_state.quiz_data:
            self.select_problem_for_mode('explain')
            return
        
        st.header("📚 Explain Mode")
        
        data = st.session_state.quiz_data
        st.subheader(data['problem_title'])
        st.write(f"**Concept:** {data['concept']}")
        
        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📝 Code Snippet")
            st.code(data['snippet'])
        
        with col2:
            st.subheader("🔑 Key Points")
            for point in data['key_points']:
                st.write(f"• {point}")
        
        st.markdown("---")
        
        st.subheader("🐛 Common Bugs to Watch For")
        for bug in data['common_bugs']:
            st.warning(f"• {bug}")
        
        st.info("💡 Explain how this code works out loud to reinforce your understanding!")
        
        if st.button("🔄 Try Another Problem"):
            st.session_state.quiz_data = None
            st.rerun()
    
    def select_problem_for_mode(self, mode: str):
        """Show problem selection interface."""
        st.header(f"Select a Problem for {mode.replace('_', ' ').title()}")
        
        # Group problems by concept
        concepts = {}
        for problem in self.problem_bank.problems.values():
            concept = problem.concept
            if concept not in concepts:
                concepts[concept] = []
            concepts[concept].append(problem)
        
        selected_concept = st.selectbox(
            "Choose a concept:",
            list(concepts.keys())
        )
        
        if selected_concept:
            problems = concepts[selected_concept]
            problem_titles = [p.title for p in problems]
            
            selected_title = st.selectbox(
                "Choose a problem:",
                problem_titles
            )
            
            if selected_title:
                selected_problem = next(p for p in problems if p.title == selected_title)
                
                if st.button("Start Practice"):
                    if mode == 'flashcard':
                        st.session_state.quiz_data = self.quiz_engine.start_flashcard_mode(selected_problem)
                    elif mode == 'unit_test':
                        st.session_state.quiz_data = self.quiz_engine.start_unit_test_mode(selected_problem)
                    elif mode == 'explain':
                        st.session_state.quiz_data = self.quiz_engine.start_explain_mode(selected_problem)
                    
                    st.session_state.quiz_mode = mode
                    st.rerun()
    
    def start_random_practice(self):
        """Start random practice."""
        problem = self.problem_bank.get_random_problem()
        if problem:
            # Randomly choose a mode
            mode = random.choice(['flashcard', 'unit_test', 'explain'])
            
            if mode == 'flashcard':
                st.session_state.quiz_data = self.quiz_engine.start_flashcard_mode(problem)
            elif mode == 'unit_test':
                st.session_state.quiz_data = self.quiz_engine.start_unit_test_mode(problem)
            elif mode == 'explain':
                st.session_state.quiz_data = self.quiz_engine.start_explain_mode(problem)
            
            st.session_state.quiz_mode = mode
            st.rerun()
    
    def show_score_summary(self):
        """Show score summary in sidebar."""
        summary = self.quiz_engine.get_score_summary()
        
        st.metric("Score", f"{summary['score']}/{summary['total']}")
        st.metric("Accuracy", f"{summary['accuracy']}%")
        
        if st.button("🔄 Reset Score"):
            self.quiz_engine.score = 0
            self.quiz_engine.total_questions = 0
            st.rerun()


def main():
    """Main entry point for Streamlit app."""
    import os
    
    problem_bank_file = 'problem_bank.yaml'
    if not os.path.exists(problem_bank_file):
        st.error(f"Problem bank file not found: {problem_bank_file}")
        st.stop()
    
    try:
        web_interface = WebInterface(problem_bank_file)
        web_interface.run()
    except Exception as e:
        st.error(f"Failed to start web interface: {e}")


if __name__ == '__main__':
    main()
