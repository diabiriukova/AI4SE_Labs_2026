# Repository Chunking Report

## 1. Overview

`chunk_repository.py` is a standard-library-only Python utility for preparing
repository text for a future RAG retrieval stage. It recursively scans the
repository, filters readable source and documentation files, splits each file
into overlapping line-based chunks, and writes the result to `chunks.json`.

The implementation does not create embeddings, use a vector database, perform
similarity search, or integrate with an LLM.

## 2. Selected chunk size

- Target size: **80 lines**
- Maximum chunk size: **80 lines**
- Small final chunks are retained rather than padded or discarded.

Eighty lines provides enough local context for Python functions, classes, and
tests while keeping individual retrieval records manageable. A line-based
limit also avoids adding a tokenizer dependency.

## 3. Splitting method

Files are split using a sliding window over `splitlines()` output. Each chunk
starts and ends on an original line boundary. The last chunk in a file ends at
the file's final non-newline line.

This preserves readable source structure and makes the original location
unambiguous.

## 4. Overlap strategy

Adjacent chunks overlap by **10 lines**, giving a step size of 70 lines.
Overlap preserves nearby imports, decorators, method boundaries, and related
context when a definition crosses a chunk boundary. The final chunk is not
duplicated once the preceding chunk already reaches the end of the file.

## 5. Storage structure and metadata

`chunks.json` contains a readable JSON array. Each record includes:

- `file_path`: repository-relative POSIX path
- `chunk_index`: zero-based index within the file
- `start_line`: one-based original starting line
- `end_line`: one-based original ending line
- `language`: inferred from the file extension
- `content`: exact chunk text

## 6. Excluded files and directories

The scanner excludes:

- Git metadata: `.git`
- Virtual environments: `.venv`, `venv`, `env`
- Caches: `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`
- Build and dependency outputs: `build`, `dist`, `*.egg-info`, `.tox`, `.nox`,
  `node_modules`
- Common binary formats, compiled files, archives, media, fonts, and PDFs
- Files containing NUL bytes or invalid UTF-8
- Generated outputs: `chunks.json` and `chunking_report.md`

Relevant text extensions currently include Python, Markdown, plain text, JSON,
YAML, TOML, INI, CFG, and `.gitignore`.

