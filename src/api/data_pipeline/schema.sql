-- Enable pgvector extension if not already enabled
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS articles (
    articles_id SERIAL PRIMARY KEY,
    link_name TEXT,
    title TEXT,
    link TEXT NOT NULL,
    published TIMESTAMP,
    summary TEXT,
    authors TEXT[],
    tags TEXT[],
    embedding vector(512)  -- replace 1536 with your embedding dimension
);
