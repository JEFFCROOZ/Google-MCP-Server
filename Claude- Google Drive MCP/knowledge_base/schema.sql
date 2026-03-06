-- Knowledge Base schema
-- Uses PostgreSQL built-in full-text search (no extensions required)
-- search_vector is maintained via trigger (to_tsvector is STABLE, not IMMUTABLE,
-- so it cannot be used in a GENERATED ALWAYS AS column directly)

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
    search_vector   tsvector,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- GIN index for fast full-text search
CREATE INDEX IF NOT EXISTS articles_search_idx  ON articles USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS articles_phase_idx   ON articles (phase);
CREATE INDEX IF NOT EXISTS articles_number_idx  ON articles (article_number);

-- Trigger function: update search_vector and updated_at on every INSERT or UPDATE
CREATE OR REPLACE FUNCTION articles_tsvector_trigger()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english',
        coalesce(NEW.title, '') || ' ' ||
        coalesce(NEW.phase_name, '') || ' ' ||
        coalesce(array_to_string(NEW.themes, ' '), '') || ' ' ||
        coalesce(NEW.summary, '') || ' ' ||
        coalesce(NEW.annotations, '')
    );
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS articles_tsvector_update ON articles;
CREATE TRIGGER articles_tsvector_update
    BEFORE INSERT OR UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION articles_tsvector_trigger();
