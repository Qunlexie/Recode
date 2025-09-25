# 🚀 Recode - NeetCode 150 Flashcards

A streamlined flashcard app for coding interview practice featuring the complete **NeetCode 150** problem set.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run run.py
```

Access at `http://localhost:8501`

## Features

- **142 NeetCode 150 Problems** - Complete problem set with solutions
- **Smart Filtering** - By difficulty, category, and progress
- **Progress Tracking** - Track mastery and review history
- **Code Execution** - Test solutions with real-time feedback
- **Clean Interface** - Mobile-friendly, distraction-free design

## Project Structure

```
Recode/
├── src/
│   ├── app.py                  # Main Streamlit app
│   ├── database_setup.py       # NeetCode 150 import script
│   ├── database_utils.py       # Database operations
│   ├── code_validator.py       # Code validation & formatting
│   └── batch_code_cleaner.py   # Batch cleaning utilities
├── .streamlit/config.toml     # Streamlit configuration
├── recode.db                  # SQLite database (142 problems)
├── requirements.txt           # Dependencies
├── run.py                     # Entry point
└── README.md                  # This file
```

## Adding Problems

Use the sidebar form in the app or edit the database directly. Problems are automatically validated and formatted.

## Categories

Arrays & Hashing • Two Pointers • Sliding Window • Stack • Binary Search • Linked List • Trees • Tries • Heap/Priority Queue • Backtracking • Graphs • Advanced Graphs • 1-D DP • 2-D DP • Greedy • Intervals • Math & Geometry • Bit Manipulation

Perfect for coding interview preparation! 🎯