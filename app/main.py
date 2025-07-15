from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Make sure this import is present
from .models import QuestionRequest, SolutionResponse, FeedbackRequest, FeedbackResponse
from .vector_store import VectorStore
from .llm_service import LlamaService
from .feedback_store import FeedbackStore
import logging
from dotenv import load_dotenv
from .agent.graph import run_math_agent
from .guardrails import is_math_question, validate_math_solution

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Math Professor Agent with LangGraph")

# Add CORS middleware - THIS MUST COME BEFORE ANY ROUTE DEFINITIONS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],  # Include both possible frontend ports
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicitly include OPTIONS
    allow_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Initialize services
vector_store = VectorStore()
llm_service = LlamaService(model_name="llama3:latest")
feedback_store = FeedbackStore()

@app.post("/solve", response_model=SolutionResponse)
async def solve_problem(request: QuestionRequest):
    """
    Solve a mathematical problem with step-by-step explanation using LangGraph agent
    """
    try:
        question = request.question
        logger.info(f"Received question: {question}")
        
        # INPUT GUARDRAIL: Check if question is math-related
        is_math, reason = is_math_question(question)
        
        if not is_math:
            logger.warning(f"Non-math question rejected: {question} - Reason: {reason}")
            return SolutionResponse(
                solution="I can only help with mathematics questions. Please ask a question related to mathematics.",
                steps=[],  # Empty steps as requested
                source_retrieved=False,
                reference_id=None
            )
        
        logger.info(f"Question accepted as math-related: {reason}")
        
        # Check if we have similar questions with good feedback
        similar_solutions = feedback_store.get_similar_questions_with_feedback(question)
        
        # Run the LangGraph agent
        result = await run_math_agent(question)
        
        # Extract the solution from the result
        solution_data = result.get("solution", {})
        
        if not solution_data:
            raise HTTPException(status_code=500, detail="Failed to generate solution")
        
        # OUTPUT GUARDRAIL: Validate the solution
        is_valid_solution, validation_reason = validate_math_solution(solution_data)
        
        if not is_valid_solution:
            logger.warning(f"Invalid solution generated: {validation_reason}")
            # Try to regenerate with the legacy approach
            return await legacy_solve_problem(request)
        
        logger.info(f"Solution validated: {validation_reason}")
        
        # Store the solution to get an ID for feedback
        solution_id = feedback_store.store_solution(question, solution_data)
        
        # Add the solution ID to the reference_id field so it can be used for feedback
        solution_data["reference_id"] = solution_id
        
        # Return the solution
        return SolutionResponse(
            solution=solution_data.get("solution", ""),
            steps=solution_data.get("steps", []),
            source_retrieved=solution_data.get("source_retrieved", False),
            reference_id=solution_id  # Use the feedback store ID
        )
    except Exception as e:
        logger.error(f"Error solving problem: {e}")
        # Fallback to the original implementation if the agent fails
        return await legacy_solve_problem(request)

@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback for a solution and get an improved solution if correction is provided
    """
    try:
        # Store the feedback
        success = feedback_store.add_feedback(
            solution_id=request.solution_id,
            rating=request.rating,
            feedback_text=request.feedback_text,
            correction=request.correction
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Solution with ID {request.solution_id} not found")
        
        # Get the original solution with the feedback
        solution_with_feedback = feedback_store.get_solution_with_feedback(request.solution_id)
        
        improved_solution = None
        
        # If correction was provided, use it to generate an improved solution
        if request.correction:
            original_question = solution_with_feedback["question"]
            
            # Create a prompt that incorporates the feedback
            prompt = f"""You are a mathematics professor. You previously provided a solution to this question:
            
Question: {original_question}

Your solution had some issues, and a human expert has provided the following correction:
{request.correction}

Please provide an improved solution incorporating this feedback. Format your response as:
SOLUTION: [concise final answer]
STEPS:
1. [first step]
2. [second step]
...and so on.
"""
            
            # Generate improved solution
            improved_data = await llm_service.generate_solution(question=prompt)
            
            # Validate the improved solution
            is_valid, _ = validate_math_solution(improved_data)
            
            if is_valid:
                improved_solution = SolutionResponse(
                    solution=improved_data["solution"],
                    steps=improved_data["steps"],
                    source_retrieved=False,
                    reference_id=request.solution_id
                )
        
        return FeedbackResponse(
            success=True,
            message="Feedback submitted successfully. Thank you for helping improve our system!",
            improved_solution=improved_solution
        )
        
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing feedback: {str(e)}")

async def legacy_solve_problem(request: QuestionRequest):
    """
    Legacy implementation as fallback
    """
    # First check if we have a similar question in our vector store
    similar_question = vector_store.search_similar_question(request.question)
    
    # If we found a very similar question (high similarity score), use its solution directly
    if similar_question and similar_question["score"] > 0.90:
        logger.info(f"Found very similar question with score {similar_question['score']}, using stored solution directly")
        
        # Extract the stored solution
        solution_data = {
            "solution": similar_question["payload"].get("solution", ""),
            "steps": similar_question["payload"].get("steps", []),
            "source_retrieved": True,
            "reference_id": similar_question["id"]
        }
        
        # Store the solution to get an ID for feedback
        solution_id = feedback_store.store_solution(request.question, solution_data)
        
        return SolutionResponse(
            solution=solution_data["solution"],
            steps=solution_data["steps"],
            source_retrieved=True,
            reference_id=solution_id  # Use the feedback store ID
        )
    
    # If no similar question found or similarity is below threshold, use LLM
    logger.info(f"Using LLM to generate solution")
    solution_data = await llm_service.generate_solution(
        question=request.question,
        retrieved_data=similar_question
    )
    
    # Apply output guardrail to LLM solution as well
    is_valid_solution, validation_reason = validate_math_solution(solution_data)
    
    if not is_valid_solution:
        logger.warning(f"Invalid solution from legacy method: {validation_reason}")
        # Return a more helpful response instead of an invalid solution
        return SolutionResponse(
            solution="I couldn't generate a valid mathematical solution for your question.",
            steps=[
                "I was unable to produce a proper mathematical answer with step-by-step explanation.",
                "This might be because your question isn't clear enough or may not be a standard mathematical problem.",
                "Please try rephrasing your question to focus on the mathematical aspects."
            ],
            source_retrieved=False,
            reference_id=None
        )
    
    # Store the solution to get an ID for feedback
    solution_id = feedback_store.store_solution(request.question, solution_data)
    
    # Prepare response
    return SolutionResponse(
        solution=solution_data["solution"],
        steps=solution_data["steps"],
        source_retrieved=similar_question is not None,
        reference_id=solution_id  # Use the feedback store ID
    )

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)