import logging
from typing import Dict, Any, List
from src.database import db
from src.llm_provider import llm

logger = logging.getLogger(__name__)

class RAGEngine:
    """
    Hybrid Vector RAG Engine utilizing pgvector / cosine similarity over ticket embeddings.
    """
    def search_and_synthesize(self, query: str, match_count: int = 5, role: str = "admin") -> Dict[str, Any]:
        """
        1. Retrieve top matching tickets using pgvector cosine similarity.
        2. Synthesize context-aware answer using LLM.
        """
        # Vector Similarity Search
        matched_tickets = db.vector_search(query_text=query, match_count=match_count, role=role)
        
        if not matched_tickets:
            return {
                "query": query,
                "retrieved_tickets": [],
                "answer": "No matching tickets found in the vector database for your query.",
                "match_count": 0
            }
            
        # Format RAG Context
        context_str = "\n".join([
            f"- Ticket {t['ticket_id']} [{t['category']} | {t['priority']} | {t['status']}]: {t['issue_summary']} (Rating: {t.get('customer_rating') or 'N/A'}, ResTime: {t.get('resolution_time_hrs') or 'Unresolved'}h, Sim: {t['similarity']})"
            for t in matched_tickets
        ])
        
        system_prompt = (
            "You are an AI Support Ticket Analyst assistant. "
            "Below are the most relevant customer support tickets retrieved from the vector database using pgvector similarity search. "
            "Use ONLY these tickets to answer the user's question clearly, professionally, and concisely."
        )
        
        user_prompt = f"User Question: {query}\n\nRetrieved Tickets Context:\n{context_str}\n\nAnswer:"
        
        synthesized_answer = llm.generate(prompt=user_prompt, system_prompt=system_prompt)
        
        return {
            "query": query,
            "retrieved_tickets": matched_tickets,
            "answer": synthesized_answer,
            "match_count": len(matched_tickets)
        }

rag_engine = RAGEngine()
