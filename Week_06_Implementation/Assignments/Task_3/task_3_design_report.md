# Task 3 Design Report

## Embedding model

The implementation uses `sentence-transformers` with
`all-MiniLM-L6-v2`. It is a compact, general-purpose sentence embedding model
that produces 384-dimensional vectors, which is sufficient for this small
code repository while keeping local inference relatively lightweight.

## Embedded content

The complete `content` field of every Task 2 chunk is embedded. The original
file path, line range, language, and chunk index are stored as metadata rather
than added to the text, so retrieved results preserve source-location
information without changing the semantic input.

## Vector storage

ChromaDB is used with `PersistentClient`, storing data under `chroma_db/`.
ChromaDB provides local persistence and nearest-neighbor querying without
requiring a separate service. The collection is configured with cosine
distance, which is appropriate for sentence-transformer vectors.

Chunk IDs are deterministic (`file_path::chunk_index`). Indexing uses
`upsert`, so rerunning the script updates existing records instead of
creating duplicates.

## Similarity search

The query is encoded with the same model as the chunks. ChromaDB returns the
requested number of nearest chunks, including their text, metadata, and cosine
distance. Lower distance indicates greater similarity.

