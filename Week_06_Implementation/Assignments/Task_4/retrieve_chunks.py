#!/usr/bin/env python3
"""Retrieve the most relevant repository chunks for a natural-language query."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

TASK_3_DIRECTORY = Path(__file__).resolve().parents[1] / "Task_3"
if str(TASK_3_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(TASK_3_DIRECTORY))

from embedding_store import DEFAULT_DATABASE, create_model, encode, get_collection


def retrieve_chunks(
    query: str,
    top_k: int = 5,
    database: Path = DEFAULT_DATABASE,
    model: Any | None = None,
) -> list[dict[str, Any]]:
    """Return up to ``top_k`` stored chunks ranked by cosine distance."""
    if not query.strip():
        raise ValueError("query must not be empty")
    if top_k < 1:
        raise ValueError("top_k must be positive")

    model = model or create_model()
    query_embedding = encode(model, [query])[0]
    collection = get_collection(database)
    available = collection.count()
    if available == 0:
        return []

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, available),
        include=["documents", "metadatas", "distances"],
    )
    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]
    return [
        {
            "content": document,
            "metadata": metadata,
            "distance": distance,
        }
        for document, metadata, distance in zip(documents, metadatas, distances)
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="natural-language task or question")
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="maximum number of chunks to retrieve (default: 5)",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE,
        help=f"Task 3 ChromaDB directory (default: {DEFAULT_DATABASE})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = retrieve_chunks(args.query, args.top_k, args.database)
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
