-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Main articles table
CREATE TABLE IF NOT EXISTS articles (
    id              SERIAL PRIMARY KEY,
    article_number  INTEGER NOT NULL UNIQUE,
    title           TEXT NOT NULL,
    source_url      TEXT,
    phase           INTEGER NOT NULL,
    phase_name      TEXT NOT NULL,
    themes          TEXT[],
    summary         TEXT,
    key_excerpts    TEXT[],
    annotations     TEXT,
    date_captured   DATE,
    embedding       vector(384),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- IVFFlat index for cosine similarity search (lists=10 suitable for ~90-500 rows)
CREATE INDEX IF NOT EXISTS articles_embedding_idx
    ON articles
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);

-- Fast filtering indexes
CREATE INDEX IF NOT EXISTS articles_phase_idx ON articles (phase);
CREATE INDEX IF NOT EXISTS articles_number_idx ON articles (article_number);

-- Auto-update updated_at on row modification
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_articles_updated_at ON articles;
CREATE TRIGGER update_articles_updated_at
    BEFORE UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
