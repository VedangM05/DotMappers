import os
import sqlite3
import logging
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from src.config import CSV_FILE_PATH, SQLITE_DB_PATH
from src.embeddings import generate_batch_embeddings, generate_embedding, cosine_similarity

logger = logging.getLogger(__name__)

class DatabaseManager:
    """SQLite Database Manager with deterministic embeddings and RLS emulation."""
    def __init__(self):
        self.db_path = SQLITE_DB_PATH
        self.init_database()

    def init_database(self):
        """Initialize database schema and seed data from support_tickets.csv."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create local SQLite tickets table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            response_time_hrs REAL NOT NULL,
            resolution_time_hrs REAL NULL,
            agent_id TEXT NOT NULL,
            customer_rating REAL NULL,
            issue_summary TEXT NOT NULL,
            issue_embedding_json TEXT NULL
        );
        """)

        # Check existing row count
        cursor.execute("SELECT COUNT(*) FROM tickets;")
        count = cursor.fetchone()[0]

        if count < 500:
            logger.info("Seeding database from support_tickets.csv...")
            cursor.execute("DELETE FROM tickets;")  # Clear incomplete records
            
            df = pd.read_csv(CSV_FILE_PATH)
            
            # Generate embeddings for issue summaries
            summaries = df['issue_summary'].tolist()
            embeddings = generate_batch_embeddings(summaries)
            
            records = []
            for idx, row in df.iterrows():
                resol_time = None if pd.isna(row['resolution_time_hrs']) else float(row['resolution_time_hrs'])
                cust_rating = None if pd.isna(row['customer_rating']) else float(row['customer_rating'])
                emb_json = json.dumps(embeddings[idx])
                
                records.append((
                    str(row['ticket_id']),
                    str(row['created_at']),
                    str(row['category']),
                    str(row['priority']),
                    str(row['status']),
                    float(row['response_time_hrs']),
                    resol_time,
                    str(row['agent_id']),
                    cust_rating,
                    str(row['issue_summary']),
                    emb_json
                ))
            
            cursor.executemany("""
            INSERT OR REPLACE INTO tickets (
                ticket_id, created_at, category, priority, status, 
                response_time_hrs, resolution_time_hrs, agent_id, customer_rating, 
                issue_summary, issue_embedding_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, records)
            conn.commit()
            logger.info(f"Successfully seeded {len(records)} ticket records with vector embeddings.")
            
        conn.close()

    def get_connection(self):
        """Get a fresh SQLite connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_raw_sql(self, sql_query: str, role: str = "admin") -> List[Dict[str, Any]]:
        """
        Execute raw SQL query safely with RLS role simulation.
        Roles: 'admin' (all records), 'agent' (scoped), 'anon' (no escalated tickets).
        """
        # Clean query
        query_upper = sql_query.strip().upper()
        if not query_upper.startswith("SELECT") and not query_upper.startswith("WITH"):
            raise ValueError("Only read-only SELECT queries are allowed for security.")

        conn = self.get_connection()
        cursor = conn.cursor()

        # Apply RLS Security Filter Simulation if needed
        final_query = sql_query
        params = []
        if role == "anon":
            # Public Anon RLS Policy: Cannot view Escalated tickets
            if "WHERE" in final_query.upper():
                final_query = final_query.replace("WHERE", "WHERE status != 'Escalated' AND ", 1)
            else:
                final_query += " WHERE status != 'Escalated'"
        elif role.startswith("agent_"):
            agent_id = role.replace("agent_", "")
            # Validate agent_id format (alphanumeric only)
            if not agent_id.replace("-", "").isalnum():
                raise ValueError("Invalid agent_id format")
            if "WHERE" in final_query.upper():
                final_query = final_query.replace("WHERE", "WHERE agent_id = ? AND ", 1)
                params = [agent_id] + params
            else:
                final_query += " WHERE agent_id = ?"
                params = [agent_id]

        try:
            if params:
                cursor.execute(final_query, params)
            else:
                cursor.execute(final_query)
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
            # Strip embedding column from API outputs to keep responses lean
            for r in result:
                r.pop("issue_embedding_json", None)
            return result
        finally:
            conn.close()

    def vector_search(self, query_text: str, match_count: int = 5, role: str = "admin") -> List[Dict[str, Any]]:
        """
        Perform deterministic cosine similarity search against ticket issue summaries.
        Returns top matching tickets with similarity score.
        """
        query_emb = generate_embedding(query_text)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        sql = "SELECT ticket_id, created_at, category, priority, status, response_time_hrs, resolution_time_hrs, agent_id, customer_rating, issue_summary, issue_embedding_json FROM tickets"
        if role == "anon":
            sql += " WHERE status != 'Escalated'"
            
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        scored_tickets = []
        for row in rows:
            r_dict = dict(row)
            emb_json = r_dict.pop("issue_embedding_json", None)
            if emb_json:
                doc_emb = json.loads(emb_json)
                sim = cosine_similarity(query_emb, doc_emb)
                r_dict["similarity"] = round(sim, 4)
                scored_tickets.append(r_dict)
                
        # Sort by similarity descending
        scored_tickets.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_tickets[:match_count]

    def get_all_tickets(self, limit: int = 100, offset: int = 0, status: Optional[str] = None, priority: Optional[str] = None, role: str = "admin") -> List[Dict[str, Any]]:
        """Retrieve paginated tickets with optional filtering."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        where_clauses = []
        params = []
        
        if role == "anon":
            where_clauses.append("status != 'Escalated'")
        elif role.startswith("agent_"):
            agent_id = role.split("_", 1)[1]
            where_clauses.append("agent_id = ?")
            params.append(agent_id)
        if status:
            where_clauses.append("status = ?")
            params.append(status)
        if priority:
            where_clauses.append("priority = ?")
            params.append(priority)
            
        where_str = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        
        sql = f"SELECT ticket_id, created_at, category, priority, status, response_time_hrs, resolution_time_hrs, agent_id, customer_rating, issue_summary FROM tickets {where_str} ORDER BY ticket_id LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

# Global DB Singleton
db = DatabaseManager()
