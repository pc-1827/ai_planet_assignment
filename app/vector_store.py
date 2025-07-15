import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Tuple

class VectorStore:
    def __init__(self, collection_name: str = "math_questions"):
        # Initialize the Qdrant client
        self.client = QdrantClient("localhost", port=6333)
        self.collection_name = collection_name
        
        # Check if collection exists, if not create it
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if self.collection_name not in collection_names:
            # Initialize sentence transformer model for encoding
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            vector_size = self.encoder.get_sentence_embedding_dimension()
            
            # Create collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )
        else:
            # Initialize encoder if collection already exists
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
    
    def add_question_solution(self, question: str, solution: str, steps: List[str], original_solution: str = None) -> str:
        # Encode the question
        question_vector = self.encoder.encode(question).tolist()
        
        # Generate a unique ID (you might want to use a more sophisticated method)
        import uuid
        point_id = str(uuid.uuid4())
        
        # Create the payload
        payload = {
            "question": question,
            "solution": solution,
            "steps": steps
        }
        
        # Add the original solution text if provided
        if original_solution:
            payload["original_solution"] = original_solution
        
        # Add the point to the collection
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=question_vector,
                    payload=payload
                )
            ]
        )
        
        return point_id
    
    def search_similar_question(self, question: str, threshold: float = 0.8) -> Optional[Dict]:
        # Encode the question
        question_vector = self.encoder.encode(question).tolist()
        
        # Search for similar questions
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=question_vector,
            limit=1
        )
        
        # Check if any results were found and if they are above the threshold
        if search_results and search_results[0].score >= threshold:
            return {
                "id": search_results[0].id,
                "score": search_results[0].score,
                "payload": search_results[0].payload
            }
        return None