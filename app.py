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
if 'show_sql' not in st.session_state:
    st.session_state.show_sql = False
if 'auto_execute' not in st.session_state:
    st.session_state.auto_execute = False
if 'results_page' not in st.session_state:
    st.session_state.results_page = 0
if 'anomalies_page' not in st.session_state:
    st.session_state.anomalies_page = 0
if 'analytics_page' not in st.session_state:
    st.session_state.analytics_page = 0

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
st.caption("DOTMappers Assessment")

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
    st.markdown("### Dashboard Overview")

    # Stats Cards
    cols = st.columns(3)

    with cols[0]:
        with st.container(border=True):
            st.metric(
                "📊 Total Tickets",
                st.session_state.dashboard_stats.get('total_tickets', 0) if st.session_state.dashboard_stats else 0
            )

    with cols[1]:
        with st.container(border=True):
            st.metric(
                "💬 Queries Executed",
                len(st.session_state.query_history)
            )

    with cols[2]:
        with st.container(border=True):
            if st.session_state.query_execution_time:
                st.metric(
                    "⚡ Response Time",
                    f"{st.session_state.query_execution_time}ms"
                )
            else:
                st.metric("⚡ Response Time", "—")

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
                st.session_state.auto_execute = True
                st.rerun()

    st.divider()

# ==================== QUERY TAB ====================
if st.session_state.active_tab == 'query':
    st.markdown("### Natural Language Query")

    # Query Input with Form (Enter to submit)
    with st.form("query_form", clear_on_submit=False):
        user_query = st.text_input(
            "Ask anything about your support tickets...",
            value=st.session_state.user_query,
            placeholder="E.g., How many tickets are open?",
            label_visibility="collapsed"
        )
        execute_button = st.form_submit_button("⚡ Execute", use_container_width=True)

    st.session_state.user_query = user_query

    # Execute Query
    should_execute = execute_button or (st.session_state.auto_execute and user_query.strip())

    if should_execute and user_query.strip():
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
            st.session_state.auto_execute = False
            st.session_state.results_page = 0
            st.session_state.show_sql = False

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
            st.session_state.auto_execute = False

    # Display Results
    if st.session_state.query_result:
        result = st.session_state.query_result

        with st.container(border=True):
            if 'error' in result and result['error']:
                st.error(f"❌ {result['error']}")
            else:
                # Execution time
                if st.session_state.query_execution_time:
                    st.markdown(f"<div style='color: #10B981; font-weight: 600; font-size: 0.9rem; margin-bottom: 1rem;'>✓ Completed in {st.session_state.query_execution_time}ms</div>", unsafe_allow_html=True)

                # Answer/Summary
                if 'answer' in result and result['answer']:
                    st.markdown(f"<div style='padding: 0.75rem; background-color: #1E293B; border-radius: 0.3rem; margin-bottom: 1.5rem; font-size: 0.9rem; color: #94A3B8;'>{result['answer']}</div>", unsafe_allow_html=True)

                # Results section
                if result.get('data') and len(result.get('data', [])) > 0:
                    # Show SQL at top if requested
                    if st.session_state.get('show_sql') and 'generated_sql' in result:
                        col1, col2 = st.columns([5, 1])
                        with col1:
                            st.markdown("<div style='font-weight: 600; color: #F8FAFC; margin-bottom: 0.5rem;'>📋 Generated SQL</div>", unsafe_allow_html=True)
                        with col2:
                            if st.button("📋 Copy", key="copy_sql", help="Copy SQL to clipboard"):
                                st.write(f"<script>navigator.clipboard.writeText(`{result['generated_sql']}`)</script>", unsafe_allow_html=True)
                                st.success("Copied!", icon="✓")

                        st.code(result['generated_sql'], language='sql')
                        st.markdown("---")

                    # Header with buttons
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"<div style='font-weight: 600; color: #F8FAFC; margin-bottom: 1rem;'>Results ({len(result['data'])} {('record' if len(result['data']) == 1 else 'records')})</div>", unsafe_allow_html=True)

                    with col2:
                        json_str = json.dumps(result['data'], indent=2)
                        st.download_button(
                            "📥 Export",
                            json_str,
                            "results.json",
                            "application/json",
                            use_container_width=True,
                            key="export_btn"
                        )

                    with col3:
                        if 'generated_sql' in result:
                            if st.button("📋 SQL", use_container_width=True, key="sql_toggle"):
                                st.session_state.show_sql = not st.session_state.get('show_sql', False)
                                st.rerun()

                    # Data table with pagination
                    st.markdown("---")

                    # Pagination logic
                    items_per_page = 10
                    total_rows = len(result['data'])
                    total_pages = (total_rows + items_per_page - 1) // items_per_page

                    # Get current page data
                    start_idx = st.session_state.results_page * items_per_page
                    end_idx = start_idx + items_per_page
                    page_data = result['data'][start_idx:end_idx]

                    # Display table with minimal height
                    header_height = 40
                    row_height = 35
                    table_height = header_height + (len(page_data) * row_height)

                    st.dataframe(
                        page_data,
                        use_container_width=True,
                        height=table_height,
                        hide_index=True
                    )

                    # Pagination controls
                    if total_pages > 1:
                        st.markdown("---")
                        col1, col2, col3 = st.columns([1, 2, 1])

                        with col1:
                            if st.button("← Prev", use_container_width=True, key="prev_page", disabled=st.session_state.results_page == 0):
                                st.session_state.results_page -= 1
                                st.rerun()

                        with col2:
                            st.markdown(f"<div style='text-align: center; color: #94A3B8; font-size: 0.9rem;'>Page {st.session_state.results_page + 1} / {total_pages}</div>", unsafe_allow_html=True)

                        with col3:
                            if st.button("Next →", use_container_width=True, key="next_page", disabled=st.session_state.results_page >= total_pages - 1):
                                st.session_state.results_page += 1
                                st.rerun()

