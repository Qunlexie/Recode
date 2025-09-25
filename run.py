#!/usr/bin/env python3
"""
Entry point to run the Recode app.
Usage: python run.py or streamlit run run.py
"""

import sys
import os

# Add src to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main app
if __name__ == "__main__":
    from src.app import main
    main()
else:
    # When run with streamlit run run.py
    import src.app
