import sys
import os
import streamlit as st
import pandas as pd
import requests

# Ensure project root is in sys.path when running 'streamlit run src/ui.py' directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Page Config
st.set_page_config(
    page_title="AI Support Ticket System — DOTMappers Assessment",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Custom CSS Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .card-metric {
        background-color: #1E293B;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .card-title {
        font-size: 0.85rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .card-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Direct module imports
from src.database import db
from src.query_engine import query_engine
from src.rag_engine import rag_engine
from src.anomaly_detector import anomaly_detector

# Sidebar RLS & Settings
st.sidebar.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=64)
st.sidebar.title("System Controls")

# Row Level Security Role Selection
rls_role = st.sidebar.selectbox(
    "🔒 Select RLS Security Role",
    options=["admin", "anon", "agent_AGT-04", "agent_AGT-01"],
    format_func=lambda x: {
        "admin": "👑 Admin (Full Access)",
        "anon": "🌐 Public Anon (Restricted)",
        "agent_AGT-04": "👤 Agent AGT-04 (Scoped)",
        "agent_AGT-01": "👤 Agent AGT-01 (Scoped)"
    }.get(x, x),
    help="Demonstrates Supabase PostgreSQL Row Level Security (RLS) policies live."
)

query_mode = st.sidebar.radio(
    "⚡ Query Engine Mode",
    options=["auto", "text_to_sql", "rag"],
    format_func=lambda x: {
        "auto": "✨ Auto-Detect (Recommended)",
        "text_to_sql": "📊 Text-to-SQL Engine",
        "rag": "🔍 pgvector Hybrid RAG"
    }.get(x, x)
)

st.sidebar.divider()
st.sidebar.markdown("### 🛠️ Architecture Tech Stack")
st.sidebar.markdown("""
- **Backend DB:** Supabase PostgreSQL / Embedded Engine
- **Vector Index:** `pgvector` (384-dim embeddings)
- **Security:** PostgreSQL Row Level Security (RLS)
- **LLM Engine:** Groq (Primary) / Gemini (Fallback) / Rule Engine
- **REST API:** FastAPI (OpenAPI / Docs ready)
""")

# Header
st.markdown('<div class="main-header">AI-Powered Support Ticket Analytics System</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">DOTMappers IT Assessment • Active Security Role: <b>{rls_role.upper()}</b></div>', unsafe_allow_html=True)

# Tabs Navigation
tab_query, tab_anomalies, tab_analytics = st.tabs([
    "💬 Natural Language Query & RAG", 
    "🚨 Anomaly Detection Radar", 
    "📊 Dataset Analytics & RLS Test"
])

# ---------------------------------------------------------
# TAB 1: NATURAL LANGUAGE QUERY & RAG
# ---------------------------------------------------------
with tab_query:
    st.subheader("Ask Anything About Support Tickets")
    st.markdown("Try clicking one of the sample assessment questions below:")

    sample_queries = [
        "How many tickets are currently open?",
        "Which agent resolved the most tickets this month?",
        "Show me all Critical tickets not resolved within 12 hours.",
        "What is the average customer rating for Technical category tickets?",
        "Are there any anomalies in resolution times this week?",
        "Find tickets related to invoice charge disputes and billing errors"
    ]

    # Render sample chips
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    selected_sample = None
    for idx, q_text in enumerate(sample_queries):
        if cols[idx % 3].button(f"💡 {q_text}", key=f"btn_{idx}"):
            selected_sample = q_text

    user_query = st.text_input(
        "Enter your query:", 
        value=selected_sample if selected_sample else "", 
        placeholder="e.g. How many critical tickets are unresolved?"
    )

    if st.button("🚀 Execute Query", type="primary") or selected_sample:
        if not user_query:
            st.warning("Please enter a question or click a sample query.")
        else:
            with st.spinner("Processing query via AI Engine..."):
                if query_mode == "rag":
                    res = rag_engine.search_and_synthesize(query=user_query, role=rls_role)
                else:
                    res = query_engine.process_query(query=user_query, role=rls_role)

            st.markdown("### 🤖 AI Summary Answer")
            st.info(res.get("answer", "No answer generated."))

            if "generated_sql" in res and res["generated_sql"]:
                with st.expander("🛠️ Generated SQL Query", expanded=True):
                    st.code(res["generated_sql"], language="sql")

            if "data" in res and res["data"]:
                st.markdown(f"### 📋 Returned Data ({res.get('results_count', len(res['data']))} rows)")
                st.dataframe(pd.DataFrame(res["data"]), use_container_width=True)
            elif "retrieved_tickets" in res and res["retrieved_tickets"]:
                st.markdown(f"### 🔍 Retrieved pgvector Similarity Matches")
                st.dataframe(pd.DataFrame(res["retrieved_tickets"]), use_container_width=True)

# ---------------------------------------------------------
# TAB 2: ANOMALY DETECTION RADAR
# ---------------------------------------------------------
with tab_anomalies:
    st.subheader("Multi-Factor Anomaly & SLA Breach Detection")
    st.markdown("Combines **IQR / Z-Score Statistical Outlier Analysis** with **Business SLA Rules**.")

    if st.button("🔄 Run Anomaly Scan"):
        st.cache_data.clear()

    anom_data = anomaly_detector.detect_anomalies(role=rls_role)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Anomalies Flagged", anom_data["total_anomalies"])
    m2.metric("Critical SLA Breaches", anom_data["critical_count"], delta_color="inverse")
    m3.metric("Warning Anomalies", anom_data["warning_count"])

    st.markdown("### 📝 AI Executive Summary Narrative")
    st.success(anom_data["narrative_summary"])

    st.markdown("### 📑 Flagged Anomaly Details")
    if anom_data["anomalies"]:
        df_anom = pd.DataFrame(anom_data["anomalies"])
        st.dataframe(df_anom, use_container_width=True)
    else:
        st.info("No anomalies detected for current security role.")

# ---------------------------------------------------------
# TAB 3: DATASET ANALYTICS & RLS TEST
# ---------------------------------------------------------
with tab_analytics:
    st.subheader("Support Tickets Overview & Row-Level Security Verification")

    tickets_data = db.get_all_tickets(limit=500, role=rls_role)
    df_tickets = pd.DataFrame(tickets_data)

    c1, c2, c3 = st.columns(3)
    c1.metric("Visible Records (RLS Enforced)", len(df_tickets))
    if not df_tickets.empty and 'status' in df_tickets.columns:
        c2.metric("Resolved Tickets", len(df_tickets[df_tickets['status'] == 'Resolved']))
        c3.metric("Escalated Tickets (Hidden in Public Anon)", len(df_tickets[df_tickets['status'] == 'Escalated']))

    st.markdown("### 📈 Visual Distributions")
    col_chart1, col_chart2 = st.columns(2)
    
    if not df_tickets.empty:
        with col_chart1:
            st.markdown("**Status Breakdown**")
            st.bar_chart(df_tickets['status'].value_counts())
            
        with col_chart2:
            st.markdown("**Priority Breakdown**")
            st.bar_chart(df_tickets['priority'].value_counts())

    st.markdown("### 🗄️ Raw Ticket Database View")
    st.dataframe(df_tickets, use_container_width=True)