# ==================== ANOMALIES TAB ====================
if st.session_state.active_tab == 'anomalies':
    st.markdown("### 🚨 Anomaly Detection")

    col1, col2, col3 = st.columns([3, 1, 1])
    with col3:
        if st.button("🔄 Scan", use_container_width=True, key="anomaly_scan"):
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

        # Anomalies Table with Pagination
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

            # Pagination
            items_per_page = 10
            total_anomalies = len(anomaly_df_data)
            total_pages = (total_anomalies + items_per_page - 1) // items_per_page

            start_idx = st.session_state.anomalies_page * items_per_page
            end_idx = start_idx + items_per_page
            page_anomalies = anomaly_df_data[start_idx:end_idx]

            header_height = 40
            row_height = 35
            table_height = header_height + (len(page_anomalies) * row_height)

            st.dataframe(
                page_anomalies,
                use_container_width=True,
                height=table_height,
                hide_index=True
            )

            # Pagination controls
            if total_pages > 1:
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 2, 1])

                with col1:
                    if st.button("← Prev", use_container_width=True, key="prev_anomaly", disabled=st.session_state.anomalies_page == 0):
                        st.session_state.anomalies_page -= 1
                        st.rerun()

                with col2:
                    st.markdown(f"<div style='text-align: center; color: #94A3B8; font-size: 0.9rem;'>Page {st.session_state.anomalies_page + 1} / {total_pages}</div>", unsafe_allow_html=True)

                with col3:
                    if st.button("Next →", use_container_width=True, key="next_anomaly", disabled=st.session_state.anomalies_page >= total_pages - 1):
                        st.session_state.anomalies_page += 1
                        st.rerun()

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

    # Reset pagination when filters change
    st.session_state.analytics_page = 0

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

    # Table with Pagination
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

        # Pagination
        items_per_page = 10
        total_tickets = len(display_data)
        total_pages = (total_tickets + items_per_page - 1) // items_per_page

        start_idx = st.session_state.analytics_page * items_per_page
        end_idx = start_idx + items_per_page
        page_tickets = display_data[start_idx:end_idx]

        header_height = 40
        row_height = 35
        table_height = header_height + (len(page_tickets) * row_height)

        st.dataframe(
            page_tickets,
            use_container_width=True,
            height=table_height,
            hide_index=True
        )

        # Pagination controls
        if total_pages > 1:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])

            with col1:
                if st.button("← Prev", use_container_width=True, key="prev_analytics", disabled=st.session_state.analytics_page == 0):
                    st.session_state.analytics_page -= 1
                    st.rerun()

            with col2:
                st.markdown(f"<div style='text-align: center; color: #94A3B8; font-size: 0.9rem;'>Page {st.session_state.analytics_page + 1} / {total_pages}</div>", unsafe_allow_html=True)

            with col3:
                if st.button("Next →", use_container_width=True, key="next_analytics", disabled=st.session_state.analytics_page >= total_pages - 1):
                    st.session_state.analytics_page += 1
                    st.rerun()
    else:
        st.info("No tickets match the selected filters.")
