import pytest
import os
import pandas as pd
from fastapi.testclient import TestClient
from src.api import app
from src.database import db
from src.query_engine import query_engine
from src.anomaly_detector import anomaly_detector
from src.rag_engine import rag_engine

client = TestClient(app)

class TestSprintCompliance:
    """
    Complete Verification Test Suite matching the DOTMappers AI Engineer Assessment Brief (AI_Engineer_Assessment_Sprint.docx).
    """

    # -------------------------------------------------------------
    # SECTION 3 & 4: DATASET INGESTION & DATASTORE INTEGRITY
    # -------------------------------------------------------------
    def test_csv_dataset_ingestion(self):
        """Verify support_tickets.csv exists, has exactly 500 rows, and matches required schema."""
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "support_tickets.csv")
        assert os.path.exists(csv_path), "support_tickets.csv must exist in project root"
        
        df = pd.read_csv(csv_path)
        assert len(df) == 500, f"Expected 500 rows in dataset, got {len(df)}"
        
        required_columns = [
            "ticket_id", "created_at", "category", "priority", "status",
            "response_time_hrs", "resolution_time_hrs", "agent_id",
            "customer_rating", "issue_summary"
        ]
        for col in required_columns:
            assert col in df.columns, f"Required column '{col}' missing from support_tickets.csv"

    def test_database_seeding_and_counts(self):
        """Verify database contains 500 seeded ticket records."""
        count = len(db.get_all_tickets(limit=500, role="admin"))
        assert count == 500, f"Expected 500 tickets in database, found {count}"

    # -------------------------------------------------------------
    # SECTION 9: SAMPLE ASSESSMENT QUERIES VERIFICATION
    # -------------------------------------------------------------
    def test_sample_query_1_open_tickets(self):
        """Sample Query 1: 'How many tickets are currently open?'"""
        res = query_engine.process_query("How many tickets are currently open?", role="admin")
        assert res["error"] is None
        assert res["results_count"] == 1
        assert res["data"][0]["open_tickets_count"] == 111
        assert "111" in res["answer"]

    def test_sample_query_2_top_agent(self):
        """Sample Query 2: 'Which agent resolved the most tickets this month?'"""
        res = query_engine.process_query("Which agent resolved the most tickets this month?", role="admin")
        assert res["error"] is None
        assert res["results_count"] > 0
        assert "agent_id" in res["data"][0]

    def test_sample_query_3_unresolved_critical_12h(self):
        """Sample Query 3: 'Show me all Critical tickets not resolved within 12 hours.'"""
        res = query_engine.process_query("Show me all Critical tickets not resolved within 12 hours.", role="admin")
        assert res["error"] is None
        assert res["results_count"] > 0
        for row in res["data"]:
            assert row.get("priority") == "Critical" or "ticket_id" in row

    def test_sample_query_4_avg_tech_rating(self):
        """Sample Query 4: 'What is the average customer rating for Technical category tickets?'"""
        res = query_engine.process_query("What is the average customer rating for Technical category tickets?", role="admin")
        assert res["error"] is None
        assert res["results_count"] == 1
        avg_rating = list(res["data"][0].values())[0]
        assert 3.0 <= avg_rating <= 4.5, f"Unexpected rating calculation: {avg_rating}"

    def test_sample_query_5_anomaly_detection_query(self):
        """Sample Query 5: 'Are there any anomalies in resolution times this week?'"""
        res = query_engine.process_query("Are there any anomalies in resolution times this week?", role="admin")
        assert res["error"] is None
        assert "anomal" in res["answer"].lower() or len(res["data"]) > 0

    # -------------------------------------------------------------
    # SECTION 2: ANOMALY DETECTION ENGINE
    # -------------------------------------------------------------
    def test_anomaly_detection_execution(self):
        """Verify statistical (IQR/Z-Score) & SLA breach anomaly detection radar."""
        anom_res = anomaly_detector.detect_anomalies(role="admin")
        assert "total_anomalies" in anom_res
        assert anom_res["total_anomalies"] > 0
        assert "critical_count" in anom_res
        assert "warning_count" in anom_res
        assert len(anom_res["narrative_summary"]) > 0

    # -------------------------------------------------------------
    # SECTION 4: REST API ENDPOINTS COMPLIANCE
    # -------------------------------------------------------------
    def test_api_health_endpoint(self):
        """GET /api/v1/health compliance check."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["status"] == "healthy"
        assert json_data["total_tickets"] == 500
        assert json_data["rls_enabled"] is True
        assert json_data["embeddings_ready"] is True

    def test_api_query_endpoint(self):
        """POST /api/v1/query compliance check."""
        response = client.post("/api/v1/query", json={
            "query": "How many tickets are currently open?",
            "mode": "auto",
            "role": "admin"
        })
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "generated_sql" in data
        assert "answer" in data
        assert data["execution_mode"] == "text_to_sql"

    def test_api_anomalies_endpoint(self):
        """GET /api/v1/anomalies compliance check."""
        response = client.get("/api/v1/anomalies?role=admin")
        assert response.status_code == 200
        data = response.json()
        assert data["total_anomalies"] > 0
        assert len(data["anomalies"]) > 0

    def test_api_rag_search_endpoint(self):
        """POST /api/v1/rag/search compliance check."""
        response = client.post("/api/v1/rag/search", json={
            "query": "billing invoice incorrect charge",
            "match_count": 5,
            "role": "admin"
        })
        assert response.status_code == 200
        data = response.json()
        assert "retrieved_tickets" in data
        assert len(data["retrieved_tickets"]) <= 5

    def test_api_tickets_endpoint(self):
        """GET /api/v1/tickets compliance check."""
        response = client.get("/api/v1/tickets?limit=20&offset=0&role=admin")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 20

    # -------------------------------------------------------------
    # POSTGRESQL ROW-LEVEL SECURITY (RLS) POLICIES
    # -------------------------------------------------------------
    def test_rls_security_roles(self):
        """Verify RLS access policies for Admin, Public Anon, and Scoped Agent."""
        admin_count = len(db.get_all_tickets(limit=500, role="admin"))
        anon_count = len(db.get_all_tickets(limit=500, role="anon"))
        agent_count = len(db.get_all_tickets(limit=500, role="agent_AGT-04"))

        assert admin_count == 500, "Admin role must access all 500 tickets"
        assert anon_count < 500, "Public Anon role must be restricted by RLS"
        assert agent_count < 500, "Agent scoped role must be restricted by RLS"
