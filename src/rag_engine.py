import logging
from typing import Dict, Any
from src.database import db

logger = logging.getLogger(__name__)

class RAGEngine:
    """Hybrid Vector RAG Engine utilizing deterministic embeddings and cosine similarity."""

    def search_and_synthesize(self, query: str, match_count: int = 5, role: str = "admin") -> Dict[str, Any]:
        """Retrieve top matching tickets using deterministic cosine similarity."""
        matched_tickets = db.vector_search(query_text=query, match_count=match_count, role=role)

        if not matched_tickets:
            return {
                "query": query,
                "retrieved_tickets": [],
                "answer": "No matching tickets found in the vector database for your query.",
                "match_count": 0
            }

        return {
            "query": query,
            "retrieved_tickets": matched_tickets,
            "answer": f"Found {len(matched_tickets)} matching ticket(s) via vector similarity search.",
            "match_count": len(matched_tickets)
        }

rag_engine = RAGEngine()
