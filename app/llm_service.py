import httpx
import json
import logging
from typing import List, Dict, Optional
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LlamaService:
    def __init__(self, model_name: str = "llama3:latest", timeout: float = 120.0):
        self.base_url = "http://localhost:11434/api"
        self.model_name = model_name
        self.timeout = timeout  # Increased timeout
    
    async def check_model_status(self) -> bool:
        """Check if Ollama is running and the model is available"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    return any(model["name"] == self.model_name for model in models)
                return False
        except Exception as e:
            logger.error(f"Error checking Ollama status: {e}")
            return False

    async def generate_solution(self, question: str, retrieved_data: Optional[Dict] = None) -> Dict:
        # First check if Ollama is running and model is available
        model_available = await self.check_model_status()
        if not model_available:
            logger.warning(f"Model {self.model_name} not available, falling back to simple response")
            return self._fallback_solution(question)
        
        # Prepare the prompt based on whether we have retrieved data
        if retrieved_data:
            prompt = self._create_prompt_with_reference(question, retrieved_data)
        else:
            prompt = self._create_prompt_without_reference(question)
        
        logger.info(f"Sending request to Ollama with prompt length: {len(prompt)}")
        
        # Call Ollama API with increased timeout and retry logic
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/generate",
                        json={
                            "model": self.model_name,
                            "prompt": prompt,
                            "stream": False
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"Successfully received response from Ollama")
                        # Parse the response to extract solution and steps
                        return self._parse_solution(result["response"])
                    else:
                        logger.error(f"Error from Ollama API: {response.text}")
                        if attempt < max_retries:
                            wait_time = (attempt + 1) * 2  # Exponential backoff
                            logger.info(f"Retrying in {wait_time} seconds...")
                            await asyncio.sleep(wait_time)
                        else:
                            return self._fallback_solution(question)
            except httpx.ReadTimeout:
                logger.error(f"Timeout while waiting for Ollama response (attempt {attempt + 1}/{max_retries + 1})")
                if attempt < max_retries:
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    return self._fallback_solution(question)
            except Exception as e:
                logger.error(f"Unexpected error calling Ollama API: {e}")
                return self._fallback_solution(question)
    
    def _fallback_solution(self, question: str) -> Dict:
        """Provide a fallback solution when Ollama is unavailable"""
        return {
            "solution": "Unable to generate solution due to API timeout",
            "steps": [
                "The Llama3 model is currently unavailable or taking too long to respond.",
                "Please try again later or with a simpler question.",
                f"Your question was: {question}"
            ]
        }
    
    def _create_prompt_with_reference(self, question: str, retrieved_data: Dict) -> str:
        # Truncate original solution if it's too long (over 2000 chars)
        # This helps prevent timeouts with very large contexts
        if "original_solution" in retrieved_data['payload']:
            original_solution = retrieved_data['payload']['original_solution']
            if len(original_solution) > 2000:
                original_solution = original_solution[:2000] + "... [truncated for brevity]"
            
            return f"""You are a highly knowledgeable mathematics professor. 
            
I have a question similar to one in our database. Please provide a step-by-step solution.

Original question from database: {retrieved_data['payload']['question']}

Original detailed solution: 
{original_solution}

My current question is: {question}

Please provide a detailed step-by-step solution to my current question, adapting the approach from the original solution if applicable. Format your response as follows:
SOLUTION: [concise final answer]
STEPS:
1. [first step]
2. [second step]
...and so on.
"""
        else:
            return f"""You are a highly knowledgeable mathematics professor. 
            
I have a question similar to one in our database. Please provide a step-by-step solution.

Original question from database: {retrieved_data['payload']['question']}
Original solution: {retrieved_data['payload']['solution']}
Original steps: {', '.join(retrieved_data['payload']['steps'])}

My current question is: {question}

Please provide a detailed step-by-step solution to my current question, adapting the approach from the original solution if applicable. Format your response as follows:
SOLUTION: [concise final answer]
STEPS:
1. [first step]
2. [second step]
...and so on.
"""

    def _create_prompt_without_reference(self, question: str) -> str:
        return f"""You are a highly knowledgeable mathematics professor.

I have the following question: {question}

Please provide a detailed step-by-step solution. Format your response as follows:
SOLUTION: [concise final answer]
STEPS:
1. [first step]
2. [second step]
...and so on.
"""

    def _parse_solution(self, response: str) -> Dict:
        # Extract solution and steps from the LLM response
        solution = ""
        steps = []
        
        # Simple parsing logic - can be improved
        if "SOLUTION:" in response:
            parts = response.split("STEPS:")
            solution = parts[0].replace("SOLUTION:", "").strip()
            
            if len(parts) > 1:
                steps_text = parts[1].strip()
                # Extract numbered steps
                import re
                steps = [step.strip() for step in re.findall(r'\d+\.\s*(.*?)(?=\d+\.|$)', steps_text, re.DOTALL)]
        else:
            # Fallback if formatting is not followed
            solution = response
            steps = ["No structured steps available"]
        
        return {
            "solution": solution,
            "steps": steps
        }