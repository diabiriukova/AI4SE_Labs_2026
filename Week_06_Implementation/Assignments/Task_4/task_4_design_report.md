# Task 4 Design Report

## Matching mechanism

`retrieve_chunks.py` accepts a natural-language query, encodes it with the
same `all-MiniLM-L6-v2` model used in Task 3, and sends the resulting vector
to the existing persistent ChromaDB collection. It returns the stored chunk
text, source metadata, and distance.

The script imports Task 3's model, encoding, and collection helpers. It does
not generate or store embeddings for repository chunks again.

## Similarity and top-n retrieval

The Task 3 collection uses cosine distance, which compares the direction of
sentence-embedding vectors and is appropriate for semantic text matching.
ChromaDB returns results ordered from the smallest distance (most similar) to
the largest distance.

The number of results is configured with `--top-k`, for example:

```text
python3 retrieve_chunks.py "How is inventory reserved?" --top-k 3
```

The script limits the request to the number of records actually available.
Empty queries and non-positive values of `--top-k` are rejected.

## Limitations

Retrieval quality depends on the compact general-purpose embedding model and
the fixed line-based chunks created in Task 2. Results are limited to the
single local ChromaDB collection and no reranking or keyword filtering is
performed.
