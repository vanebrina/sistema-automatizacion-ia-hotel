-- Habilita la extensión pgvector al inicializar el contenedor de Postgres.
-- Necesaria para almacenar los embeddings del RAG (langchain-postgres / PGVector).
CREATE EXTENSION IF NOT EXISTS vector;
