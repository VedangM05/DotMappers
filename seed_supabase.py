import os
import sys
import json
import logging
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import CSV_FILE_PATH, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_KEY
from src.embeddings import generate_batch_embeddings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_supabase")

def main():
    key = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY
    if not SUPABASE_URL or not key or "your-project-id" in SUPABASE_URL:
        logger.error("Please configure valid SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env file.")
        return

    try:
        from supabase import create_client
        client = create_client(SUPABASE_URL, key)
        logger.info(f"Connected to Supabase Cloud project: {SUPABASE_URL}")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return

    # Check table existence
    try:
        res = client.table('tickets').select('ticket_id', count='exact').limit(1).execute()
        logger.info(f"Current tickets in Supabase Cloud: {res.count}")
    except Exception as e:
        logger.error("Could not find table 'public.tickets' on Supabase Cloud!")
        logger.info("Please open your Supabase Dashboard -> SQL Editor and run 'supabase/migrations/20260916_init_schema.sql' first.")
        return

    logger.info("Reading support_tickets.csv and generating 384-dim vector embeddings...")
    df = pd.read_csv(CSV_FILE_PATH)
    summaries = df['issue_summary'].tolist()
    embeddings = generate_batch_embeddings(summaries)

    logger.info(f"Uploading {len(df)} records to Supabase Cloud PostgreSQL...")
    batch_size = 50
    records = []
    
    for idx, row in df.iterrows():
        resol_time = None if pd.isna(row['resolution_time_hrs']) else float(row['resolution_time_hrs'])
        cust_rating = None if pd.isna(row['customer_rating']) else float(row['customer_rating'])
        
        records.append({
            "ticket_id": str(row['ticket_id']),
            "created_at": str(row['created_at']),
            "category": str(row['category']),
            "priority": str(row['priority']),
            "status": str(row['status']),
            "response_time_hrs": float(row['response_time_hrs']),
            "resolution_time_hrs": resol_time,
            "agent_id": str(row['agent_id']),
            "customer_rating": cust_rating,
            "issue_summary": str(row['issue_summary']),
            "issue_embedding": embeddings[idx]
        })

    # Batch upsert
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        client.table('tickets').upsert(batch).execute()
        logger.info(f"Uploaded batch {i // batch_size + 1} / {(len(records) + batch_size - 1) // batch_size} ({i + len(batch)} / {len(records)} records)")

    logger.info("✅ Supabase Cloud Ingestion Completed! All 500 tickets and vector embeddings are live.")

if __name__ == "__main__":
    main()
