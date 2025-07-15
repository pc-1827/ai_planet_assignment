from typing import Dict, List, Annotated, Any, TypedDict, Literal
import logging
from langgraph.graph import END, StateGraph
import httpx
from ..vector_store import VectorStore
from ..llm_service import LlamaService
from ..web_search_client import WebSearchClient
from ..mcp_client import MCPClient
from ..feedback_store import FeedbackStore

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the agent state
class AgentState(TypedDict):
    """State for the math agent graph."""
    question: str
    vector_search_result: Dict | None
    web_search_result: List[Dict] | None
    solution: Dict | None
    error: str | None
    steps: List[str]
    next: Literal["search_vector_db", "search_web", "generate_solution", "end"]

# Node functions
async def search_vector_db(state: AgentState) -> AgentState:
    """Search the vector database for similar questions."""
    try:
        question = state["question"]
        logger.info(f"Searching vector DB for: {question}")
        
        vector_store = VectorStore(collection_name="math_questions")
        similar_question = vector_store.search_similar_question(question)
        
        if similar_question and similar_question["score"] > 0.90:
            logger.info(f"Found very similar question with score {similar_question['score']}")
            state["vector_search_result"] = similar_question
            # For very similar questions, skip web search and go directly to solution
            state["next"] = "generate_solution"
        else:
            logger.info("No similar question found in vector DB or similarity below threshold")
            state["vector_search_result"] = None
            state["next"] = "search_web"
        
        return state
    
    except Exception as e:
        logger.error(f"Error searching vector DB: {e}")
        state["error"] = f"Vector DB search error: {str(e)}"
        state["next"] = "search_web"  # Fallback to web search
        return state

async def search_web(state: AgentState) -> AgentState:
    """Search the web using the WebSearch MCP server."""
    try:
        question = state["question"]
        logger.info(f"Searching web for: {question}")
        
        # Use the proper MCP client with our custom server
        mcp_client = MCPClient("http://localhost:3000/mcp")
        
        # Initialize the MCP session
        init_success = await mcp_client.initialize()
        if not init_success:
            logger.error("Failed to initialize MCP session")
            state["error"] = "Failed to initialize MCP session"
            state["web_search_result"] = []
            state["next"] = "generate_solution"
            return state
        
        # Perform the web search using the MCP tool
        search_results = await mcp_client.web_search(
            query=f"math problem solution: {question}",
            limit=5,
            engines=["exa"]  # Change from "bing" to "exa"
        )
        
        # Close the MCP session
        await mcp_client.close()
        
        if search_results:
            logger.info(f"Found {len(search_results)} web search results")
            state["web_search_result"] = search_results
        else:
            logger.warning("Web search returned no results")
            state["web_search_result"] = []
        
        state["next"] = "generate_solution"
        return state
    
    except Exception as e:
        logger.error(f"Error searching web: {e}")
        state["error"] = f"Web search error: {str(e)}"
        state["web_search_result"] = []
        state["next"] = "generate_solution"  # Continue to solution generation with what we have
        return state

