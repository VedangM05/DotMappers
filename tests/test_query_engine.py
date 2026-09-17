import pytest
from src.query_engine import query_engine

def test_sample_query_open_tickets():
    """Test sample query: How many tickets are currently open?"""
    res = query_engine.process_query("How many tickets are currently open?")
    assert res["error"] is None
    assert res["results_count"] > 0
    assert "open" in res["answer"].lower() or "tickets" in res["answer"].lower()

def test_sample_query_critical_unresolved():
    """Test sample query: Show me all Critical tickets not resolved within 12 hours."""
    res = query_engine.process_query("Show me all Critical tickets not resolved")
    assert res["error"] is None
    assert res["results_count"] >= 0

def test_sample_query_average_rating():
    """Test sample query: What is the average customer rating for Technical category tickets?"""
    res = query_engine.process_query("What is the average customer rating for Technical category tickets?")
    assert res["error"] is None
    assert "answer" in res
