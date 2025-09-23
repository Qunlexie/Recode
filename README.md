# 🃏 Simple Coding Interview Flashcards

A clean, simple flashcard app for coding interview practice. Easy to add new questions!

## 🚀 Quick Start

1. **Install dependencies:**
```bash
pip install streamlit
```

2. **Run the app:**
```bash
python3 -m streamlit run app.py
```

3. **Access:** Go to `http://localhost:8501`

## ➕ Adding New Questions

Super easy! Just edit `questions.py`:

```python
QUESTIONS = [
    {
        "title": "Your Question Title",
        "question": """
Your question text here...
With examples if needed.
        """,
        "answer": """
Your answer here...
With code and explanation.
        """
    },
    # Add more questions...
]
```

## 📱 Mobile Ready

- Touch-friendly buttons
- Clean, simple interface
- Works great on phones

## 🎯 Features

- **Simple**: Just question → answer
- **Clean**: No distractions
- **Random**: Questions appear randomly
- **Easy to edit**: Add questions in one file

Perfect for quick coding interview practice! 🎯