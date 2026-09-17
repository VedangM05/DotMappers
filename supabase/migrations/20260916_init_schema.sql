-- Enable pgvector extension for RAG vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Define support tickets table schema
CREATE TABLE IF NOT EXISTS public.tickets (
    ticket_id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    response_time_hrs REAL NOT NULL,
    resolution_time_hrs REAL NULL,
    agent_id TEXT NOT NULL,
    customer_rating REAL NULL,
    issue_summary TEXT NOT NULL,
    issue_embedding vector(384) NULL  -- pgvector embedding column for MiniLM
);

-- Index for fast vector similarity search using cosine distance
CREATE INDEX IF NOT EXISTS tickets_issue_embedding_idx 
ON public.tickets 
USING ivfflat (issue_embedding vector_cosine_ops) 
WITH (lists = 10);

-- Indexes for fast query filtering
CREATE INDEX IF NOT EXISTS idx_tickets_status ON public.tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON public.tickets(priority);
CREATE INDEX IF NOT EXISTS idx_tickets_category ON public.tickets(category);
CREATE INDEX IF NOT EXISTS idx_tickets_agent ON public.tickets(agent_id);

-- Enable Row Level Security (RLS) on tickets table
ALTER TABLE public.tickets ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if re-running
DROP POLICY IF EXISTS "Admin full access policy" ON public.tickets;
DROP POLICY IF EXISTS "Agent ticket access policy" ON public.tickets;
DROP POLICY IF EXISTS "Anon public read policy" ON public.tickets;

-- Policy 1: Admin / Service Role Full Access
CREATE POLICY "Admin full access policy" 
ON public.tickets 
FOR ALL 
TO service_role 
USING (true);

-- Policy 2: Authenticated Agent Scoped Access
CREATE POLICY "Agent ticket access policy" 
ON public.tickets 
FOR SELECT 
TO authenticated 
USING (
  agent_id = current_setting('request.jwt.claims', true)::json->>'agent_id'
  OR current_setting('request.jwt.claims', true)::json->>'role' = 'admin'
);

-- Policy 3: Anonymous Public Read Access (Restricted: cannot view Escalated tickets)
CREATE POLICY "Anon public read policy" 
ON public.tickets 
FOR SELECT 
TO anon 
USING (status != 'Escalated');

-- RPC Function for pgvector similarity search
CREATE OR REPLACE FUNCTION match_tickets (
  query_embedding vector(384),
  match_threshold float DEFAULT 0.0,
  match_count int DEFAULT 5
)
RETURNS TABLE (
  ticket_id text,
  created_at timestamptz,
  category text,
  priority text,
  status text,
  response_time_hrs real,
  resolution_time_hrs real,
  agent_id text,
  customer_rating real,
  issue_summary text,
  similarity float
)
LANGUAGE sql STABLE
AS $$
  SELECT
    t.ticket_id,
    t.created_at,
    t.category,
    t.priority,
    t.status,
    t.response_time_hrs,
    t.resolution_time_hrs,
    t.agent_id,
    t.customer_rating,
    t.issue_summary,
    1 - (t.issue_embedding <=> query_embedding) AS similarity
  FROM public.tickets t
  WHERE t.issue_embedding IS NOT NULL
    AND (1 - (t.issue_embedding <=> query_embedding)) >= match_threshold
  ORDER BY t.issue_embedding <=> query_embedding
  LIMIT match_count;
$$;
