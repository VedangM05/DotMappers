import React, { useState, useEffect } from 'react';
import {
  Bot, Shield, Search, AlertTriangle, BarChart3, Database, Sparkles, Terminal,
  CheckCircle2, RefreshCw, Code2, Users, Clock, Layers, Download, Heart,
  History, Settings, Moon, Sun, ChevronDown, X, TrendingUp
} from 'lucide-react';

const API_BASE = 'http://localhost:8080';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [rlsRole, setRlsRole] = useState('admin');
  const [queryMode, setQueryMode] = useState('auto');
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [queryExecutionTime, setQueryExecutionTime] = useState(null);
  const [queryHistory, setQueryHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [dashboardStats, setDashboardStats] = useState(null);

  const [userQuery, setUserQuery] = useState('');
  const [queryLoading, setQueryLoading] = useState(false);
  const [queryResult, setQueryResult] = useState(null);
  const [resultPage, setResultPage] = useState(0);
  const [showSqlDetails, setShowSqlDetails] = useState(false);
  const [copiedSql, setCopiedSql] = useState(false);

  const [anomaliesLoading, setAnomaliesLoading] = useState(false);
  const [anomaliesData, setAnomaliesData] = useState(null);
  const [anomaliesPage, setAnomaliesPage] = useState(0);

  const [ticketsLoading, setTicketsLoading] = useState(false);
  const [ticketsData, setTicketsData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [analyticsPage, setAnalyticsPage] = useState(0);
  const [filterCategory, setFilterCategory] = useState('');
  const [filterPriority, setFilterPriority] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [filterAgent, setFilterAgent] = useState('');

  const sampleQueries = [
    "How many tickets are currently open?",
    "Which agent resolved the most tickets this month?",
    "Show me all Critical tickets not resolved within 12 hours.",
    "What is the average customer rating for Technical category tickets?",
    "Are there any anomalies in resolution times this week?",
    "Find tickets related to invoice charge disputes and billing errors"
  ];

  const fetchDashboardStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/health`);
      const data = await res.json();
      setDashboardStats(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const handleExecuteQuery = async (queryText = userQuery) => {
    if (!queryText.trim()) return;

    setQueryLoading(true);
    setQueryResult(null);
    setResultPage(0);
    const startTime = Date.now();

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

      const executionTime = Date.now() - startTime;
      setQueryExecutionTime(executionTime);
      console.log('Query Response:', data);
      setQueryResult(data);

      if (!data.error) {
        setQueryHistory(prev => [{ query: queryText, time: new Date(), mode: queryMode }, ...prev].slice(0, 10));
      }
    } catch (err) {
      setQueryResult({ error: `Failed to connect to backend server at ${API_BASE}. Make sure FastAPI is running!` });
    } finally {
      setQueryLoading(false);
    }
  };

  const downloadResults = (data, filename = 'results.json') => {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
  };

  const copySqlToClipboard = (sql) => {
    navigator.clipboard.writeText(sql);
    setCopiedSql(true);
    setTimeout(() => setCopiedSql(false), 2000);
  };

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

  const fetchTickets = async () => {
    setTicketsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/tickets?limit=500&role=${rlsRole}`);
      const data = await res.json();
      setTicketsData(data.tickets || []);
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

  const filteredTickets = (ticketsData || []).filter(t => {
    const matchSearch = !searchTerm ||
      t.ticket_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.category?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.issue_summary?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.agent_id?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchCategory = !filterCategory || t.category === filterCategory;
    const matchPriority = !filterPriority || t.priority === filterPriority;
    const matchStatus = !filterStatus || t.status === filterStatus;
    const matchAgent = !filterAgent || t.agent_id === filterAgent;

    return matchSearch && matchCategory && matchPriority && matchStatus && matchAgent;
  });

  // Reset page when filters change
  useEffect(() => {
    setAnalyticsPage(0);
  }, [searchTerm, filterCategory, filterPriority, filterStatus, filterAgent]);

  const ITEMS_PER_PAGE = 20;
  const paginatedResults = queryResult?.data?.slice(
    resultPage * ITEMS_PER_PAGE,
    (resultPage + 1) * ITEMS_PER_PAGE
  ) || [];

  const bgColor = isDarkMode ? '#0F172A' : '#F8FAFC';
  const cardBg = isDarkMode ? '#1E293B' : '#F8FAFC';
  const textPrimary = isDarkMode ? '#F8FAFC' : '#0F172A';
  const textSecondary = isDarkMode ? '#94A3B8' : '#64748B';
  const border = isDarkMode ? '#334155' : '#E2E8F0';

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: bgColor }}>
      {/* Sidebar */}
      <aside style={{
        width: '320px',
        backgroundColor: bgColor,
        borderRight: `1px solid ${border}`,
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem',
        overflowY: 'auto'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '40px', height: '40px', borderRadius: '10px',
              background: 'linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#FFF'
            }}>
              <Bot size={24} />
            </div>
            <div>
              <h2 style={{ fontSize: '1rem', fontWeight: 700, color: textPrimary }}>DOTMappers</h2>
              <p style={{ fontSize: '0.7rem', color: textSecondary }}>AI Analytics</p>
            </div>
          </div>
          <button onClick={() => setIsDarkMode(!isDarkMode)} style={{
            background: 'transparent', border: 'none', cursor: 'pointer', padding: '0.4rem', display: 'flex'
          }}>
            {isDarkMode ? <Sun size={18} color="#F59E0B" /> : <Moon size={18} color="#6366F1" />}
          </button>
        </div>


        <div style={{ padding: '0.85rem', backgroundColor: cardBg, borderRadius: '0.5rem', border: `1px solid ${border}` }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', fontWeight: 600, color: textPrimary, marginBottom: '0.6rem' }}>
            <Sparkles size={14} color="#4F46E5" /> Query Mode
          </label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
            {[{ id: 'auto', label: '✨ Auto-Detect' }, { id: 'text_to_sql', label: '📊 Text-to-SQL' }, { id: 'rag', label: '🔍 Vector RAG' }].map(mode => (
              <label key={mode.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', cursor: 'pointer' }}>
                <input type="radio" name="queryMode" value={mode.id} checked={queryMode === mode.id} onChange={() => setQueryMode(mode.id)} />
                <span style={{ color: queryMode === mode.id ? '#4F46E5' : textSecondary }}>{mode.label}</span>
              </label>
            ))}
          </div>
        </div>

        {queryHistory.length > 0 && (
          <div>
            <button onClick={() => setShowHistory(!showHistory)} style={{
              width: '100%', display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0.75rem',
              backgroundColor: cardBg, border: `1px solid ${border}`, borderRadius: '0.4rem',
              cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600, color: textPrimary
            }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <History size={14} /> History ({queryHistory.length})
              </span>
              <ChevronDown size={14} style={{ transform: showHistory ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }} />
            </button>
            {showHistory && (
              <div style={{ marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                {queryHistory.map((item, idx) => (
                  <button key={idx} onClick={() => { setUserQuery(item.query); handleExecuteQuery(item.query); }} style={{
                    padding: '0.5rem 0.65rem', backgroundColor: cardBg, border: 'none', borderRadius: '0.4rem',
                    cursor: 'pointer', textAlign: 'left', fontSize: '0.8rem', color: textSecondary,
                    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'
                  }} title={item.query}>
                    {item.query}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, overflowY: 'auto', padding: '2rem' }}>
        <header style={{ marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: textPrimary, marginBottom: '0.3rem' }}>
            AI Support Ticket Analytics
          </h1>
          <p style={{ color: textSecondary, fontSize: '0.95rem' }}>
            DOTMappers Assessment • Role: <span style={{ fontWeight: 600, color: '#06B6D4' }}>{rlsRole.toUpperCase()}</span>
          </p>
        </header>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: `1px solid ${border}`, paddingBottom: '0.75rem' }}>
          {[
            { id: 'dashboard', label: '📊 Dashboard', icon: BarChart3 },
            { id: 'query', label: '💬 Query', icon: Bot },
            { id: 'anomalies', label: '🚨 Anomalies', icon: AlertTriangle },
            { id: 'analytics', label: '📈 Analytics', icon: TrendingUp }
          ].map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
              background: activeTab === tab.id ? (isDarkMode ? 'rgba(79, 70, 229, 0.2)' : 'rgba(79, 70, 229, 0.1)') : 'transparent',
              border: activeTab === tab.id ? `1px solid #4F46E5` : '1px solid transparent',
              color: activeTab === tab.id ? '#4F46E5' : textSecondary,
              padding: '0.6rem 1rem', borderRadius: '0.4rem', fontSize: '0.9rem', fontWeight: 600,
              cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', transition: 'all 0.2s'
            }}>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
              <div style={{ padding: '1.5rem', backgroundColor: cardBg, borderRadius: '0.5rem', border: `1px solid ${border}` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.85rem', color: textSecondary, fontWeight: 600 }}>Total Tickets</span>
                  <Database size={18} color="#06B6D4" />
                </div>
                <p style={{ fontSize: '2rem', fontWeight: 800, color: '#06B6D4' }}>{dashboardStats?.total_tickets || 0}</p>
              </div>

              <div style={{ padding: '1.5rem', backgroundColor: cardBg, borderRadius: '0.5rem', border: `1px solid ${border}` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.85rem', color: textSecondary, fontWeight: 600 }}>Queries</span>
                  <Search size={18} color="#4F46E5" />
                </div>
                <p style={{ fontSize: '2rem', fontWeight: 800, color: '#4F46E5' }}>{queryHistory.length}</p>
              </div>

              <div style={{ padding: '1.5rem', backgroundColor: cardBg, borderRadius: '0.5rem', border: `1px solid ${border}` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.85rem', color: textSecondary, fontWeight: 600 }}>Response Time</span>
                  <Clock size={18} color="#F59E0B" />
                </div>
                <p style={{ fontSize: '2rem', fontWeight: 800, color: '#F59E0B' }}>{queryExecutionTime ? `${queryExecutionTime}ms` : 'N/A'}</p>
              </div>
            </div>

            <div style={{ padding: '1.5rem', backgroundColor: cardBg, borderRadius: '0.5rem', border: `1px solid ${border}` }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: textPrimary, marginBottom: '1rem' }}>🚀 Quick Start</h3>
              <p style={{ color: textSecondary, marginBottom: '1rem', lineHeight: 1.6 }}>
                Select a sample query to get started with the AI-powered analytics system.
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
                {sampleQueries.map((q, idx) => (
                  <button key={idx} onClick={() => { setUserQuery(q); setActiveTab('query'); handleExecuteQuery(q); }} style={{
                    padding: '0.75rem 1rem', backgroundColor: bgColor, border: `1px solid ${border}`, borderRadius: '0.4rem',
                    cursor: 'pointer', fontSize: '0.85rem', color: textPrimary, textAlign: 'left', fontWeight: 500, transition: 'all 0.2s'
                  }}>
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Query Tab */}
        {activeTab === 'query' && (
          <div>
            <div style={{ padding: '1.5rem', backgroundColor: cardBg, borderRadius: '0.5rem', border: `1px solid ${border}`, marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem' }}>
                <div style={{ flex: 1, position: 'relative' }}>
                  <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: '#64748B' }} />
                  <input type="text" value={userQuery} onChange={(e) => setUserQuery(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleExecuteQuery()}
                    placeholder="Ask anything about tickets..." style={{
                    width: '100%', padding: '0.85rem 1rem 0.85rem 2.75rem', backgroundColor: bgColor, color: textPrimary,
                    border: `1px solid ${border}`, borderRadius: '0.4rem', fontSize: '0.95rem', outline: 'none'
                  }} />
                </div>
                <button onClick={() => handleExecuteQuery()} disabled={queryLoading} style={{
                  padding: '0.85rem 1.5rem', backgroundColor: queryLoading ? '#64748B' : '#4F46E5', color: '#FFF',
                  border: 'none', borderRadius: '0.4rem', cursor: queryLoading ? 'not-allowed' : 'pointer',
                  fontWeight: 600, fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem'
                }}>
                  {queryLoading ? <RefreshCw size={16} /> : <Sparkles size={16} />}
                  {queryLoading ? 'Processing...' : 'Execute'}
                </button>
              </div>
              {queryExecutionTime && <p style={{ fontSize: '0.8rem', color: textSecondary }}>⏱️ Completed in {queryExecutionTime}ms</p>}
            </div>

            {queryResult && (
              <div style={{ padding: '1.5rem', backgroundColor: cardBg, borderRadius: '0.5rem', border: `1px solid ${border}` }}>
                {queryResult.error ? (
                  <div style={{ color: '#EF4444', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.95rem' }}>
                    <AlertTriangle size={18} /> {queryResult.error}
                  </div>
                ) : (
                  <>
                    {queryResult.answer && (
                      <p style={{ fontSize: '0.9rem', color: textSecondary, marginBottom: '1rem', padding: '0.75rem', backgroundColor: bgColor, borderRadius: '0.3rem' }}>
                        {queryResult.answer}
                      </p>
                    )}

                    {queryResult.data && queryResult.data.length > 0 && (
                      <>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                          <p style={{ fontSize: '0.8rem', fontWeight: 600, color: textSecondary }}>
                            Results ({queryResult.results_count || queryResult.data.length} records)
                          </p>
                          <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <button onClick={() => downloadResults(queryResult.data, 'query_results.json')} style={{
                              padding: '0.4rem 0.75rem', backgroundColor: 'transparent', border: `1px solid ${border}`, borderRadius: '0.3rem',
                              cursor: 'pointer', fontSize: '0.75rem', color: textSecondary, display: 'flex', alignItems: 'center', gap: '0.3rem'
                            }}>
                              <Download size={12} /> Export
                            </button>
                            {queryResult.generated_sql && (
                              <button onClick={() => setShowSqlDetails(!showSqlDetails)} style={{
                                padding: '0.4rem 0.75rem', backgroundColor: showSqlDetails ? '#4F46E5' : 'transparent', border: `1px solid ${border}`, borderRadius: '0.3rem',
                                cursor: 'pointer', fontSize: '0.75rem', color: showSqlDetails ? '#FFF' : textSecondary, display: 'flex', alignItems: 'center', gap: '0.3rem'
                              }}>
                                <Code2 size={12} /> SQL
                              </button>
                            )}
                          </div>
                        </div>

                        <div style={{ overflowX: 'auto', marginBottom: '1rem' }}>
                          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                            <thead>
                              <tr style={{ borderBottom: `1px solid ${border}` }}>
                                {Object.keys(queryResult.data[0]).map(key => (
                                  <th key={key} style={{ padding: '0.6rem', textAlign: 'left', fontWeight: 600, color: textPrimary }}>
                                    {key}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {paginatedResults.map((row, rIdx) => (
                                <tr key={rIdx} style={{ borderBottom: `1px solid ${isDarkMode ? '#1E293B' : '#F1F5F9'}` }}>
                                  {Object.values(row).map((val, cIdx) => (
                                    <td key={cIdx} style={{ padding: '0.6rem', color: textSecondary }}>
                                      {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>

                        {Math.ceil((queryResult.data.length || 0) / ITEMS_PER_PAGE) > 1 && (
                          <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', alignItems: 'center', marginBottom: '1rem' }}>
                            <button onClick={() => setResultPage(prev => Math.max(0, prev - 1))} disabled={resultPage === 0} style={{
                              padding: '0.4rem 0.6rem', backgroundColor: cardBg, border: `1px solid ${border}`, borderRadius: '0.3rem',
                              cursor: resultPage === 0 ? 'not-allowed' : 'pointer', color: textSecondary, fontSize: '0.75rem'
                            }}>
                              ← Prev
                            </button>
                            <span style={{ fontSize: '0.75rem', color: textSecondary }}>
                              {resultPage + 1} / {Math.ceil((queryResult.data.length || 0) / ITEMS_PER_PAGE)}
                            </span>
                            <button onClick={() => setResultPage(prev => prev + 1)} disabled={resultPage >= Math.ceil((queryResult.data.length || 0) / ITEMS_PER_PAGE) - 1} style={{
                              padding: '0.4rem 0.6rem', backgroundColor: cardBg, border: `1px solid ${border}`, borderRadius: '0.3rem',
                              cursor: resultPage >= Math.ceil((queryResult.data.length || 0) / ITEMS_PER_PAGE) - 1 ? 'not-allowed' : 'pointer', color: textSecondary, fontSize: '0.75rem'
                            }}>
                              Next →
                            </button>
                          </div>
                        )}

                        {showSqlDetails && queryResult.generated_sql && (
                          <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: bgColor, borderRadius: '0.3rem', border: `1px solid ${border}` }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                              <p style={{ fontSize: '0.75rem', fontWeight: 600, color: textSecondary, margin: 0 }}>
                                <Terminal size={12} style={{ display: 'inline', marginRight: '0.3rem' }} />Generated SQL
                              </p>
                              <button onClick={() => copySqlToClipboard(queryResult.generated_sql)} style={{
                                padding: '0.3rem 0.6rem', backgroundColor: copiedSql ? '#10B981' : 'transparent', border: `1px solid ${border}`, borderRadius: '0.2rem',
                                cursor: 'pointer', fontSize: '0.7rem', color: copiedSql ? '#FFF' : textSecondary, display: 'flex', alignItems: 'center', gap: '0.2rem',
                                transition: 'all 0.2s'
                              }}>
                                {copiedSql ? '✓ Copied' : 'Copy'}
                              </button>
                            </div>
                            <pre style={{
                              color: '#38BDF8', fontSize: '0.8rem', overflowX: 'auto', margin: 0
                            }}>
                              {queryResult.generated_sql}
                            </pre>
                          </div>
                        )}
                      </>
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        )}

        {/* Anomalies Tab */}
        {activeTab === 'anomalies' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: textPrimary }}>🚨 Anomaly Detection</h3>
              <button onClick={fetchAnomalies} disabled={anomaliesLoading} style={{
                padding: '0.6rem 1.25rem', backgroundColor: anomaliesLoading ? '#64748B' : '#4F46E5', color: '#FFF',
                border: 'none', borderRadius: '0.4rem', cursor: anomaliesLoading ? 'not-allowed' : 'pointer',
                fontWeight: 600, fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem'
              }}>
                <RefreshCw size={16} /> Scan
              </button>
            </div>

            {anomaliesData && (
              <>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                  <div style={{ padding: '1.25rem', backgroundColor: cardBg, borderRadius: '0.5rem', border: `1px solid ${border}` }}>
                    <p style={{ fontSize: '0.8rem', color: textSecondary, fontWeight: 600, marginBottom: '0.3rem' }}>TOTAL</p>
                    <p style={{ fontSize: '2rem', fontWeight: 800, color: '#06B6D4' }}>{anomaliesData.total_anomalies}</p>
                  </div>
                  <div style={{ padding: '1.25rem', backgroundColor: isDarkMode ? '#7F1D1D' : '#FEE2E2', borderRadius: '0.5rem', border: `1px solid ${isDarkMode ? '#991B1B' : '#FECACA'}` }}>
                    <p style={{ fontSize: '0.8rem', color: isDarkMode ? '#FECACA' : '#991B1B', fontWeight: 600, marginBottom: '0.3rem' }}>CRITICAL</p>
                    <p style={{ fontSize: '2rem', fontWeight: 800, color: isDarkMode ? '#FCA5A5' : '#DC2626' }}>{anomaliesData.critical_count}</p>
                  </div>
                  <div style={{ padding: '1.25rem', backgroundColor: isDarkMode ? '#78350F' : '#FEF3C7', borderRadius: '0.5rem', border: `1px solid ${isDarkMode ? '#B45309' : '#FCD34D'}` }}>
                    <p style={{ fontSize: '0.8rem', color: isDarkMode ? '#FCD34D' : '#B45309', fontWeight: 600, marginBottom: '0.3rem' }}>WARNING</p>
                    <p style={{ fontSize: '2rem', fontWeight: 800, color: isDarkMode ? '#FBBF24' : '#F59E0B' }}>{anomaliesData.warning_count}</p>
                  </div>
                </div>

                <div style={{ padding: '1.25rem', backgroundColor: isDarkMode ? '#064E3B' : '#D1FAE5', borderRadius: '0.5rem', border: `1px solid ${isDarkMode ? '#059669' : '#6EE7B7'}`, marginBottom: '1.5rem' }}>
                  <p style={{ fontSize: '0.85rem', fontWeight: 700, color: isDarkMode ? '#6EE7B7' : '#065F46', marginBottom: '0.5rem' }}>📋 Summary</p>
                  <p style={{ fontSize: '0.95rem', color: isDarkMode ? '#D1FAE5' : '#065F46', lineHeight: 1.6 }}>{anomaliesData.narrative_summary}</p>
                </div>

                <div style={{ padding: '1.25rem', backgroundColor: cardBg, borderRadius: '0.5rem', border: `1px solid ${border}`, overflowX: 'auto' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h4 style={{ fontWeight: 700, margin: 0, color: textPrimary }}>Flagged Records ({anomaliesData.anomalies?.length || 0} total)</h4>
                  </div>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', marginBottom: '1rem' }}>
                    <thead>
                      <tr style={{ borderBottom: `1px solid ${border}` }}>
                        <th style={{ padding: '0.6rem', textAlign: 'left', fontWeight: 600, color: textPrimary }}>Ticket ID</th>
                        <th style={{ padding: '0.6rem', textAlign: 'left', fontWeight: 600, color: textPrimary }}>Type</th>
                        <th style={{ padding: '0.6rem', textAlign: 'left', fontWeight: 600, color: textPrimary }}>Severity</th>
                        <th style={{ padding: '0.6rem', textAlign: 'left', fontWeight: 600, color: textPrimary }}>Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      {anomaliesData.anomalies?.slice(anomaliesPage * 10, (anomaliesPage + 1) * 10).map((a, idx) => (
                        <tr key={idx} style={{ borderBottom: `1px solid ${isDarkMode ? '#1E293B' : '#F1F5F9'}` }}>
                          <td style={{ padding: '0.6rem', fontWeight: 600, color: '#06B6D4' }}>{a.ticket_id}</td>
                          <td style={{ padding: '0.6rem', color: textSecondary }}>{a.anomaly_type.substring(0, 30)}</td>
                          <td style={{ padding: '0.6rem' }}>
                            <span style={{ padding: '0.3rem 0.6rem', borderRadius: '0.3rem', fontSize: '0.75rem', fontWeight: 600, backgroundColor: a.severity === 'CRITICAL' ? '#7F1D1D' : '#78350F', color: a.severity === 'CRITICAL' ? '#FCA5A5' : '#FCD34D' }}>
                              {a.severity}
                            </span>
                          </td>
                          <td style={{ padding: '0.6rem', color: '#64748B', fontSize: '0.8rem' }}>{a.details}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

                  {anomaliesData.anomalies && Math.ceil((anomaliesData.anomalies.length || 0) / 10) > 1 && (
                    <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', alignItems: 'center' }}>
                      <button onClick={() => setAnomaliesPage(prev => Math.max(0, prev - 1))} disabled={anomaliesPage === 0} style={{
                        padding: '0.4rem 0.6rem', backgroundColor: cardBg, border: `1px solid ${border}`, borderRadius: '0.3rem',
                        cursor: anomaliesPage === 0 ? 'not-allowed' : 'pointer', color: textSecondary, fontSize: '0.75rem'
                      }}>
                        ← Prev
                      </button>
                      <span style={{ fontSize: '0.75rem', color: textSecondary }}>
                        {anomaliesPage + 1} / {Math.ceil((anomaliesData.anomalies.length || 0) / 10)}
                      </span>
                      <button onClick={() => setAnomaliesPage(prev => prev + 1)} disabled={anomaliesPage >= Math.ceil((anomaliesData.anomalies.length || 0) / 10) - 1} style={{
                        padding: '0.4rem 0.6rem', backgroundColor: cardBg, border: `1px solid ${border}`, borderRadius: '0.3rem',
                        cursor: anomaliesPage >= Math.ceil((anomaliesData.anomalies.length || 0) / 10) - 1 ? 'not-allowed' : 'pointer', color: textSecondary, fontSize: '0.75rem'
                      }}>
                        Next →
                      </button>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div>
            <div style={{ marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: textPrimary }}>📈 Dataset Analytics</h3>
              </div>
              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
                <div style={{ position: 'relative', flex: 1, minWidth: '200px' }}>
                  <Search size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: '#64748B' }} />
                  <input type="text" placeholder="Search..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} style={{
                    width: '100%', padding: '0.6rem 0.75rem 0.6rem 2.25rem', backgroundColor: cardBg, color: textPrimary,
                    border: `1px solid ${border}`, borderRadius: '0.4rem', fontSize: '0.85rem'
                  }} />
                </div>
                <select value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)} style={{
                  padding: '0.6rem 0.75rem', backgroundColor: cardBg, color: textPrimary, border: `1px solid ${border}`, borderRadius: '0.4rem', fontSize: '0.85rem', cursor: 'pointer'
                }}>
                  <option value="">All Categories</option>
                  <option value="Billing">Billing</option>
                  <option value="General">General</option>
                  <option value="Technical">Technical</option>
                </select>
                <select value={filterPriority} onChange={(e) => setFilterPriority(e.target.value)} style={{
                  padding: '0.6rem 0.75rem', backgroundColor: cardBg, color: textPrimary, border: `1px solid ${border}`, borderRadius: '0.4rem', fontSize: '0.85rem', cursor: 'pointer'
                }}>
                  <option value="">All Priorities</option>
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Critical">Critical</option>
                </select>
                <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} style={{
                  padding: '0.6rem 0.75rem', backgroundColor: cardBg, color: textPrimary, border: `1px solid ${border}`, borderRadius: '0.4rem', fontSize: '0.85rem', cursor: 'pointer'
                }}>
                  <option value="">All Status</option>
                  <option value="Open">Open</option>
                  <option value="Resolved">Resolved</option>
                  <option value="Escalated">Escalated</option>
                </select>
                <select value={filterAgent} onChange={(e) => setFilterAgent(e.target.value)} style={{
                  padding: '0.6rem 0.75rem', backgroundColor: cardBg, color: textPrimary, border: `1px solid ${border}`, borderRadius: '0.4rem', fontSize: '0.85rem', cursor: 'pointer'
                }}>
                  <option value="">All Agents</option>
                  {Array.from({ length: 12 }, (_, i) => `AGT-${String(i + 1).padStart(2, '0')}`).map(agent => (
                    <option key={agent} value={agent}>{agent}</option>
                  ))}
                </select>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ padding: '1.25rem', backgroundColor: cardBg, borderRadius: '0.5rem', border: `1px solid ${border}` }}>
                <p style={{ fontSize: '0.8rem', color: textSecondary, fontWeight: 600, marginBottom: '0.3rem' }}>VISIBLE</p>
                <p style={{ fontSize: '2rem', fontWeight: 800, color: '#06B6D4' }}>{filteredTickets?.length || 0}</p>
              </div>
              <div style={{ padding: '1.25rem', backgroundColor: cardBg, borderRadius: '0.5rem', border: `1px solid ${border}` }}>
                <p style={{ fontSize: '0.8rem', color: textSecondary, fontWeight: 600, marginBottom: '0.3rem' }}>RESOLVED</p>
                <p style={{ fontSize: '2rem', fontWeight: 800, color: '#10B981' }}>{filteredTickets?.filter(t => t.status === 'Resolved').length || 0}</p>
              </div>
              <div style={{ padding: '1.25rem', backgroundColor: cardBg, borderRadius: '0.5rem', border: `1px solid ${border}` }}>
                <p style={{ fontSize: '0.8rem', color: textSecondary, fontWeight: 600, marginBottom: '0.3rem' }}>OPEN</p>
                <p style={{ fontSize: '2rem', fontWeight: 800, color: '#F59E0B' }}>{filteredTickets?.filter(t => t.status !== 'Resolved').length || 0}</p>
              </div>
            </div>

            <div style={{ padding: '1.25rem', backgroundColor: cardBg, borderRadius: '0.5rem', border: `1px solid ${border}`, overflowX: 'auto' }}>
              <div style={{ marginBottom: '1rem' }}>
                <h4 style={{ fontWeight: 700, margin: '0 0 0.5rem 0', color: textPrimary }}>Tickets ({filteredTickets?.length || 0} total)</h4>
              </div>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', marginBottom: '1rem' }}>
                <thead>
                  <tr style={{ borderBottom: `1px solid ${border}` }}>
                    <th style={{ padding: '0.6rem', textAlign: 'left', fontWeight: 600, color: textPrimary }}>Ticket ID</th>
                    <th style={{ padding: '0.6rem', textAlign: 'left', fontWeight: 600, color: textPrimary }}>Category</th>
                    <th style={{ padding: '0.6rem', textAlign: 'left', fontWeight: 600, color: textPrimary }}>Priority</th>
                    <th style={{ padding: '0.6rem', textAlign: 'left', fontWeight: 600, color: textPrimary }}>Status</th>
                    <th style={{ padding: '0.6rem', textAlign: 'left', fontWeight: 600, color: textPrimary }}>Agent</th>
                    <th style={{ padding: '0.6rem', textAlign: 'left', fontWeight: 600, color: textPrimary }}>Rating</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTickets?.slice(analyticsPage * 10, (analyticsPage + 1) * 10).map((t, idx) => (
                    <tr key={idx} style={{ borderBottom: `1px solid ${isDarkMode ? '#1E293B' : '#F1F5F9'}` }}>
                      <td style={{ padding: '0.6rem', fontWeight: 600, color: '#06B6D4' }}>{t.ticket_id}</td>
                      <td style={{ padding: '0.6rem', color: textSecondary }}>{t.category}</td>
                      <td style={{ padding: '0.6rem' }}>
                        <span style={{ padding: '0.3rem 0.6rem', borderRadius: '0.3rem', fontSize: '0.75rem', fontWeight: 600, backgroundColor: t.priority === 'Critical' ? '#7F1D1D' : '#78350F', color: t.priority === 'Critical' ? '#FCA5A5' : '#FCD34D' }}>
                          {t.priority}
                        </span>
                      </td>
                      <td style={{ padding: '0.6rem', color: textSecondary }}>{t.status}</td>
                      <td style={{ padding: '0.6rem', color: textSecondary }}>{t.agent_id}</td>
                      <td style={{ padding: '0.6rem', color: textSecondary }}>{t.customer_rating ? `⭐ ${t.customer_rating}` : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {filteredTickets && Math.ceil((filteredTickets.length || 0) / 10) > 1 && (
                <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', alignItems: 'center' }}>
                  <button onClick={() => setAnalyticsPage(prev => Math.max(0, prev - 1))} disabled={analyticsPage === 0} style={{
                    padding: '0.4rem 0.6rem', backgroundColor: cardBg, border: `1px solid ${border}`, borderRadius: '0.3rem',
                    cursor: analyticsPage === 0 ? 'not-allowed' : 'pointer', color: textSecondary, fontSize: '0.75rem'
                  }}>
                    ← Prev
                  </button>
                  <span style={{ fontSize: '0.75rem', color: textSecondary }}>
                    {analyticsPage + 1} / {Math.ceil((filteredTickets.length || 0) / 10)}
                  </span>
                  <button onClick={() => setAnalyticsPage(prev => prev + 1)} disabled={analyticsPage >= Math.ceil((filteredTickets.length || 0) / 10) - 1} style={{
                    padding: '0.4rem 0.6rem', backgroundColor: cardBg, border: `1px solid ${border}`, borderRadius: '0.3rem',
                    cursor: analyticsPage >= Math.ceil((filteredTickets.length || 0) / 10) - 1 ? 'not-allowed' : 'pointer', color: textSecondary, fontSize: '0.75rem'
                  }}>
                    Next →
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
