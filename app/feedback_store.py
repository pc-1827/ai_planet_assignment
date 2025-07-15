import logging
from typing import Dict, List, Optional, Any
import uuid
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class FeedbackStore:
    """Store and retrieve feedback for solutions"""
    
    def __init__(self, feedback_dir: str = "feedback_data"):
        self.feedback_dir = feedback_dir
        # Create directory if it doesn't exist
        os.makedirs(self.feedback_dir, exist_ok=True)
        self.solutions_file = os.path.join(self.feedback_dir, "solutions.json")
        self.feedback_file = os.path.join(self.feedback_dir, "feedback.json")
        
        # Initialize empty dictionaries
        self.solutions = self._load_json(self.solutions_file, {})
        self.feedback = self._load_json(self.feedback_file, {})
    
    def _load_json(self, filepath: str, default: Any) -> Any:
        """Load JSON data from file or return default if file doesn't exist"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
            return default
        except Exception as e:
            logger.error(f"Error loading JSON from {filepath}: {e}")
            return default
    
    def _save_json(self, filepath: str, data: Any) -> bool:
        """Save JSON data to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving JSON to {filepath}: {e}")
            return False
    
    def store_solution(self, question: str, solution_data: Dict) -> str:
        """Store a solution and return its ID"""
        solution_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        self.solutions[solution_id] = {
            "question": question,
            "solution": solution_data,
            "timestamp": timestamp,
            "feedback": []
        }
        
        self._save_json(self.solutions_file, self.solutions)
        return solution_id
    
    def add_feedback(self, solution_id: str, rating: int, feedback_text: Optional[str] = None, 
                    correction: Optional[str] = None) -> bool:
        """Add feedback for a solution"""
        if solution_id not in self.solutions:
            logger.error(f"Solution ID {solution_id} not found")
            return False
        
        feedback_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        feedback_data = {
            "id": feedback_id,
            "solution_id": solution_id,
            "rating": rating,
            "feedback_text": feedback_text,
            "correction": correction,
            "timestamp": timestamp
        }
        
        # Store in feedback dictionary
        self.feedback[feedback_id] = feedback_data
        
        # Also link to the solution
        self.solutions[solution_id]["feedback"].append(feedback_id)
        
        # Save both files
        self._save_json(self.feedback_file, self.feedback)
        self._save_json(self.solutions_file, self.solutions)
        
        return True
    
    def get_solution(self, solution_id: str) -> Optional[Dict]:
        """Get a solution by ID"""
        return self.solutions.get(solution_id)
    
    def get_solution_with_feedback(self, solution_id: str) -> Optional[Dict]:
        """Get a solution with all its feedback"""
        solution = self.solutions.get(solution_id)
        if not solution:
            return None
        
        # Add the full feedback data
        full_feedback = []
        for feedback_id in solution["feedback"]:
            if feedback_id in self.feedback:
                full_feedback.append(self.feedback[feedback_id])
        
        solution_copy = solution.copy()
        solution_copy["feedback"] = full_feedback
        return solution_copy
    
    def get_similar_questions_with_feedback(self, question: str, min_rating: int = 4) -> List[Dict]:
        """Get similar questions that received positive feedback"""
        # This is a simplified implementation
        # In a real system, you'd use vector similarity or keyword matching
        
        similar_solutions = []
        for solution_id, solution_data in self.solutions.items():
            # Check if solution has any feedback
            if not solution_data["feedback"]:
                continue
            
            # Check if at least one feedback has a rating >= min_rating
            has_good_feedback = False
            for feedback_id in solution_data["feedback"]:
                if feedback_id in self.feedback and self.feedback[feedback_id]["rating"] >= min_rating:
                    has_good_feedback = True
                    break
            
            if has_good_feedback:
                similar_solutions.append(solution_data)
        
        return similar_solutions