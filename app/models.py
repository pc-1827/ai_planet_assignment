from pydantic import BaseModel
from typing import List, Optional

class QuestionRequest(BaseModel):
    question: str

class SolutionResponse(BaseModel):
    solution: str
    steps: List[str]
    source_retrieved: bool
    reference_id: Optional[str] = None

# New models for feedback system
class FeedbackRequest(BaseModel):
    solution_id: str
    rating: int  # 1-5 rating
    feedback_text: Optional[str] = None
    correction: Optional[str] = None
    
class FeedbackResponse(BaseModel):
    success: bool
    message: str
    improved_solution: Optional[SolutionResponse] = None