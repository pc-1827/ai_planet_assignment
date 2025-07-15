import logging
import re
from typing import Dict, List, Optional, Tuple, Set

logger = logging.getLogger(__name__)

# Math-related keywords to detect math questions
MATH_KEYWORDS = {
    # General math terms
    "math", "mathematics", "equation", "formula", "calculate", "solve", "problem", 
    "arithmetic", "algebra", "calculus", "geometry", "trigonometry", "statistics",
    
    # Mathematical operations
    "add", "subtract", "multiply", "divide", "square", "cube", "root", "power",
    "exponent", "logarithm", "differentiate", "integrate", "derivative", "integral",
    
    # Mathematical concepts
    "function", "variable", "constant", "coefficient", "expression", "term",
    "polynomial", "fraction", "decimal", "percentage", "ratio", "proportion",
    "sequence", "series", "limit", "infinity", "vector", "matrix", "determinant",
    
    # Geometry terms
    "angle", "triangle", "square", "rectangle", "circle", "polygon", "sphere",
    "cube", "cylinder", "cone", "area", "volume", "perimeter", "circumference",
    
    # Number types
    "integer", "rational", "irrational", "real", "complex", "imaginary", "prime",
    "composite", "factorial", "odd", "even",
    
    # Probability and statistics
    "probability", "statistics", "mean", "median", "mode", "variance", "deviation",
    "distribution", "random", "sample", "hypothesis", "confidence"
}

# Non-math subjects to filter out non-math questions
NON_MATH_SUBJECTS = {
    "history", "geography", "politics", "art", "music", "literature", "language",
    "grammar", "spelling", "biology", "chemistry", "physics", "psychology", 
    "sociology", "economics", "business", "marketing", "philosophy", "ethics",
    "religion", "culture", "sports", "entertainment", "technology", "computing",
    "programming", "coding", "software", "hardware", "internet", "web", "app"
}

def is_math_question(question: str) -> Tuple[bool, str]:
    """
    Check if a question is related to mathematics.
    
    Args:
        question (str): The question to check
        
    Returns:
        Tuple[bool, str]: (is_math_related, reason)
    """
    # Convert to lowercase for case-insensitive matching
    question_lower = question.lower()
    
    # Check for explicitly non-math subjects
    for subject in NON_MATH_SUBJECTS:
        if subject in question_lower:
            return False, f"Question appears to be about {subject}, not mathematics."
    
    # Check for math keywords
    math_terms_found = []
    for keyword in MATH_KEYWORDS:
        # Use word boundary to match whole words only
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, question_lower):
            math_terms_found.append(keyword)
    
    # If we found math keywords
    if math_terms_found:
        return True, f"Math-related terms found: {', '.join(math_terms_found[:3])}"
    
    # Check for mathematical symbols
    math_symbols = ['+', '-', '*', '/', '=', '<', '>', '≤', '≥', '≠', '±', '∫', '∑', '∏', '∂', '√']
    found_symbols = [sym for sym in math_symbols if sym in question]
    
    if found_symbols:
        return True, f"Mathematical symbols found: {', '.join(found_symbols)}"
    
    # Check for numbers and numerical patterns
    has_numbers = bool(re.search(r'\d+', question))
    has_equation_pattern = bool(re.search(r'\d+\s*[+\-*/^=]\s*\d+', question))
    
    if has_equation_pattern:
        return True, "Question contains what appears to be a mathematical expression"
    
    if has_numbers and len(question.split()) < 15:
        return True, "Short question with numbers is likely math-related"
        
    # If uncertain, check for question patterns common in math problems
    math_question_patterns = [
        r'find the',
        r'calculate the',
        r'solve for',
        r'what is the value',
        r'how many',
        r'prove that',
        r'simplify',
        r'evaluate',
        r'factor'
    ]
    
    for pattern in math_question_patterns:
        if re.search(pattern, question_lower):
            return True, f"Question contains math problem pattern: '{pattern}'"
    
    # Default: if we're not sure, assume it's not math
    return False, "No clear mathematical content detected"

def validate_math_solution(solution: Dict) -> Tuple[bool, str]:
    """
    Check if a solution is a valid mathematical solution with proper steps.
    
    Args:
        solution (Dict): The solution dictionary containing 'solution' and 'steps'
        
    Returns:
        Tuple[bool, str]: (is_valid, reason)
    """
    # Check if solution exists
    if not solution or not isinstance(solution, dict):
        return False, "No solution provided"
    
    # Check if solution has content
    solution_text = solution.get("solution", "")
    steps = solution.get("steps", [])
    
    if not solution_text.strip():
        return False, "Solution is empty"
    
    # Check if steps exist and are not empty
    if not steps or not isinstance(steps, list) or len(steps) == 0:
        return False, "No steps provided in the solution"
    
    # Check if there are enough steps (at least 2 for a proper explanation)
    if len(steps) < 2:
        return False, "Solution doesn't have enough steps for a proper explanation"
    
    # Check if steps have content
    empty_steps = [i for i, step in enumerate(steps) if not step or not step.strip()]
    if empty_steps:
        return False, f"Empty steps found at positions: {empty_steps}"
    
    # Check for mathematical content in solution and steps
    math_content_found = False
    math_terms = set()
    
    # Check solution for math terms
    for keyword in MATH_KEYWORDS:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, solution_text.lower()):
            math_terms.add(keyword)
            math_content_found = True
    
    # Check steps for math terms
    for step in steps:
        for keyword in MATH_KEYWORDS:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, step.lower()):
                math_terms.add(keyword)
                math_content_found = True
    
    if not math_content_found:
        return False, "No mathematical content found in solution or steps"
    
    # Check for mathematical symbols
    math_symbols = ['+', '-', '*', '/', '=', '<', '>', '≤', '≥', '≠', '±', '∫', '∑', '∏', '∂', '√']
    symbols_in_solution = [sym for sym in math_symbols if sym in solution_text]
    
    has_symbols_in_steps = False
    for step in steps:
        if any(sym in step for sym in math_symbols):
            has_symbols_in_steps = True
            break
    
    # Solution looks valid
    return True, f"Valid mathematical solution with {len(steps)} steps"