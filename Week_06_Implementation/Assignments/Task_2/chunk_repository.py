
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterator

CHUNK_SIZE = 80
OVERLAP = 10
DEFAULT_ROOT = Path(
    "/Users/diana/matfyz/AI4SE_Labs_2026/Week_06_Implementation/AI4SE_Playground"
)
DEFAULT_OUTPUT = Path(
    "/Users/diana/matfyz/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_2/chunks.json"
)

TEXT_EXTENSIONS = {
    ".cfg",
    ".gitignore",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

EXCLUDED_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "env",
    "node_modules",
    "venv",
}

BINARY_EXTENSIONS = {
    ".7z",
    ".a",
    ".bmp",
    ".class",
    ".dll",
    ".dylib",
    ".eot",
    ".exe",
    ".gif",
    ".gz",
    ".ico",
    ".jpeg",
    ".jpg",
    ".mp3",
    ".mp4",
    ".pdf",
    ".png",
    ".pyc",
    ".so",
    ".tar",
    ".ttf",
    ".wav",
    ".webp",
    ".woff",
    ".woff2",
    ".zip",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help=f"repository root to scan (default: {DEFAULT_ROOT})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"JSON output path (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args()


def is_text_candidate(path: Path) -> bool:
    if path.name in {"chunks.json", "chunking_report.md"}:
        return False
    if path.name == ".gitignore":
        return True
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return False
    return path.suffix.lower() in TEXT_EXTENSIONS


def iter_files(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(root).parts
        if any(part in EXCLUDED_DIRECTORIES for part in relative_parts[:-1]):
            continue
        if is_text_candidate(path):
            yield path


def read_lines(path: Path) -> list[str] | None:
    try:
        raw = path.read_bytes()
        if b"\x00" in raw:
            return None
        return raw.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        return None


def language_for(path: Path) -> str:
    if path.name == ".gitignore":
        return "gitignore"
    return path.suffix.lower().lstrip(".") or "text"


def chunk_file(path: Path, root: Path) -> list[dict[str, object]]:
    lines = read_lines(path)
    if lines is None or not lines:
        return []

    relative_path = path.relative_to(root).as_posix()
    chunks: list[dict[str, object]] = []
    step = CHUNK_SIZE - OVERLAP
    for chunk_index, start in enumerate(range(0, len(lines), step)):
        chunk_lines = lines[start : start + CHUNK_SIZE]
        chunks.append(
            {
                "file_path": relative_path,
                "chunk_index": chunk_index,
                "start_line": start + 1,
                "end_line": start + len(chunk_lines),
                "language": language_for(path),
                "content": "\n".join(chunk_lines),
            }
        )
        if start + CHUNK_SIZE >= len(lines):
            break
    return chunks


def build_chunks(root: Path) -> list[dict[str, object]]:
    chunks: list[dict[str, object]] = []
    for path in iter_files(root):
        chunks.extend(chunk_file(path, root))
    return chunks


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    chunks = build_chunks(root)
    output.write_text(json.dumps(chunks, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    files = len({chunk["file_path"] for chunk in chunks})
    print(f"Processed {files} files into {len(chunks)} chunks: {output}")


if __name__ == "__main__":
    main()
