#!/usr/bin/env python3
"""
Session manager for dynamic Fill-in-the-Blanks variations.
Ensures blanks change every time while maintaining learning quality.
"""

import hashlib
import time
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class SessionState:
    """Session state for fill-in-blanks mode."""
    problem_id: int
    attempt_number: int
    difficulty: str
    session_seed: int
    created_at: float

class FillBlanksSessionManager:
    """Manages dynamic sessions for fill-in-blanks mode."""
    
    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}
    
    def get_session_key(self, problem_id: int, user_id: str = "default") -> str:
        """Generate a unique session key."""
        return f"{user_id}_{problem_id}"
    
    def get_session_seed(self, problem_id: int, difficulty: str = "medium", user_id: str = "default") -> int:
        """Get a dynamic session seed that changes each time."""
        session_key = self.get_session_key(problem_id, user_id)
        
        # Get or create session state
        if session_key not in self.sessions:
            self.sessions[session_key] = SessionState(
                problem_id=problem_id,
                attempt_number=1,
                difficulty=difficulty,
                session_seed=self._generate_seed(problem_id, 1, difficulty),
                created_at=time.time()
            )
        else:
            # Increment attempt number for new variation
            session = self.sessions[session_key]
            session.attempt_number += 1
            session.session_seed = self._generate_seed(problem_id, session.attempt_number, difficulty)
            session.created_at = time.time()
        
        return self.sessions[session_key].session_seed
    
    def get_new_variation_seed(self, problem_id: int, difficulty: str = "medium", user_id: str = "default") -> int:
        """Force a new variation by incrementing attempt number."""
        session_key = self.get_session_key(problem_id, user_id)
        
        if session_key in self.sessions:
            session = self.sessions[session_key]
            session.attempt_number += 1
            session.session_seed = self._generate_seed(problem_id, session.attempt_number, difficulty)
            session.created_at = time.time()
            return session.session_seed
        else:
            return self.get_session_seed(problem_id, difficulty, user_id)
    
    def _generate_seed(self, problem_id: int, attempt: int, difficulty: str) -> int:
        """Generate a deterministic but varying seed."""
        # Create a unique string combining problem, attempt, difficulty, and time component
        time_component = int(time.time() / 3600)  # Changes every hour for more variation
        seed_string = f"{problem_id}_{attempt}_{difficulty}_{time_component}"
        
        # Use hash to create a consistent but unpredictable seed
        hash_object = hashlib.md5(seed_string.encode())
        seed = int(hash_object.hexdigest()[:8], 16)
        
        return seed % (2**31 - 1)  # Keep within int32 range
    
    def get_session_info(self, problem_id: int, user_id: str = "default") -> Dict[str, Any]:
        """Get information about current session."""
        session_key = self.get_session_key(problem_id, user_id)
        
        if session_key in self.sessions:
            session = self.sessions[session_key]
            return {
                'attempt_number': session.attempt_number,
                'difficulty': session.difficulty,
                'session_seed': session.session_seed,
                'created_at': session.created_at
            }
        else:
            return {
                'attempt_number': 0,
                'difficulty': 'medium',
                'session_seed': 0,
                'created_at': 0
            }
    
    def reset_session(self, problem_id: int, user_id: str = "default"):
        """Reset session for a problem."""
        session_key = self.get_session_key(problem_id, user_id)
        if session_key in self.sessions:
            del self.sessions[session_key]
    
    def clean_old_sessions(self, max_age_hours: int = 24):
        """Clean up old sessions to prevent memory leaks."""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        keys_to_remove = []
        for key, session in self.sessions.items():
            if current_time - session.created_at > max_age_seconds:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.sessions[key]

# Global session manager instance
session_manager = FillBlanksSessionManager()
