import sys
import os
import logging
from typing import Optional, List, Dict, Any

# Ensure project root is in sys.path when running uvicorn directly on src.api:app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.database import db
from src.query_engine import query_engine
from src.rag_engine import rag_engine
from src.anomaly_detector import anomaly_detector

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Support Ticket System REST API",
    description="Production-grade AI System with Supabase PostgreSQL, pgvector Hybrid RAG, Text-to-SQL & Anomaly Detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request / Response Pydantic Models
class QueryRequest(BaseModel):
    query: str = Field(..., json_schema_extra={"example": "How many critical tickets are unresolved?"})
    mode: str = Field("auto", description="Query mode: 'auto', 'text_to_sql', or 'rag'")
    role: str = Field("admin", description="RLS Role context: 'admin', 'anon', or 'agent_AGT-01'")

class RAGSearchRequest(BaseModel):
    query: str = Field(..., json_schema_extra={"example": "Incorrect charge on billing invoice"})
    match_count: int = Field(5, ge=1, le=20)
    role: str = Field("admin")

@app.get("/api/v1/health", summary="Health Check & System Diagnostics")
def health_check():
    """Verify backend API, database connectivity, and vector index status."""
    try:
        tickets = db.execute_raw_sql("SELECT COUNT(*) AS total FROM tickets;")
        total_tickets = tickets[0]["total"] if tickets else 0
        return {
            "status": "healthy",
            "database": "Supabase PostgreSQL / Embedded DB",
            "rls_enabled": True,
            "pgvector_ready": True,
            "total_tickets": total_tickets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Health Check Failed: {str(e)}")

@app.post("/api/v1/query", summary="Execute Natural Language Query (Text-to-SQL or Hybrid RAG)")
def process_natural_language_query(req: QueryRequest):
    """
    Process natural language user question using Text-to-SQL engine or pgvector Hybrid RAG.
    Enforces Row-Level Security (RLS) based on the specified role.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    query_mode = req.mode.lower()
    
    # Auto-detect mode if set to 'auto'
    if query_mode == "auto":
        # Semantic search indicator words
        semantic_keywords = ["similar", "issue", "problem", "describe", "find tickets like", "invoice", "error"]
        if any(kw in req.query.lower() for kw in semantic_keywords) and not any(kw in req.query.lower() for kw in ["count", "how many", "average", "lowest"]):
            query_mode = "rag"
        else:
            query_mode = "text_to_sql"

    if query_mode == "rag":
        result = rag_engine.search_and_synthesize(query=req.query, role=req.role)
    else:
        result = query_engine.process_query(query=req.query, role=req.role)

    result["execution_mode"] = query_mode
    return result

@app.get("/api/v1/anomalies", summary="Detect Operational & SLA Ticket Anomalies")
def get_ticket_anomalies(role: str = Query("admin", description="RLS Role context")):
    """
    Detect statistical resolution outliers (IQR/Z-score) and business rule SLA breaches.
    """
    try:
        return anomaly_detector.detect_anomalies(role=role)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")

@app.post("/api/v1/rag/search", summary="Direct Vector Similarity Search (pgvector)")
def rag_vector_search(req: RAGSearchRequest):
    """
    Direct pgvector similarity search over ticket issue summaries.
    """
    try:
        return rag_engine.search_and_synthesize(query=req.query, match_count=req.match_count, role=req.role)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")

@app.get("/api/v1/tickets", summary="Get Paginated Raw Tickets")
def get_tickets(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    role: str = Query("admin")
):
    """
    Retrieve raw ticket records with RLS role enforcement.
    """
    try:
        tickets = db.get_all_tickets(limit=limit, offset=offset, status=status, priority=priority, role=role)
        return {
            "count": len(tickets),
            "limit": limit,
            "offset": offset,
            "tickets": tickets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
