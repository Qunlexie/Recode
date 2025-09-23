# 🎯 Coding Interview Revision System

A focused practice system for coding interview preparation that breaks problems down into core concepts and provides targeted revision through multiple practice modes.

## 🚀 Features

- **Core Concept Focus**: Instead of full problems, practice 5-10 lines of critical code
- **Multiple Practice Modes**:
  - 🃏 **Flashcard Mode**: Test knowledge of key code snippets
  - 🧪 **Unit Test Mode**: Practice handling edge cases
  - 📚 **Explain Mode**: Review concepts and common pitfalls
- **Smart Tagging**: Filter by data structure, pattern, complexity, difficulty
- **Edge Case Testing**: Automated testing harness for common pitfalls
- **Progress Tracking**: Score tracking and accuracy metrics

## 📦 Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🎮 Usage

### Command Line Interface

Start the CLI:
```bash
python cli.py
```

Available commands:
- `list` - List all available concepts
- `practice <concept>` - Practice a specific concept
- `random` - Practice a random concept
- `flashcard <problem_id>` - Start flashcard mode
- `test <problem_id>` - Start unit test mode
- `explain <problem_id>` - Start explain mode
- `score` - Show current score

### Web Interface

Start the Streamlit web app:
```bash
streamlit run web_app.py
```

The web interface provides a more visual and interactive experience with:
- Problem selection by concept
- Real-time code editing
- Progress tracking
- Multiple practice modes

## 📚 Problem Bank Structure

Problems are stored in `problem_bank.yaml` with the following structure:

```yaml
problems:
  - id: "two_sum"
    title: "Two Sum"
    concept: "Hash Map Lookup"
    description: "Find two numbers that add up to target"
    snippet: |
      def two_sum(nums, target):
          seen = {}
          for i, num in enumerate(nums):
              complement = target - num
              if complement in seen:
                  return [seen[complement], i]
              seen[num] = i
          return []
    tags:
      - data_structure: "hashmap"
      - pattern: "hash_map_lookup"
      - complexity: "O(n)"
      - difficulty: "easy"
    test_cases:
      - input: "nums=[2,7,11,15], target=9"
        expected: "[0,1]"
        edge_case: false
    quiz_questions:
      - question: "What line stores the current number and its index?"
        answer: "seen[num] = i"
        context: "After checking if complement exists"
```

## 🎯 Practice Modes

### 1. Flashcard Mode
- Tests recall of critical code lines
- Focuses on the "aha!" moments
- Instant feedback on answers

### 2. Unit Test Mode
- Practice handling edge cases
- Modify code snippets to pass tests
- Learn common bug patterns

### 3. Explain Mode
- Review complete solutions
- Understand common pitfalls
- Reinforce conceptual understanding

## 🔧 Adding New Problems

To add a new problem:

1. Edit `problem_bank.yaml`
2. Add a new problem entry with:
   - Unique ID and title
   - Core concept description
   - Minimal code snippet (5-10 lines)
   - Relevant tags
   - Test cases (including edge cases)
   - Quiz questions for flashcard mode

## 🎨 Customization

The system is designed to be easily extensible:

- **Add new practice modes** by extending the `QuizEngine` class
- **Customize problem selection** by modifying the filtering logic
- **Add new problem sources** by implementing different parsers
- **Extend the web interface** by adding new Streamlit components

## 📊 Benefits

- **Time Efficient**: 5-10 minutes per session
- **Focused Practice**: Only the hard parts of problems
- **Edge Case Training**: Builds intuition for tricky inputs
- **Pattern Recognition**: Covers breadth of interview patterns
- **Progress Tracking**: Measure improvement over time

## 🤝 Contributing

Feel free to:
- Add new problems to the problem bank
- Improve the user interface
- Add new practice modes
- Enhance the testing framework

## 📄 License

MIT License - feel free to use and modify as needed!