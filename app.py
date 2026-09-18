import streamlit as st
import requests
import json
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="DOTMappers - AI Support Ticket Analytics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styles
st.markdown("""
<style>
    /* Custom theme colors */
    :root {
        --primary: #4F46E5;
        --secondary: #06B6D4;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --dark-bg: #0F172A;
        --dark-card: #1E293B;
        --dark-text: #F8FAFC;
        --dark-text-secondary: #94A3B8;
        --dark-border: #334155;
        --light-bg: #F8FAFC;
        --light-card: #FFFFFF;
        --light-text: #0F172A;
        --light-text-secondary: #64748B;
        --light-border: #E2E8F0;
    }

    .metric-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid var(--dark-border);
        text-align: left;
    }

    .stat-value {
        font-size: 2rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }

    .stat-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--dark-text-secondary);
    }

    .tab-content {
        padding: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API Base
API_BASE = 'http://localhost:8000'

# Initialize session state
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'dashboard'
if 'rls_role' not in st.session_state:
    st.session_state.rls_role = 'admin'
if 'query_mode' not in st.session_state:
    st.session_state.query_mode = 'auto'
if 'user_query' not in st.session_state:
    st.session_state.user_query = ''
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'query_result' not in st.session_state:
    st.session_state.query_result = None
if 'query_execution_time' not in st.session_state:
    st.session_state.query_execution_time = None
if 'dashboard_stats' not in st.session_state:
    st.session_state.dashboard_stats = None
if 'anomalies_data' not in st.session_state:
    st.session_state.anomalies_data = None
if 'tickets_data' not in st.session_state:
    st.session_state.tickets_data = []

# Sidebar
with st.sidebar:
    # Logo and Theme Toggle
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 🤖 DOTMappers")
        st.caption("AI Analytics")

    st.divider()

    # Query Mode
    st.markdown("**✨ Query Mode**")
    st.session_state.query_mode = st.radio(
        "Select query mode:",
        options=['auto', 'text_to_sql', 'rag'],
        format_func=lambda x: {
            'auto': '✨ Auto-Detect',
            'text_to_sql': '📊 Text-to-SQL',
            'rag': '🔍 Vector RAG'
        }[x],
        label_visibility="collapsed"
    )

    # RLS Role
    st.markdown("**👤 RLS Role**")
    st.session_state.rls_role = st.selectbox(
        "Select role:",
        options=['admin', 'anon', 'agent_AGT-01'],
        label_visibility="collapsed"
    )

    st.divider()

    # Query History
    if st.session_state.query_history:
        st.markdown(f"**📋 History ({len(st.session_state.query_history)})**")
        for i, item in enumerate(st.session_state.query_history):
            if st.button(item['query'][:50] + '...' if len(item['query']) > 50 else item['query'], key=f"hist_{i}"):
                st.session_state.user_query = item['query']
                st.rerun()

# Main Content
st.markdown("## AI Support Ticket Analytics")
st.caption(f"DOTMappers Assessment • Role: **{st.session_state.rls_role.upper()}**")

# Fetch dashboard stats on load
if st.session_state.dashboard_stats is None:
    try:
        response = requests.get(f'{API_BASE}/api/v1/health', timeout=5)
        st.session_state.dashboard_stats = response.json()
    except Exception as e:
        st.error(f"Failed to connect to backend: {str(e)}")

# Tab Navigation (Radio buttons for programmatic control)
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.active_tab = 'dashboard'
        st.rerun()
with col2:
    if st.button("💬 Query", use_container_width=True):
        st.session_state.active_tab = 'query'
        st.rerun()
with col3:
    if st.button("🚨 Anomalies", use_container_width=True):
        st.session_state.active_tab = 'anomalies'
        st.rerun()
with col4:
    if st.button("📈 Analytics", use_container_width=True):
        st.session_state.active_tab = 'analytics'
        st.rerun()

st.divider()

# ==================== DASHBOARD TAB ====================
if st.session_state.active_tab == 'dashboard':
    # Stats
    cols = st.columns(3)

    with cols[0]:
        st.metric(
            "Total Tickets",
            st.session_state.dashboard_stats.get('total_tickets', 0) if st.session_state.dashboard_stats else 0
        )

    with cols[1]:
        st.metric(
            "Queries",
            len(st.session_state.query_history)
        )

    with cols[2]:
        if st.session_state.query_execution_time:
            st.metric(
                "Response Time",
                f"{st.session_state.query_execution_time}ms"
            )
        else:
            st.metric("Response Time", "N/A")

    st.divider()

    # Quick Start Queries
    st.markdown("### 🚀 Quick Start")
    st.markdown("Select a sample query to get started with the AI-powered analytics system.")

    sample_queries = [
        "How many tickets are currently open?",
        "Which agent resolved the most tickets this month?",
        "Show me all Critical tickets not resolved within 12 hours.",
        "What is the average customer rating for Technical category tickets?",
        "Are there any anomalies in resolution times this week?",
        "Find tickets related to invoice charge disputes and billing errors"
    ]

    cols = st.columns(2)
    for i, query in enumerate(sample_queries):
        with cols[i % 2]:
            if st.button(query, key=f"sample_{i}", use_container_width=True):
                st.session_state.user_query = query
                st.session_state.active_tab = 'query'
                st.rerun()

    st.divider()

# ==================== QUERY TAB ====================
if st.session_state.active_tab == 'query':
    # Query Input
    col1, col2 = st.columns([4, 1])

    with col1:
        user_query = st.text_input(
            "Query:",
            value=st.session_state.user_query,
            placeholder="Ask anything about tickets...",
            label_visibility="collapsed"
        )
        st.session_state.user_query = user_query

    with col2:
        execute_button = st.button("⚡ Execute", use_container_width=True)

    # Execute Query
    if execute_button and user_query.strip():
        start_time = time.time()
        try:
            endpoint = f'{API_BASE}/api/v1/rag/search' if st.session_state.query_mode == 'rag' else f'{API_BASE}/api/v1/query'

            if st.session_state.query_mode == 'rag':
                body = {
                    'query': user_query,
                    'match_count': 5,
                    'role': st.session_state.rls_role
                }
            else:
                body = {
                    'query': user_query,
                    'mode': st.session_state.query_mode,
                    'role': st.session_state.rls_role
                }

            with st.spinner("Processing..."):
                response = requests.post(endpoint, json=body, timeout=30)
                response.raise_for_status()
                data = response.json()

            # Normalize response
            if 'retrieved_tickets' in data and 'data' not in data:
                data['data'] = data['retrieved_tickets']

            st.session_state.query_result = data
            st.session_state.query_execution_time = int((time.time() - start_time) * 1000)

            # Add to history
            if 'error' not in data:
                st.session_state.query_history.insert(0, {
                    'query': user_query,
                    'time': datetime.now(),
                    'mode': st.session_state.query_mode
                })
                st.session_state.query_history = st.session_state.query_history[:10]

        except Exception as e:
            st.session_state.query_result = {'error': f'API Error: {str(e)}'}

    # Display Results
    if st.session_state.query_result:
        result = st.session_state.query_result

        if 'error' in result and result['error']:
            st.error(f"❌ {result['error']}")
        else:
            if st.session_state.query_execution_time:
                st.success(f"✓ Completed in {st.session_state.query_execution_time}ms")

            if 'answer' in result and result['answer']:
                st.info(result['answer'])

            if result.get('data') and len(result.get('data', [])) > 0:
                st.markdown(f"**Results** ({len(result['data'])} records)")

                # Display table
                st.dataframe(
                    result['data'],
                    use_container_width=True,
                    height=400,
                    hide_index=True
                )

                # Download and SQL buttons
                col1, col2 = st.columns(2)

                with col1:
                    json_str = json.dumps(result['data'], indent=2)
                    st.download_button(
                        "📥 Download JSON",
                        json_str,
                        "query_results.json",
                        "application/json"
                    )

                if 'generated_sql' in result:
                    with col2:
                        if st.button("📋 Show SQL"):
                            st.code(result['generated_sql'], language='sql')

# ==================== ANOMALIES TAB ====================
if st.session_state.active_tab == 'anomalies':
    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown("### 🚨 Anomaly Detection")

    with col2:
        if st.button("🔄 Scan", use_container_width=True):
            with st.spinner("Scanning for anomalies..."):
                try:
                    response = requests.get(
                        f'{API_BASE}/api/v1/anomalies',
                        params={'role': st.session_state.rls_role},
                        timeout=30
                    )
                    st.session_state.anomalies_data = response.json()
                except Exception as e:
                    st.error(f"Failed to fetch anomalies: {str(e)}")

    if st.session_state.anomalies_data:
        data = st.session_state.anomalies_data

        # Anomaly Stats
        cols = st.columns(3)

        with cols[0]:
            st.metric("Total", data.get('total_anomalies', 0))

        with cols[1]:
            st.metric("🔴 Critical", data.get('critical_count', 0))

        with cols[2]:
            st.metric("🟡 Warning", data.get('warning_count', 0))

        st.divider()

        # Summary
        if 'narrative_summary' in data:
            st.info(data['narrative_summary'])

        # Anomalies Table
        if 'anomalies' in data and data['anomalies']:
            st.markdown(f"**Flagged Records** ({len(data['anomalies'])} total)")

            anomaly_df_data = []
            for a in data['anomalies']:
                anomaly_df_data.append({
                    'Ticket ID': a['ticket_id'],
                    'Type': a['anomaly_type'][:40],
                    'Severity': a['severity'],
                    'Details': a['details']
                })

            st.dataframe(
                anomaly_df_data,
                use_container_width=True,
                height=400,
                hide_index=True
            )

# ==================== ANALYTICS TAB ====================
if st.session_state.active_tab == 'analytics':
    st.markdown("### 📈 Dataset Analytics")

    # Fetch tickets on first load
    if not st.session_state.tickets_data:
        with st.spinner("Loading tickets..."):
            try:
                response = requests.get(
                    f'{API_BASE}/api/v1/tickets',
                    params={'limit': 500, 'role': st.session_state.rls_role},
                    timeout=30
                )
                st.session_state.tickets_data = response.json().get('tickets', [])
            except Exception as e:
                st.error(f"Failed to fetch tickets: {str(e)}")

    # Filters
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        search_term = st.text_input("🔍 Search", "")

    with col2:
        filter_category = st.selectbox(
            "Category",
            options=[''] + list(set([t.get('category', '') for t in st.session_state.tickets_data if t.get('category')]))
        )

    with col3:
        filter_priority = st.selectbox(
            "Priority",
            options=['', 'Low', 'Medium', 'High', 'Critical']
        )

    with col4:
        filter_status = st.selectbox(
            "Status",
            options=['', 'Open', 'Resolved', 'Escalated']
        )

    with col5:
        agents = list(set([t.get('agent_id', '') for t in st.session_state.tickets_data if t.get('agent_id')]))
        filter_agent = st.selectbox(
            "Agent",
            options=[''] + agents
        )

    # Filter tickets
    filtered = st.session_state.tickets_data

    if search_term:
        search_lower = search_term.lower()
        filtered = [
            t for t in filtered
            if (search_lower in str(t.get('ticket_id', '')).lower() or
                search_lower in str(t.get('category', '')).lower() or
                search_lower in str(t.get('issue_summary', '')).lower() or
                search_lower in str(t.get('agent_id', '')).lower())
        ]

    if filter_category:
        filtered = [t for t in filtered if t.get('category') == filter_category]

    if filter_priority:
        filtered = [t for t in filtered if t.get('priority') == filter_priority]

    if filter_status:
        filtered = [t for t in filtered if t.get('status') == filter_status]

    if filter_agent:
        filtered = [t for t in filtered if t.get('agent_id') == filter_agent]

    st.divider()

    # Stats
    cols = st.columns(3)

    with cols[0]:
        st.metric("Visible", len(filtered))

    with cols[1]:
        resolved = len([t for t in filtered if t.get('status') == 'Resolved'])
        st.metric("Resolved", resolved)

    with cols[2]:
        open_tickets = len([t for t in filtered if t.get('status') != 'Resolved'])
        st.metric("Open", open_tickets)

    st.divider()

    # Table
    st.markdown(f"**Tickets** ({len(filtered)} total)")

    if filtered:
        display_data = []
        for t in filtered:
            display_data.append({
                'Ticket ID': t.get('ticket_id', ''),
                'Category': t.get('category', ''),
                'Priority': t.get('priority', ''),
                'Status': t.get('status', ''),
                'Agent': t.get('agent_id', ''),
                'Rating': f"⭐ {t.get('customer_rating', '')}" if t.get('customer_rating') else '—'
            })

        st.dataframe(
            display_data,
            use_container_width=True,
            height=500,
            hide_index=True
        )
    else:
        st.info("No tickets match the selected filters.")
