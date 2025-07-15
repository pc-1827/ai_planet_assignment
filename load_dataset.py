import json
import os
import glob
from typing import Dict, Any, List
from app.vector_store import VectorStore

def process_solution(solution_text: str) -> Dict[str, Any]:
    """
    Extract structured information from the solution text
    """
    # Initialize with defaults
    solution_parts = {
        "final_answer": "",
        "steps": []
    }
    
    # Extract final answer (usually at the end, marked with a box)
    if "Final Answer:" in solution_text:
        final_answer_part = solution_text.split("Final Answer:")[-1].strip()
        solution_parts["final_answer"] = final_answer_part
    elif "\\boxed{" in solution_text:
        # Look for LaTeX boxed expression which usually contains the final answer
        import re
        boxed_match = re.search(r'\\boxed{(.*?)}', solution_text)
        if boxed_match:
            solution_parts["final_answer"] = boxed_match.group(1)
    
    # Extract steps - assuming they are numbered in the solution text
    import re
    steps = re.findall(r'\d+\.\s+(.*?)(?=\d+\.\s+|\Z)', solution_text, re.DOTALL)
    if steps:
        solution_parts["steps"] = [step.strip() for step in steps]
    else:
        # If no numbered steps found, try another approach - split by sections
        sections = re.split(r'#{1,3}\s+\d+\.\s+', solution_text)
        if len(sections) > 1:
            solution_parts["steps"] = [section.strip() for section in sections[1:]]
    
    return solution_parts

def load_dataset(dataset_dir: str, vector_store: VectorStore) -> None:
    """
    Load math problems from dataset into vector store
    """
    # Get all JSON files in the dataset directory and subdirectories
    json_files = glob.glob(os.path.join(dataset_dir, "**/*.json"), recursive=True)
    print(f"Found {len(json_files)} problems in the dataset")
    
    for i, json_file in enumerate(json_files):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            problem = data.get("problem", "")
            solution_text = data.get("solution", "")
            
            # Process the solution to extract structured information
            solution_parts = process_solution(solution_text)
            
            # Add to vector store
            point_id = vector_store.add_question_solution(
                question=problem,
                solution=solution_parts.get("final_answer", ""),
                steps=solution_parts.get("steps", []),
                original_solution=solution_text  # Store the full solution text as well
            )
            
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(json_files)} problems")
                
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
    
    print(f"Successfully loaded {len(json_files)} problems into the vector store")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python load_dataset.py <dataset_directory>")
        sys.exit(1)
    
    dataset_dir = sys.argv[1]
    vector_store = VectorStore(collection_name="math_questions")
    
    load_dataset(dataset_dir, vector_store)