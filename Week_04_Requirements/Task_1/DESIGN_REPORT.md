# Requirements refinement network

## Architecture

`agentic_network.py` builds a LangGraph state graph with deterministic and LLM-backed
nodes. The loader recursively discovers `.txt` and `.md` files and stores each path
relative to the configured input directory. Documents are processed in batches of five,
with each document truncated at 100,000 characters.

The three LLM nodes are:

1. `extract_requirements`: extracts candidate requirements and their provenance.
2. `merge_duplicates`: performs semantic duplicate merging and records discarded items.
3. `review_quality`: checks contradictions, terminology, source coverage, and completeness.

Deterministic nodes load files, enforce API and iteration limits, validate required fields,
assign stable `REQ-###` identifiers, and render the final JSON document. A failed review
routes through `refine` back to duplicate merging. The loop is bounded by three refinement
iterations; unresolved findings are retained in `blacklist`.

## Specification mapping

| Specification | Implementation |
|---|---|
| ANS1 | Three LLM-invoking nodes listed above |
| ANS2 | Loader, validator, ID assignment, routing, and renderer |
| ANS3 | `review_quality -> refine -> merge_duplicates`, capped at three iterations |
| ANS4 | Configurable defaults use three distinct assignment models: `gpt-4o-mini`, `gpt-4.1-nano`, and `gpt-5-nano`; execution fails if the provider does not support one |
| ANS5 | `StateGraph` from LangGraph |
| OS1 | One JSON object with requirements, blacklist, priority scale, and review. Next, it is used to generate Markdown file for better readability. |
| OS2 | Deterministic `REQ-001`, `REQ-002`, ... IDs |
| OS3 | Semantic merge prompt and provenance-preserving merge node |
| OS4 | Relative `source_documents` paths |
| OS5 | Required `name` and paragraph `explanation` fields |
| OS6 | `Must`, `Should`, `Could`, `Won't` definitions in every output |
| OS7 | Review node checks contradictions and terminology |
| OS8 | Extraction is batched over every discovered supported document; review checks coverage |
| OS9 | Invalid, discarded, conflicting, and unresolved items are in `blacklist` with reasons |

## Limits and safety

Defaults are configurable in `NetworkConfig`: 100,000 characters per document, five
documents per batch, 50 API calls, three refinement iterations, and two retries for
transient API errors. The `.env` file is loaded by `python-dotenv`; its contents and the
API key are never printed, serialized, or committed.

## Commands

From `Week_04_Requirements/Task_1`:

```bash
python -m pip install langgraph langchain-openai python-dotenv pytest
python agentic_network.py data/corpus --output requirements.json
python agentic_network.py --connection-test
```

The limits can be overridden with `--max-document-size`, `--batch-size`,
`--max-api-calls`, `--max-refinement-iterations`, and `--transient-retries`.
The workflow writes `requirements.md` alongside `requirements.json` by default;
use `--markdown-output PATH` to select another Markdown path.

The workflow command requires a valid `OPENAI_API_KEY` and availability of all three
configured models. The connection-test command preserves the original `gpt-4o-mini`
smoke test independently of the workflow.
