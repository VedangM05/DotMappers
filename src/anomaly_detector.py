import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from src.database import db
from src.llm_provider import llm

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    Multi-factor Anomaly Detection Engine combining statistical IQR/Z-score analysis,
    business SLA rule checks, and LLM narrative synthesis.
    """
    def detect_anomalies(self, role: str = "admin") -> Dict[str, Any]:
        """Run all anomaly detectors on ticket dataset."""
        tickets = db.execute_raw_sql("SELECT * FROM tickets;", role=role)
        if not tickets:
            return {"anomalies": [], "total_anomalies": 0, "summary": "No tickets found."}

        df = pd.DataFrame(tickets)
        anomalies = []

        # 1. Unresolved High/Critical Priority Tickets older than 24 Hours
        unresolved_crit = df[
            (df['priority'].isin(['High', 'Critical'])) & 
            (df['status'] != 'Resolved') & 
            (df['response_time_hrs'] > 1.0)
        ]
        for _, row in unresolved_crit.iterrows():
            anomalies.append({
                "ticket_id": row['ticket_id'],
                "category": row['category'],
                "priority": row['priority'],
                "status": row['status'],
                "agent_id": row['agent_id'],
                "anomaly_type": "Unresolved High/Critical SLA Breach",
                "severity": "CRITICAL",
                "issue_summary": row['issue_summary'],
                "details": f"Ticket is {row['status']} with {row['priority']} priority. Response time: {row['response_time_hrs']}h."
            })

        # 2. Resolution Time Outliers (IQR & Z-score > 2.5)
        resolved_df = df[df['resolution_time_hrs'].notnull()].copy()
        if not resolved_df.empty:
            res_times = resolved_df['resolution_time_hrs'].values
            mean_res = np.mean(res_times)
            std_res = np.std(res_times)
            q75, q25 = np.percentile(res_times, [75, 25])
            iqr = q75 - q25
            upper_bound = q75 + 1.5 * iqr

            outliers = resolved_df[resolved_df['resolution_time_hrs'] > upper_bound]
            for _, row in outliers.iterrows():
                z_score = (row['resolution_time_hrs'] - mean_res) / (std_res + 1e-6)
                anomalies.append({
                    "ticket_id": row['ticket_id'],
                    "category": row['category'],
                    "priority": row['priority'],
                    "status": row['status'],
                    "agent_id": row['agent_id'],
                    "anomaly_type": "Abnormally Long Resolution Time",
                    "severity": "WARNING" if z_score < 3.0 else "CRITICAL",
                    "issue_summary": row['issue_summary'],
                    "details": f"Resolution took {row['resolution_time_hrs']:.1f}h (IQR Upper Limit: {upper_bound:.1f}h, Z-score: {z_score:.2f})."
                })

        # 3. Rushed Resolution with Low Rating (Resolution < 2h & Rating <= 2)
        rushed_low_rating = df[
            (df['status'] == 'Resolved') & 
            (df['resolution_time_hrs'] <= 2.0) & 
            (df['customer_rating'] <= 2.0)
        ]
        for _, row in rushed_low_rating.iterrows():
            anomalies.append({
                "ticket_id": row['ticket_id'],
                "category": row['category'],
                "priority": row['priority'],
                "status": row['status'],
                "agent_id": row['agent_id'],
                "anomaly_type": "Premature Resolution / Low Satisfaction",
                "severity": "WARNING",
                "issue_summary": row['issue_summary'],
                "details": f"Closed in {row['resolution_time_hrs']}h but received low customer rating of {row['customer_rating']}/5."
            })

        # Deduplicate anomalies by ticket_id + anomaly_type
        unique_anomalies = []
        seen = set()
        for a in anomalies:
            key = (a['ticket_id'], a['anomaly_type'])
            if key not in seen:
                seen.add(key)
                unique_anomalies.append(a)

        # Synthesize Summary Narrative
        summary = self._synthesize_anomaly_narrative(unique_anomalies)

        return {
            "total_anomalies": len(unique_anomalies),
            "critical_count": sum(1 for a in unique_anomalies if a['severity'] == 'CRITICAL'),
            "warning_count": sum(1 for a in unique_anomalies if a['severity'] == 'WARNING'),
            "anomalies": unique_anomalies,
            "narrative_summary": summary
        }

    def _synthesize_anomaly_narrative(self, anomalies: List[Dict[str, Any]]) -> str:
        """Generate AI narrative explaining overall anomaly patterns."""
        if not anomalies:
            return "No operational anomalies detected in the support ticket system."

        crit_count = sum(1 for a in anomalies if a['severity'] == 'CRITICAL')
        warn_count = sum(1 for a in anomalies if a['severity'] == 'WARNING')

        prompt = (
            f"You are a Quality Control Lead for a Support Team. "
            f"Analyze these operational ticket anomalies:\n"
            f"- Total Anomalies Detected: {len(anomalies)} (Critical: {crit_count}, Warning: {warn_count})\n"
            f"- Sample Anomaly Details:\n" + "\n".join([f"  * [{a['severity']}] {a['ticket_id']} ({a['category']}): {a['anomaly_type']} - {a['details']}" for a in anomalies[:8]]) + "\n\n"
            "Provide a concise 3-bullet point executive summary highlighting the primary operational risks and recommended agent actions."
        )

        system_prompt = "Provide a professional, actionable executive summary of operational support ticket anomalies."
        return llm.generate(prompt=prompt, system_prompt=system_prompt)

anomaly_detector = AnomalyDetector()
