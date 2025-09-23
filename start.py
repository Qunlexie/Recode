#!/usr/bin/env python3
"""
Startup script for the Coding Interview Revision System.
Provides easy access to different modes.
"""

import sys
import os
import subprocess


def main():
    """Main startup function."""
    print("🎯 Coding Interview Revision System")
    print("=" * 50)
    print("Choose your preferred interface:")
    print()
    print("1. 🌐 Web Interface (Streamlit) - Recommended for beginners")
    print("2. 💻 Command Line Interface - For power users")
    print("3. 🎮 Demo Mode - See how it works")
    print("4. ❓ Help - Learn more about the system")
    print()
    
    while True:
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            print("🚀 Starting web interface...")
            print("The interface will open in your browser automatically.")
            print("Press Ctrl+C to stop the server.")
            try:
                subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'web_app.py'], check=True)
            except KeyboardInterrupt:
                print("\n👋 Web interface stopped.")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error starting web interface: {e}")
            break
            
        elif choice == '2':
            print("🚀 Starting command line interface...")
            try:
                subprocess.run([sys.executable, 'cli.py'], check=True)
            except KeyboardInterrupt:
                print("\n👋 CLI stopped.")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error starting CLI: {e}")
            break
            
        elif choice == '3':
            print("🎮 Running demo...")
            try:
                subprocess.run([sys.executable, 'demo.py'], check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Error running demo: {e}")
            break
            
        elif choice == '4':
            show_help()
            continue
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")


def show_help():
    """Show help information."""
    print("\n📚 About the Coding Interview Revision System")
    print("=" * 50)
    print("""
This system helps you practice coding interview problems efficiently by focusing on:

🎯 Core Concepts: Instead of full problems, practice 5-10 lines of critical code
🃏 Flashcard Mode: Test your knowledge of key code snippets  
🧪 Unit Test Mode: Practice handling edge cases
📚 Explain Mode: Review concepts and common pitfalls

Key Benefits:
• Time Efficient: 5-10 minutes per session
• Focused Practice: Only the hard parts of problems
• Edge Case Training: Builds intuition for tricky inputs
• Pattern Recognition: Covers breadth of interview patterns

The system includes problems for:
• Hash Map Lookup (Two Sum)
• Binary Search
• DFS/BFS Traversal
• Sliding Window

You can add more problems by editing problem_bank.yaml
""")


if __name__ == '__main__':
    main()
