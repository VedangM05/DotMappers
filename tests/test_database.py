import pytest
from src.database import db

def test_database_seeding_count():
    """Verify that 500 tickets were seeded into the database."""
    tickets = db.execute_raw_sql("SELECT COUNT(*) AS total FROM tickets;")
    assert len(tickets) == 1
    assert tickets[0]["total"] == 500

def test_rls_anon_role_restriction():
    """Verify RLS simulation: 'anon' role cannot view Escalated tickets."""
    escalated_admin = db.execute_raw_sql("SELECT * FROM tickets WHERE status = 'Escalated';", role="admin")
    escalated_anon = db.execute_raw_sql("SELECT * FROM tickets WHERE status = 'Escalated';", role="anon")
    
    assert len(escalated_admin) > 0, "Escalated tickets exist for admin"
    assert len(escalated_anon) == 0, "Anon role RLS policy must hide Escalated tickets"

def test_vector_search_functionality():
    """Verify deterministic similarity search returns relevant tickets."""
    matches = db.vector_search(query_text="invoice billing charge error", match_count=3)
    assert len(matches) == 3
    assert "similarity" in matches[0]
    assert matches[0]["similarity"] > 0
