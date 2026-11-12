from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
COLLECTION_NAME = "repository_chunks"
DEFAULT_CHUNKS = Path(
    "/Users/diana/matfyz/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_2/chunks.json"
)
DEFAULT_DATABASE = Path(
    "/Users/diana/matfyz/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_3/chroma_db"
)


def load_dependencies() -> tuple[Any, Any]:
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "Task 3 requires sentence-transformers and chromadb. "
            "Install them with: python3 -m pip install sentence-transformers chromadb"
        ) from exc
    return chromadb, SentenceTransformer


def load_chunks(path: Path) -> list[dict[str, Any]]:
    chunks = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(chunks, list):
        raise ValueError(f"Expected a JSON array in {path}")
    required = {"file_path", "chunk_index", "start_line", "end_line", "language", "content"}
    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, dict) or not required.issubset(chunk):
            raise ValueError(f"Chunk {index} is missing required metadata")
    return chunks


def chunk_id(chunk: dict[str, Any]) -> str:
    return f"{chunk['file_path']}::{chunk['chunk_index']}"


def create_model() -> Any:
    _, sentence_transformer = load_dependencies()
    return sentence_transformer(MODEL_NAME)


def encode(model: Any, texts: list[str]) -> list[list[float]]:
    vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    result = vectors.tolist() if hasattr(vectors, "tolist") else vectors
    if len(result) != len(texts) or any(len(vector) != EMBEDDING_DIMENSION for vector in result):
        raise ValueError(f"Expected {EMBEDDING_DIMENSION}-dimensional embeddings")
    return result


def get_collection(database: Path) -> Any:
    chromadb, _ = load_dependencies()
    client = chromadb.PersistentClient(path=str(database))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def index_chunks(
    chunks_path: Path = DEFAULT_CHUNKS,
    database: Path = DEFAULT_DATABASE,
    model: Any | None = None,
) -> int:
    chunks = load_chunks(chunks_path)
    model = model or create_model()
    embeddings = encode(model, [chunk["content"] for chunk in chunks])
    collection = get_collection(database)
    collection.upsert(
        ids=[chunk_id(chunk) for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=embeddings,
        metadatas=[
            {
                "file_path": chunk["file_path"],
                "chunk_index": chunk["chunk_index"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
                "language": chunk["language"],
            }
            for chunk in chunks
        ],
    )
    return len(chunks)


def search_chunks(
    query: str,
    database: Path = DEFAULT_DATABASE,
    top_k: int = 5,
    model: Any | None = None,
) -> list[dict[str, Any]]:
    if top_k < 1:
        raise ValueError("top_k must be positive")
    model = model or create_model()
    collection = get_collection(database)
    query_embedding = encode(model, [query])[0]
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]
    return [
        {"content": document, "metadata": metadata, "distance": distance}
        for document, metadata, distance in zip(documents, metadatas, distances)
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--query", help="search the indexed chunks instead of indexing")
    parser.add_argument("--top-k", type=int, default=5)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.query:
        results = search_chunks(args.query, args.database, args.top_k)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        count = index_chunks(args.chunks, args.database)
        print(f"Indexed {count} chunks in {args.database}")


if __name__ == "__main__":
    main()
