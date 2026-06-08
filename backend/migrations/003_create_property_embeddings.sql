CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS public.property_embeddings (
    property_id TEXT PRIMARY KEY,
    embedding vector(1536) NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION public.match_property_embeddings(
    query_embedding vector(1536),
    match_count INT DEFAULT 50
)
RETURNS TABLE (
    property_id TEXT,
    similarity FLOAT
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        property_embeddings.property_id,
        1 - (property_embeddings.embedding <=> query_embedding) AS similarity
    FROM public.property_embeddings
    ORDER BY property_embeddings.embedding <=> query_embedding
    LIMIT COALESCE(match_count, 50);
$$;
