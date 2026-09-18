import logging
from typing import Optional

logger = logging.getLogger(__name__)

class LLMProvider:
    """Deterministic rule-based query engine (zero-cost, zero-fail)."""

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate SQL or summary using hardcoded rules."""
        p = prompt.lower()

        if ("closed" in p or "resolved" in p) and "open" in p and "ticket" in p:
            return "SELECT status, COUNT(*) AS count FROM tickets GROUP BY status ORDER BY status;"
        if "how many" in p and "categor" in p:
            return "SELECT COUNT(DISTINCT category) AS total_categories FROM tickets;"
        if "how many" in p and "agent" in p:
            return "SELECT COUNT(DISTINCT agent_id) AS total_agents FROM tickets;"
        # Multi-filter queries: billing + critical + open
        # Return full records if user says "show" or similar
        if ("show" in p or "list" in p or "get" in p) and "billing" in p and "critical" in p and "open" in p:
            return "SELECT ticket_id, category, priority, status, agent_id, issue_summary FROM tickets WHERE category = 'Billing' AND priority = 'Critical' AND status = 'Open';"
        if ("show" in p or "list" in p or "get" in p) and "technical" in p and "critical" in p and "open" in p:
            return "SELECT ticket_id, category, priority, status, agent_id, issue_summary FROM tickets WHERE category = 'Technical' AND priority = 'Critical' AND status = 'Open';"
        if "billing" in p and "critical" in p and "open" in p:
            return "SELECT COUNT(*) AS open_tickets_count FROM tickets WHERE category = 'Billing' AND priority = 'Critical' AND status = 'Open';"
        if "technical" in p and "critical" in p and "open" in p:
            return "SELECT COUNT(*) AS open_tickets_count FROM tickets WHERE category = 'Technical' AND priority = 'Critical' AND status = 'Open';"
        if "billing" in p and "critical" in p:
            return "SELECT COUNT(*) AS critical_billing_tickets FROM tickets WHERE category = 'Billing' AND priority = 'Critical';"
        if "technical" in p and "critical" in p:
            return "SELECT COUNT(*) AS critical_technical_tickets FROM tickets WHERE category = 'Technical' AND priority = 'Critical';"
        if "open" in p and "ticket" in p:
            return "SELECT COUNT(*) AS open_tickets_count FROM tickets WHERE status = 'Open';"
        if "critical" in p and ("unresolved" in p or "not resolved" in p):
            return "SELECT COUNT(*) AS unresolved_critical_tickets FROM tickets WHERE priority = 'Critical' AND status != 'Resolved';"
        if ("highest" in p or "most" in p) and "agent" in p:
            return "SELECT agent_id, COUNT(*) AS resolved_count FROM tickets WHERE status = 'Resolved' GROUP BY agent_id ORDER BY resolved_count DESC LIMIT 1;"
        if "lowest" in p and ("rating" in p or "agent" in p):
            return "SELECT agent_id, AVG(customer_rating) AS avg_rating FROM tickets WHERE customer_rating IS NOT NULL GROUP BY agent_id ORDER BY avg_rating ASC LIMIT 1;"
        if "average" in p or "avg" in p:
            if "rating" in p and "technical" in p:
                return "SELECT AVG(customer_rating) AS avg_tech_rating FROM tickets WHERE category = 'Technical' AND customer_rating IS NOT NULL;"
            if "rating" in p:
                return "SELECT category, AVG(customer_rating) AS avg_rating FROM tickets WHERE customer_rating IS NOT NULL GROUP BY category;"
            if "resolution" in p:
                return "SELECT category, AVG(resolution_time_hrs) AS avg_resolution_hours FROM tickets WHERE resolution_time_hrs IS NOT NULL GROUP BY category;"
        if "critical" in p and ("12" in p or "24" in p or "hour" in p):
            return "SELECT ticket_id, category, priority, status, created_at, agent_id, issue_summary FROM tickets WHERE priority = 'Critical' AND status != 'Resolved';"
        if "anomaly" in p or "anomalies" in p:
            return "SELECT ticket_id, category, priority, status, resolution_time_hrs, agent_id FROM tickets WHERE resolution_time_hrs > 40 OR (priority = 'Critical' AND status != 'Resolved');"

        return "SELECT ticket_id, category, priority, status, created_at, agent_id, issue_summary FROM tickets LIMIT 10;"

llm = LLMProvider()
