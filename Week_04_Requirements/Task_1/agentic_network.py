"""LangGraph network for refining a text corpus into structured requirements.

The network deliberately keeps document loading, limits, validation, ID assignment,
and rendering deterministic. LLM nodes are responsible for extraction, semantic
merging, and quality review.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

from openai import APIConnectionError, APITimeoutError, RateLimitError
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

SUPPORTED_EXTENSIONS = {".txt", ".md"}
DEFAULT_MAX_DOCUMENT_SIZE = 100_000
DEFAULT_BATCH_SIZE = 5
DEFAULT_MAX_API_CALLS = 50
DEFAULT_MAX_REFINEMENT_ITERATIONS = 3
DEFAULT_TRANSIENT_RETRIES = 2
PRIORITY_DEFINITIONS = {
    "Must": "Required for the system to be acceptable; without it, a core objective fails.",
    "Should": "Important and expected, but a justified implementation workaround is possible.",
    "Could": "Useful enhancement that may be deferred without blocking acceptance.",
    "Won't": "Explicitly out of scope for this release; retain it for traceability.",
}


class NetworkState(TypedDict, total=False):
    input_dir: str
    documents: list[dict[str, str]]
    candidates: list[dict[str, Any]]
    requirements: list[dict[str, Any]]
    blacklist: list[dict[str, Any]]
    review: dict[str, Any]
    terminology: list[str]
    retry_count: int
    api_calls: int
    output: dict[str, Any]
    error: str
    _max_api_calls: int


@dataclass(frozen=True)
class NetworkConfig:
    max_document_size: int = DEFAULT_MAX_DOCUMENT_SIZE
    batch_size: int = DEFAULT_BATCH_SIZE
    max_api_calls: int = DEFAULT_MAX_API_CALLS
    max_refinement_iterations: int = DEFAULT_MAX_REFINEMENT_ITERATIONS
    transient_retries: int = DEFAULT_TRANSIENT_RETRIES
    extraction_model: str = "gpt-4o-mini"
    merge_model: str = "gpt-4.1-nano"
    review_model: str = "gpt-5-nano"


def load_documents(input_dir: str, max_document_size: int = DEFAULT_MAX_DOCUMENT_SIZE) -> list[dict[str, str]]:
    """Read supported files recursively and retain paths relative to input_dir."""
    root = Path(input_dir).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    documents = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS):
        relative_path = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_document_size:
            text = text[:max_document_size]
        documents.append({"path": relative_path, "text": text})
    if not documents:
        raise ValueError(f"No supported .txt or .md documents found under {root}")
    return documents


def _parse_json(content: Any) -> Any:
    text = content.content if hasattr(content, "content") else content
    if not isinstance(text, str):
        raise ValueError("LLM response was not text")
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    return json.loads(fenced.group(1) if fenced else text)


def _invoke_with_retries(
    model: Any,
    prompt: str,
    retries: int,
    state: NetworkState,
) -> Any:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            state["api_calls"] = state.get("api_calls", 0) + 1
            if state["api_calls"] > state.get("_max_api_calls", DEFAULT_MAX_API_CALLS):
                raise RuntimeError("Maximum API call budget exceeded")
            return _parse_json(model.invoke(prompt))
        except (ValueError, json.JSONDecodeError, OSError, RuntimeError, APIConnectionError, APITimeoutError, RateLimitError) as exc:
            last_error = exc
            if attempt == retries:
                break
            time.sleep(0.2 * (attempt + 1))
    raise RuntimeError(f"LLM invocation failed after {retries + 1} attempts: {last_error}") from last_error


def _extract_node(state: NetworkState, model: Any, config: NetworkConfig) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for start in range(0, len(state["documents"]), config.batch_size):
        batch = state["documents"][start : start + config.batch_size]
        prompt = (
            "Extract every distinct software requirement from these source documents. "
            "Do not invent facts. Return JSON array only; each item must contain name, "
            "explanation (one paragraph), priority (Must/Should/Could/Won't), and source_documents.\n"
            f"Documents:\n{json.dumps(batch, ensure_ascii=False)}"
        )
        result = _invoke_with_retries(model, prompt, config.transient_retries, state)
        if not isinstance(result, list):
            raise ValueError("Extraction response must be a JSON array")
        candidates.extend(result)
    return {"candidates": candidates}


def _merge_node(state: NetworkState, model: Any, config: NetworkConfig) -> dict[str, Any]:
    prompt = (
        "Semantically merge duplicate requirements, preserving all source_documents. "
        "Do not merge requirements with different behavior or conflicting constraints. "
        "Return JSON object with requirements (array) and blacklist (array). Each requirement "
        "must have name, explanation, priority, source_documents. Each blacklist item must "
        "have candidate, reason, source_documents.\nCandidates:\n"
        + json.dumps(state.get("candidates", []), ensure_ascii=False)
    )
    result = _invoke_with_retries(model, prompt, config.transient_retries, state)
    if not isinstance(result, dict) or not isinstance(result.get("requirements"), list):
        raise ValueError("Merge response must contain a requirements array")
    return {"requirements": result["requirements"], "blacklist": result.get("blacklist", [])}


def _review_node(state: NetworkState, model: Any, config: NetworkConfig) -> dict[str, Any]:
    prompt = (
        "Review these requirements against their source candidates. Find contradictions, "
        "inconsistent terminology, missing source coverage, and incomplete explanations. "
        "Return JSON object with pass (boolean), issues (array of strings), terminology "
        "(array of canonical terms), and unresolved (array of objects with candidate, reason, "
        "source_documents).\nRequirements:\n"
        + json.dumps(state.get("requirements", []), ensure_ascii=False)
        + "\nCandidates:\n"
        + json.dumps(state.get("candidates", []), ensure_ascii=False)
    )
    result = _invoke_with_retries(model, prompt, config.transient_retries, state)
    if not isinstance(result, dict):
        raise ValueError("Review response must be a JSON object")
    return {"review": result, "terminology": result.get("terminology", [])}


def _assign_ids_and_validate(state: NetworkState) -> dict[str, Any]:
    requirements = []
    blacklist = list(state.get("blacklist", []))
    for number, item in enumerate(state.get("requirements", []), 1):
        required = ("name", "explanation", "priority", "source_documents")
        if not all(item.get(field) for field in required) or item["priority"] not in PRIORITY_DEFINITIONS:
            blacklist.append({"candidate": item, "reason": "Missing or invalid required fields.", "source_documents": item.get("source_documents", [])})
            continue
        requirements.append({
            "id": f"REQ-{number:03d}",
            "name": str(item["name"]).strip(),
            "explanation": str(item["explanation"]).strip(),
            "priority": item["priority"],
            "source_documents": sorted(set(item["source_documents"])),
        })
    return {"requirements": requirements, "blacklist": blacklist}


def _review_route(state: NetworkState, config: NetworkConfig) -> str:
    review = state.get("review", {})
    if review.get("pass", False) or state.get("retry_count", 0) >= config.max_refinement_iterations:
        return "finalize"
    return "refine"


def _refine_node(state: NetworkState) -> dict[str, Any]:
    return {"retry_count": state.get("retry_count", 0) + 1, "candidates": state.get("candidates", [])}


def _finalize_node(state: NetworkState) -> dict[str, Any]:
    review = state.get("review", {})
    blacklist = list(state.get("blacklist", []))
    blacklist.extend(review.get("unresolved", []))
    return {"output": {
        "priority_scale": PRIORITY_DEFINITIONS,
        "requirements": state.get("requirements", []),
        "blacklist": blacklist,
        "quality_review": {
            "passed": bool(review.get("pass", False)),
            "issues": review.get("issues", []),
            "terminology": state.get("terminology", []),
            "refinement_iterations": state.get("retry_count", 0),
        },
    }}


def _markdown_text(output: dict[str, Any]) -> str:
    """Render the validated final output without invoking the LLMs again."""

    def inline(value: Any) -> str:
        return str(value).replace("\\", "\\\\").replace("`", "\\`").replace("\n", " ")

    def sources(value: Any) -> str:
        if not value:
            return "Unavailable"
        return ", ".join(f"`{inline(source)}`" for source in value)

    lines = [
        "# Software Requirements",
        "",
        "This document contains the accepted requirements and rejected or unresolved "
        "candidates produced from the configured source corpus.",
        "",
        "## Priority scale",
        "",
    ]
    for priority, definition in output.get("priority_scale", {}).items():
        lines.append(f"- **{inline(priority)}** — {inline(definition)}")

    lines.extend(["", "## Accepted requirements", ""])
    requirements = output.get("requirements", [])
    if not requirements:
        lines.append("No accepted requirements were produced.")
    for requirement in requirements:
        requirement_id = inline(requirement.get("id", "Unavailable"))
        name = inline(requirement.get("name", "Unnamed requirement"))
        lines.extend([
            f"### {requirement_id}: {name}",
            "",
            f"**Priority:** {inline(requirement.get('priority', 'Unavailable'))}",
        ])
        if requirement.get("priority_justification"):
            lines.append(f"**Priority justification:** {inline(requirement['priority_justification'])}")
        lines.extend([
            "",
            inline(requirement.get("explanation", "Explanation unavailable.")),
            "",
            f"**Source documents:** {sources(requirement.get('source_documents'))}",
            "",
        ])

    lines.extend(["## Blacklist", ""])
    blacklist = output.get("blacklist", [])
    if not blacklist:
        lines.append("No discarded or unresolved candidates were recorded.")
    for number, item in enumerate(blacklist, 1):
        if isinstance(item, dict):
            candidate = item.get("candidate", "Unavailable")
            reason = item.get("reason", "Reason unavailable.")
            item_sources = item.get("source_documents")
        else:
            candidate = item
            reason = "Reason unavailable."
            item_sources = None
        if isinstance(candidate, (dict, list)):
            candidate_text = json.dumps(candidate, ensure_ascii=False, sort_keys=True)
        else:
            candidate_text = str(candidate)
        lines.extend([
            f"### Candidate {number}",
            "",
            f"**Candidate:** {inline(candidate_text)}",
            f"**Reason:** {inline(reason)}",
            f"**Source documents:** {sources(item_sources)}",
            "",
        ])

    quality_review = output.get("quality_review")
    if quality_review:
        lines.extend([
            "## Processing summary",
            "",
            f"- **Quality review passed:** {quality_review.get('passed', 'Unavailable')}",
            f"- **Refinement iterations:** {quality_review.get('refinement_iterations', 'Unavailable')}",
            f"- **Accepted requirements:** {len(requirements)}",
            f"- **Blacklisted candidates:** {len(blacklist)}",
        ])
        issues = quality_review.get("issues")
        if issues:
            lines.append(f"- **Quality review issues:** {'; '.join(inline(issue) for issue in issues)}")
        lines.append("")
    return "\n".join(lines)


def write_outputs(output: dict[str, Any], json_path: str, markdown_path: str | None = None) -> tuple[Path, Path]:
    """Write JSON and Markdown representations of the same final result."""
    json_file = Path(json_path)
    markdown_file = Path(markdown_path) if markdown_path else json_file.with_suffix(".md")
    try:
        json_file.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        markdown_file.write_text(_markdown_text(output), encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(
            f"Could not write output files '{json_file}' and '{markdown_file}': {exc}"
        ) from exc
    return json_file, markdown_file


def build_graph(config: NetworkConfig | None = None, models: dict[str, Any] | None = None):
    config = config or NetworkConfig()
    models = models or {
        "extract": ChatOpenAI(model=config.extraction_model, temperature=0),
        "merge": ChatOpenAI(model=config.merge_model, temperature=0),
        "review": ChatOpenAI(model=config.review_model, temperature=0),
    }

    def load_node(state: NetworkState) -> dict[str, Any]:
        documents = load_documents(state["input_dir"], config.max_document_size)
        return {"documents": documents, "retry_count": 0, "api_calls": 0, "_max_api_calls": config.max_api_calls}

    def extract(state: NetworkState) -> dict[str, Any]:
        return _extract_node(state, models["extract"], config)

    def merge(state: NetworkState) -> dict[str, Any]:
        return _merge_node(state, models["merge"], config)

    def review(state: NetworkState) -> dict[str, Any]:
        return _review_node(state, models["review"], config)

    graph = StateGraph(NetworkState)
    graph.add_node("load_documents", load_node)
    graph.add_node("extract_requirements", extract)
    graph.add_node("merge_duplicates", merge)
    graph.add_node("validate_structure", _assign_ids_and_validate)
    graph.add_node("review_quality", review)
    graph.add_node("refine", _refine_node)
    graph.add_node("finalize", _finalize_node)
    graph.add_edge(START, "load_documents")
    graph.add_edge("load_documents", "extract_requirements")
    graph.add_edge("extract_requirements", "merge_duplicates")
    graph.add_edge("merge_duplicates", "validate_structure")
    graph.add_edge("validate_structure", "review_quality")
    graph.add_conditional_edges("review_quality", lambda state: _review_route(state, config), {"refine": "refine", "finalize": "finalize"})
    graph.add_edge("refine", "merge_duplicates")
    graph.add_edge("finalize", END)
    return graph.compile()


def run(
    input_dir: str,
    output_path: str,
    config: NetworkConfig | None = None,
    models: dict[str, Any] | None = None,
    markdown_output_path: str | None = None,
) -> dict[str, Any]:
    graph = build_graph(config, models)
    result = graph.invoke({"input_dir": input_dir})
    output = result["output"]
    write_outputs(output, output_path, markdown_output_path)
    return output


def test_openai_connection() -> None:
    """Preserve the original connection check without printing credentials."""
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("API key not found. Check that your .env file exists.")
    response = ChatOpenAI(model="gpt-4o-mini", temperature=0).invoke(
        "Reply with exactly: OpenAI connection successful"
    )
    print(response.content)


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", nargs="?")
    parser.add_argument("-o", "--output", default="requirements.json")
    parser.add_argument("--markdown-output", default=None)
    parser.add_argument("--connection-test", action="store_true")
    parser.add_argument("--max-document-size", type=int, default=DEFAULT_MAX_DOCUMENT_SIZE)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--max-api-calls", type=int, default=DEFAULT_MAX_API_CALLS)
    parser.add_argument("--max-refinement-iterations", type=int, default=DEFAULT_MAX_REFINEMENT_ITERATIONS)
    parser.add_argument("--transient-retries", type=int, default=DEFAULT_TRANSIENT_RETRIES)
    args = parser.parse_args()
    if args.connection_test:
        test_openai_connection()
        return
    if not args.input_dir:
        parser.error("input_dir is required unless --connection-test is used")
    config = NetworkConfig(
        max_document_size=args.max_document_size,
        batch_size=args.batch_size,
        max_api_calls=args.max_api_calls,
        max_refinement_iterations=args.max_refinement_iterations,
        transient_retries=args.transient_retries,
    )
    markdown_path = args.markdown_output or str(Path(args.output).with_suffix(".md"))
    run(args.input_dir, args.output, config, markdown_output_path=markdown_path)
    print(f"Wrote requirements JSON to {args.output}")
    print(f"Wrote requirements Markdown to {markdown_path}")


if __name__ == "__main__":
    main()