async def generate_solution(state: AgentState) -> AgentState:
    """Generate a solution based on vector DB results or web search results."""
    try:
        llm_service = LlamaService(model_name="llama3:latest")
        feedback_store = FeedbackStore()
        
        # Check if we have similar questions with good feedback
        similar_solutions = feedback_store.get_similar_questions_with_feedback(state["question"])
        
        # If we have similar solutions with good feedback, use them to enhance the prompt
        feedback_context = ""
        if similar_solutions:
            feedback_context = "I've found some similar questions with expert feedback that might be helpful:\n\n"
            for i, solution in enumerate(similar_solutions[:2]):  # Use at most 2 examples
                feedback_context += f"Example {i+1}:\n"
                feedback_context += f"Question: {solution['question']}\n"
                feedback_context += f"Solution: {solution['solution'].get('solution', '')}\n"
                
                # Get the highest-rated feedback with a correction
                best_feedback = None
                for feedback_id in solution["feedback"]:
                    feedback = feedback_store.feedback.get(feedback_id)
                    if feedback and feedback.get("correction") and (not best_feedback or feedback["rating"] > best_feedback["rating"]):
                        best_feedback = feedback
                
                if best_feedback and best_feedback.get("correction"):
                    feedback_context += f"Expert correction: {best_feedback['correction']}\n\n"
                else:
                    feedback_context += "\n"

        # If we have a very similar question in the vector DB, use it directly
        if state["vector_search_result"] and state["vector_search_result"]["score"] > 0.95:
            # Use the solution from vector DB directly
            similar_question = state["vector_search_result"]
            payload = similar_question["payload"]
            
            solution = payload.get("solution", "")
            steps = payload.get("steps", [])
            
            logger.info("Using solution directly from vector DB")
            state["solution"] = {
                "solution": solution,
                "steps": steps,
                "source_retrieved": True,
                "reference_id": similar_question["id"]
            }
            
        elif state["vector_search_result"]:
            # We have a similar question but not exact, use LLM with the context
            logger.info("Generating solution with LLM using vector DB context")
            
            # Add feedback context to the prompt if available
            if feedback_context:
                # Create a special prompt that includes feedback
                question_with_feedback = f"""You are a mathematics professor solving the following question:

{state["question"]}

{feedback_context}

Based on these examples and any corrections, please provide a detailed and accurate solution to the original question.
"""
                solution_data = await llm_service.generate_solution(
                    question=question_with_feedback,
                    retrieved_data=state["vector_search_result"]
                )
            else:
                solution_data = await llm_service.generate_solution(
                    question=state["question"],
                    retrieved_data=state["vector_search_result"]
                )
            
            state["solution"] = {
                "solution": solution_data["solution"],
                "steps": solution_data["steps"],
                "source_retrieved": True,
                "reference_id": state["vector_search_result"]["id"]
            }
            
        elif state["web_search_result"] and len(state["web_search_result"]) > 0:
            # Use web search results to generate a solution
            logger.info("Generating solution using web search results")
            
            # Create a prompt with web search results
            search_context = ""
            for i, result in enumerate(state["web_search_result"]):
                search_context += f"\n[{i+1}] {result['title']}\n"
                search_context += f"URL: {result['url']}\n"
                search_context += f"Description: {result['description']}\n\n"
            
            # Create a special prompt for the LLM with web search results
            # Include feedback context if available
            prompt = f"""You are a mathematics professor expert at solving math problems step by step.
            
I need help solving this math problem: 
"{state['question']}"

I've found the following information from the web that might be helpful:

{search_context}

{feedback_context}

Please provide a detailed step-by-step solution to the problem. Format your response as follows:
SOLUTION: [concise final answer]
STEPS:
1. [first step]
2. [second step]
...and so on.

Use mathematical notation where appropriate and explain each step clearly.
"""
            
            # Generate solution using Llama 3
            solution_data = await llm_service.generate_solution(
                question=prompt  # Use the entire prompt as the "question"
            )
            
            state["solution"] = {
                "solution": solution_data["solution"],
                "steps": solution_data["steps"],
                "source_retrieved": False,
                "reference_id": None
            }
            
        else:
            # No information available, generate a simple response
            logger.info("No information available, generating basic solution")
            
            # Include feedback context if available
            if feedback_context:
                prompt = f"""You are a mathematics professor solving the following question:

{state["question"]}

{feedback_context}

Based on these examples and any corrections, please provide a detailed and accurate solution to the original question.
Format your response as follows:
SOLUTION: [concise final answer]
STEPS:
1. [first step]
2. [second step]
...and so on.
"""
                solution_data = await llm_service.generate_solution(
                    question=prompt
                )
            else:
                solution_data = await llm_service.generate_solution(
                    question=state["question"]
                )
            
            state["solution"] = {
                "solution": solution_data["solution"],
                "steps": solution_data["steps"],
                "source_retrieved": False,
                "reference_id": None
            }
        
        state["next"] = "end"
        return state
    
    except Exception as e:
        logger.error(f"Error generating solution: {e}")
        state["error"] = f"Solution generation error: {str(e)}"
        state["solution"] = {
            "solution": "Error generating solution.",
            "steps": [f"An error occurred: {str(e)}"]
        }
        state["next"] = "end"
        return state

# State transition function
def decide_next_step(state: AgentState) -> Literal["search_vector_db", "search_web", "generate_solution", "end"]:
    """Determine the next step based on the current state."""
    return state["next"]

# Create the graph
def create_agent_graph():
    """Create and return the math agent graph."""
    # Define the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("search_vector_db", search_vector_db)
    workflow.add_node("search_web", search_web)
    workflow.add_node("generate_solution", generate_solution)
    
    # Add edges
    workflow.add_conditional_edges(
        "search_vector_db",
        decide_next_step,
        {
            "search_web": "search_web",
            "generate_solution": "generate_solution",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "search_web",
        decide_next_step,
        {
            "generate_solution": "generate_solution", 
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "generate_solution",
        decide_next_step,
        {
            "end": END
        }
    )
    
    # Set the entry point
    workflow.set_entry_point("search_vector_db")
    
    # Compile the graph
    return workflow.compile()

# Create a function to run the agent
async def run_math_agent(question: str):
    """Run the math agent with a given question."""
    # Create the graph
    graph = create_agent_graph()
    
    # Run the graph
    result = await graph.ainvoke(
        {
            "question": question,
            "vector_search_result": None,
            "web_search_result": None,
            "solution": None,
            "error": None,
            "steps": [],
            "next": "search_vector_db"
        }
    )
    
    return result