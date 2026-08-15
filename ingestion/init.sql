CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.members (
    id BIGSERIAL PRIMARY KEY,
    batch_id UUID NOT NULL,
    payload JSONB NOT NULL,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_raw_members_payload ON raw.members USING gin (payload);
CREATE INDEX IF NOT EXISTS idx_raw_members_batch_id ON raw.members (batch_id);