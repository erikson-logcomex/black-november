-- Migration: create deal_notifications table
CREATE TABLE IF NOT EXISTS deal_notifications (
  id TEXT PRIMARY KEY,
  deal_name TEXT,
  amount NUMERIC,
  owner_name TEXT,
  sdr_name TEXT,
  ldr_name TEXT,
  company_name TEXT,
  pipeline TEXT,
  deal_stage TEXT,
  payload JSONB,
  created_at TIMESTAMPTZ DEFAULT now(),
  viewed_by TEXT[] DEFAULT ARRAY[]::text[]
);

-- Index on created_at for fast ordering
CREATE INDEX IF NOT EXISTS idx_deal_notifications_created_at ON deal_notifications (created_at DESC);

-- Optional: index for viewed_by membership (GIN)
CREATE INDEX IF NOT EXISTS idx_deal_notifications_viewed_by ON deal_notifications USING GIN (viewed_by);
