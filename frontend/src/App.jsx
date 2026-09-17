import React, { useState, useEffect } from 'react';
import { 
  Bot, 
  Shield, 
  Search, 
  AlertTriangle, 
  BarChart3, 
  Database, 
  Sparkles, 
  Terminal, 
  CheckCircle2, 
  RefreshCw,
  Code2,
  Users,
  Clock,
  Layers
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export default function App() {
  const [activeTab, setActiveTab] = useState('query');
  const [rlsRole, setRlsRole] = useState('admin');
  const [queryMode, setQueryMode] = useState('auto');
  
  // Tab 1 state
  const [userQuery, setUserQuery] = useState('');
  const [queryLoading, setQueryLoading] = useState(false);
  const [queryResult, setQueryResult] = useState(null);
  
  // Tab 2 state
  const [anomaliesLoading, setAnomaliesLoading] = useState(false);
  const [anomaliesData, setAnomaliesData] = useState(null);
  
  // Tab 3 state
  const [ticketsLoading, setTicketsLoading] = useState(false);
  const [ticketsData, setTicketsData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  const sampleQueries = [
    "How many tickets are currently open?",
    "Which agent resolved the most tickets this month?",
    "Show me all Critical tickets not resolved within 12 hours.",
    "What is the average customer rating for Technical category tickets?",
    "Are there any anomalies in resolution times this week?",
    "Find tickets related to invoice charge disputes and billing errors"
  ];

  // Execute Natural Language or RAG Query
  const handleExecuteQuery = async (queryText = userQuery) => {
    if (!queryText.trim()) return;
    setQueryLoading(true);
    setQueryResult(null);
    try {
      const endpoint = queryMode === 'rag' ? `${API_BASE}/api/v1/rag/search` : `${API_BASE}/api/v1/query`;
      const body = queryMode === 'rag' 
        ? { query: queryText, match_count: 5, role: rlsRole }
        : { query: queryText, mode: queryMode, role: rlsRole };

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      setQueryResult(data);
    } catch (err) {
      setQueryResult({ error: `Failed to connect to backend server at ${API_BASE}. Make sure FastAPI is running!` });
    } finally {
      setQueryLoading(false);
    }
  };

  // Fetch Anomaly Scan
  const fetchAnomalies = async () => {
    setAnomaliesLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/anomalies?role=${rlsRole}`);
      const data = await res.json();
      setAnomaliesData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setAnomaliesLoading(false);
    }
  };

  // Fetch Tickets Dataset Analytics
  const fetchTickets = async () => {
    setTicketsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/tickets?limit=500&role=${rlsRole}`);
      const data = await res.json();
      setTicketsData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setTicketsLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'anomalies') fetchAnomalies();
    if (activeTab === 'analytics') fetchTickets();
  }, [activeTab, rlsRole]);

  const filteredTickets = ticketsData.filter(t => 
    t.ticket_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.category?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.issue_summary?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.agent_id?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar Controls */}
      <aside style={{
        width: '300px',
        backgroundColor: 'var(--bg-sidebar)',
        borderRight: '1px solid var(--bg-card-border)',
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '2rem'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#FFF'
            }}>
              <Bot size={24} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#F8FAFC' }}>DOTMappers</h2>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>AI Ticket Analytics</p>
            </div>
          </div>
        </div>

        {/* Security Role Switcher */}
        <div className="glass-card" style={{ padding: '1rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', fontWeight: 600, color: '#E2E8F0', marginBottom: '0.75rem' }}>
            <Shield size={16} color="var(--accent)" /> RLS Security Role
          </label>
          <select 
            value={rlsRole} 
            onChange={(e) => setRlsRole(e.target.value)}
            style={{
              width: '100%',
              padding: '0.6rem 0.75rem',
              backgroundColor: '#1E293B',
              color: '#F8FAFC',
              border: '1px solid #334155',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.875rem',
              cursor: 'pointer'
            }}
          >
            <option value="admin">👑 Admin (Full Access)</option>
            <option value="anon">🌐 Public Anon (Restricted)</option>
            <option value="agent_AGT-04">👤 Agent AGT-04 (Scoped)</option>
            <option value="agent_AGT-01">👤 Agent AGT-01 (Scoped)</option>
          </select>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.5rem', lineHeight: 1.3 }}>
            Controls Supabase PostgreSQL Row Level Security live.
          </p>
        </div>

        {/* Query Engine Mode Selection */}
        <div className="glass-card" style={{ padding: '1rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', fontWeight: 600, color: '#E2E8F0', marginBottom: '0.75rem' }}>
            <Sparkles size={16} color="var(--primary)" /> Query Engine Mode
          </label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {[
              { id: 'auto', label: '✨ Auto-Detect' },
              { id: 'text_to_sql', label: '📊 Text-to-SQL Engine' },
              { id: 'rag', label: '🔍 pgvector Hybrid RAG' }
            ].map(mode => (
              <label key={mode.id} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.6rem',
                fontSize: '0.825rem',
                color: queryMode === mode.id ? '#FFF' : '#94A3B8',
                cursor: 'pointer',
                padding: '0.4rem 0.6rem',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: queryMode === mode.id ? 'rgba(79, 70, 229, 0.25)' : 'transparent',
                border: queryMode === mode.id ? '1px solid rgba(79, 70, 229, 0.5)' : '1px solid transparent'
              }}>
                <input 
                  type="radio" 
                  name="queryMode" 
                  value={mode.id} 
                  checked={queryMode === mode.id} 
                  onChange={() => setQueryMode(mode.id)} 
                />
                {mode.label}
              </label>
            ))}
          </div>
        </div>

        {/* Architecture Specs */}
        <div style={{ marginTop: 'auto', fontSize: '0.75rem', color: 'var(--text-dim)', lineHeight: 1.6 }}>
          <p style={{ fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem' }}>🛠️ Tech Stack</p>
          <p>• Supabase PostgreSQL Cloud</p>
          <p>• `pgvector` Hybrid RAG</p>
          <p>• Groq (Llama-3.3-70b)</p>
          <p>• FastAPI REST Backend</p>
        </div>
      </aside>

      {/* Main Content Area */}
      <main style={{ flex: 1, padding: '2rem 2.5rem', overflowY: 'auto' }}>
        {/* Top Header Bar */}
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <div>
            <h1 className="header-title">AI Support Ticket Analytics</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.2rem' }}>
              DOTMappers Technical Assessment • Active Security Role: <span className={`badge badge-${rlsRole.split('_')[0]}`}>{rlsRole.toUpperCase()}</span>
            </p>
          </div>
        </header>

        {/* Navigation Tabs */}
        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '2rem', borderBottom: '1px solid var(--bg-card-border)', paddingBottom: '0.75rem' }}>
          {[
            { id: 'query', label: '💬 Natural Language Query & RAG', icon: Bot },
            { id: 'anomalies', label: '🚨 Anomaly Detection Radar', icon: AlertTriangle },
            { id: 'analytics', label: '📊 Dataset Analytics & RLS Test', icon: BarChart3 }
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  background: isActive ? 'linear-gradient(135deg, rgba(79, 70, 229, 0.2) 0%, rgba(6, 182, 212, 0.2) 100%)' : 'transparent',
                  border: isActive ? '1px solid var(--accent)' : '1px solid transparent',
                  color: isActive ? '#FFFFFF' : 'var(--text-muted)',
                  padding: '0.6rem 1.25rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  transition: 'all 0.2s ease'
                }}
              >
                <Icon size={18} color={isActive ? 'var(--accent)' : 'var(--text-muted)'} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* TAB 1: NATURAL LANGUAGE QUERY & RAG */}
        {activeTab === 'query' && (
          <div>
            <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Sparkles size={20} color="var(--accent)" /> Ask Anything About Support Tickets
              </h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '1rem' }}>
                Select a sample query chip or type your question below:
              </p>

              {/* Sample Question Chips */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '0.6rem', marginBottom: '1.25rem' }}>
                {sampleQueries.map((q, idx) => (
                  <button key={idx} className="chip-btn" onClick={() => { setUserQuery(q); handleExecuteQuery(q); }}>
                    💡 {q}
                  </button>
                ))}
              </div>

              {/* Input & Action */}
              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <div style={{ flex: 1, position: 'relative' }}>
                  <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-dim)' }} />
                  <input
                    type="text"
                    value={userQuery}
                    onChange={(e) => setUserQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleExecuteQuery()}
                    placeholder="e.g. How many critical tickets are unresolved?"
                    style={{
                      width: '100%',
                      padding: '0.85rem 1rem 0.85rem 2.75rem',
                      backgroundColor: '#1E293B',
                      color: '#FFF',
                      border: '1px solid #334155',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.95rem',
                      outline: 'none'
                    }}
                  />
                </div>
                <button className="btn-primary" onClick={() => handleExecuteQuery()} disabled={queryLoading}>
                  {queryLoading ? <RefreshCw size={18} className="animate-spin" /> : <Sparkles size={18} />}
                  {queryLoading ? 'Processing...' : 'Execute Query'}
                </button>
              </div>
            </div>

            {/* AI Result Card */}
            {queryResult && (
              <div className="glass-card" style={{ borderColor: queryResult.error ? 'var(--danger)' : 'rgba(79, 70, 229, 0.4)' }}>
                {queryResult.error ? (
                  <div style={{ color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <AlertTriangle size={20} /> {queryResult.error}
                  </div>
                ) : (
                  <div>
                    <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--accent)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Bot size={18} /> AI Response Summary
                    </h4>
                    <p style={{ fontSize: '1rem', color: '#F8FAFC', background: 'rgba(30, 41, 59, 0.6)', padding: '1rem', borderRadius: 'var(--radius-sm)', marginBottom: '1rem', lineHeight: 1.6 }}>
                      {queryResult.answer}
                    </p>

                    {queryResult.generated_sql && (
                      <div style={{ marginBottom: '1.25rem' }}>
                        <p style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <Terminal size={14} /> Generated Safe SQL Query:
                        </p>
                        <pre style={{ background: '#0F172A', padding: '0.85rem', borderRadius: 'var(--radius-sm)', color: '#38BDF8', fontSize: '0.85rem', overflowX: 'auto', border: '1px solid #1E293B' }}>
                          {queryResult.generated_sql}
                        </pre>
                      </div>
                    )}

                    {/* Data Table */}
                    {queryResult.data && queryResult.data.length > 0 && (
                      <div>
                        <p style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                          Returned Data ({queryResult.results_count || queryResult.data.length} records):
                        </p>
                        <div className="data-table-container">
                          <table className="data-table">
                            <thead>
                              <tr>
                                {Object.keys(queryResult.data[0]).map(key => (
                                  <th key={key}>{key}</th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {queryResult.data.map((row, rIdx) => (
                                <tr key={rIdx}>
                                  {Object.values(row).map((val, cIdx) => (
                                    <td key={cIdx}>{typeof val === 'object' ? JSON.stringify(val) : String(val)}</td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* TAB 2: ANOMALY DETECTION RADAR */}
        {activeTab === 'anomalies' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Multi-Factor Anomaly & SLA Breach Radar</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                  Statistical Outliers (IQR / Z-Score) + Business SLA Breach Scanner
                </p>
              </div>
              <button className="btn-primary" onClick={fetchAnomalies} disabled={anomaliesLoading}>
                <RefreshCw size={16} /> Run Anomaly Scan
              </button>
            </div>

            {anomaliesData && (
              <>
                {/* Metric Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.25rem', marginBottom: '1.5rem' }}>
                  <div className="glass-card">
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Total Anomalies Flagged</p>
                    <p style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--accent)', marginTop: '0.2rem' }}>{anomaliesData.total_anomalies}</p>
                  </div>
                  <div className="glass-card" style={{ borderColor: 'rgba(239, 68, 68, 0.4)' }}>
                    <p style={{ fontSize: '0.8rem', color: 'var(--danger)', textTransform: 'uppercase', fontWeight: 600 }}>Critical SLA Breaches</p>
                    <p style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--danger)', marginTop: '0.2rem' }}>{anomaliesData.critical_count}</p>
                  </div>
                  <div className="glass-card" style={{ borderColor: 'rgba(245, 158, 11, 0.4)' }}>
                    <p style={{ fontSize: '0.8rem', color: 'var(--warning)', textTransform: 'uppercase', fontWeight: 600 }}>Warning Anomalies</p>
                    <p style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--warning)', marginTop: '0.2rem' }}>{anomaliesData.warning_count}</p>
                  </div>
                </div>

                {/* Narrative Summary */}
                <div className="glass-card" style={{ marginBottom: '1.5rem', background: 'rgba(16, 185, 129, 0.1)', borderColor: 'rgba(16, 185, 129, 0.3)' }}>
                  <h4 style={{ color: 'var(--success)', fontWeight: 700, marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Bot size={18} /> Executive Summary Narrative
                  </h4>
                  <p style={{ color: '#E2E8F0', fontSize: '0.925rem', lineHeight: 1.6 }}>{anomaliesData.narrative_summary}</p>
                </div>

                {/* Anomalies Table */}
                <div className="glass-card">
                  <h4 style={{ fontWeight: 700, marginBottom: '1rem' }}>Flagged Anomaly Records</h4>
                  <div className="data-table-container">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Ticket ID</th>
                          <th>Category</th>
                          <th>Priority</th>
                          <th>Status</th>
                          <th>Agent ID</th>
                          <th>Anomaly Type</th>
                          <th>Severity</th>
                          <th>Issue Summary</th>
                        </tr>
                      </thead>
                      <tbody>
                        {anomaliesData.anomalies?.map((a, idx) => (
                          <tr key={idx}>
                            <td style={{ fontWeight: 600, color: '#38BDF8' }}>{a.ticket_id}</td>
                            <td>{a.category}</td>
                            <td>
                              <span className={`badge ${a.priority === 'Critical' ? 'badge-critical' : 'badge-warning'}`}>
                                {a.priority}
                              </span>
                            </td>
                            <td>{a.status}</td>
                            <td>{a.agent_id}</td>
                            <td style={{ fontWeight: 500 }}>{a.anomaly_type}</td>
                            <td>
                              <span className={`badge ${a.severity === 'CRITICAL' ? 'badge-critical' : 'badge-warning'}`}>
                                {a.severity}
                              </span>
                            </td>
                            <td style={{ color: 'var(--text-muted)' }}>{a.issue_summary}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* TAB 3: DATASET ANALYTICS & RLS AUDIT */}
        {activeTab === 'analytics' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Dataset Analytics & Row-Level Security Verification</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                  Live records filtered according to active security role: <span className="badge badge-admin">{rlsRole.toUpperCase()}</span>
                </p>
              </div>
              <div style={{ position: 'relative', width: '300px' }}>
                <Search size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-dim)' }} />
                <input
                  type="text"
                  placeholder="Filter records..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.5rem 0.75rem 0.5rem 2.25rem',
                    backgroundColor: '#1E293B',
                    color: '#FFF',
                    border: '1px solid #334155',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.85rem'
                  }}
                />
              </div>
            </div>

            {/* Stats Overview */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.25rem', marginBottom: '1.5rem' }}>
              <div className="glass-card">
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Visible Records (RLS Enforced)</p>
                <p style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--accent)', marginTop: '0.2rem' }}>{filteredTickets.length}</p>
              </div>
              <div className="glass-card">
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Resolved Tickets</p>
                <p style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--success)', marginTop: '0.2rem' }}>
                  {filteredTickets.filter(t => t.status === 'Resolved').length}
                </p>
              </div>
              <div className="glass-card">
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Escalated / Open</p>
                <p style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--warning)', marginTop: '0.2rem' }}>
                  {filteredTickets.filter(t => t.status !== 'Resolved').length}
                </p>
              </div>
            </div>

            {/* Tickets Raw Table */}
            <div className="glass-card">
              <div className="data-table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Ticket ID</th>
                      <th>Category</th>
                      <th>Priority</th>
                      <th>Status</th>
                      <th>Created At</th>
                      <th>Agent ID</th>
                      <th>Customer Rating</th>
                      <th>Issue Summary</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredTickets.slice(0, 100).map((t, idx) => (
                      <tr key={idx}>
                        <td style={{ fontWeight: 600, color: '#38BDF8' }}>{t.ticket_id}</td>
                        <td>{t.category}</td>
                        <td>
                          <span className={`badge ${t.priority === 'Critical' ? 'badge-critical' : 'badge-warning'}`}>
                            {t.priority}
                          </span>
                        </td>
                        <td>{t.status}</td>
                        <td>{t.created_at ? new Date(t.created_at).toLocaleDateString() : 'N/A'}</td>
                        <td>{t.agent_id}</td>
                        <td>{t.customer_rating ? `⭐ ${t.customer_rating}` : 'N/A'}</td>
                        <td style={{ color: 'var(--text-muted)' }}>{t.issue_summary}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
