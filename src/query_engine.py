import logging
import re
from typing import Dict, Any, List
from src.database import db
from src.llm_provider import llm

logger = logging.getLogger(__name__)

SYSTEM_TEXT_TO_SQL_PROMPT = """You are an expert SQL Data Analyst for a Customer Support Ticket Database.
Translate the user's natural language question into a valid, executable SQL query for the 'tickets' table.

TABLE SCHEMA:
Table: tickets
Columns:
- ticket_id (TEXT): Unique ID (e.g. 'TKT-001')
- created_at (TEXT/DATETIME): Timestamp (e.g. '2024-01-03 09:12')
- category (TEXT): Issue category ('Billing', 'Technical', 'General')
- priority (TEXT): Urgency ('Low', 'Medium', 'High', 'Critical')
- status (TEXT): Status ('Open', 'Resolved', 'Escalated')
- response_time_hrs (REAL): Hours from creation to first agent response
- resolution_time_hrs (REAL): Hours to resolve (NULL if unresolved)
- agent_id (TEXT): Assigned agent ID ('AGT-01' through 'AGT-10')
- customer_rating (REAL): Rating 1.0 to 5.0 (NULL if unresolved)
- issue_summary (TEXT): Free text description

RULES:
1. Generate ONLY the executable SQL query inside ```sql ... ``` block or as plain text. No explanations.
2. MUST use ONLY read-only SELECT or WITH statements.
3. For unresolved tickets, status is 'Open' or 'Escalated' (or status != 'Resolved').
4. Always handle NULL values properly (e.g., WHERE customer_rating IS NOT NULL).
"""

class NLQueryEngine:
    """
    Natural Language Text-to-SQL Query Engine with SQL validation and LLM synthesis.
    """
    def process_query(self, query: str, role: str = "admin") -> Dict[str, Any]:
        """
        1. Translate NL question to SQL.
        2. Validate & execute SQL on database.
        3. Synthesize natural language answer.
        """
        if not query.strip():
            return {
                "query": query,
                "generated_sql": None,
                "results_count": 0,
                "data": [],
                "answer": "Query cannot be empty. Please provide a question.",
                "error": "Empty query",
                "role": role
            }

        # Step 1: Generate SQL via LLM
        llm_raw_response = llm.generate(prompt=query, system_prompt=SYSTEM_TEXT_TO_SQL_PROMPT)
        sql_query = self._clean_sql(llm_raw_response)
        
        # Step 2: Execute SQL against database
        sql_error = None
        raw_results = []
        try:
            raw_results = db.execute_raw_sql(sql_query, role=role)
        except Exception as e:
            sql_error = str(e)
            logger.error(f"SQL execution error on query '{sql_query}': {e}")

        # Step 3: Synthesize Conversational Answer
        if sql_error:
            answer = f"I encountered an error executing the query: {sql_error}"
        elif not raw_results:
            answer = "The query returned no matching records in the database."
        else:
            answer = self._synthesize_answer(query, sql_query, raw_results)

        return {
            "query": query,
            "generated_sql": sql_query,
            "results_count": len(raw_results),
            "data": raw_results[:50],  # Return up to 50 rows in response payload
            "answer": answer,
            "error": sql_error,
            "role": role
        }

    def _clean_sql(self, text: str) -> str:
        """Extract clean SQL string from markdown or LLM output."""
        match = re.search(r"```sql\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if match:
            sql = match.group(1).strip()
        else:
            sql = text.strip()
            
        # Ensure single trailing semicolon removal for string manipulation
        sql = sql.rstrip(";")
        return sql

    def _synthesize_answer(self, user_query: str, sql_query: str, results: List[Dict[str, Any]]) -> str:
        """Return row count summary."""
        return f"Found {len(results)} record{'s' if len(results) != 1 else ''}. See results below."

query_engine = NLQueryEngine()
