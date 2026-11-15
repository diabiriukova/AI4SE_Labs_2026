#!/usr/bin/env python3
"""Implement missing repository methods with retrieval-augmented LLM prompts."""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shutil
import sys
import textwrap
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

ASSIGNMENTS_ROOT = Path(__file__).resolve().parents[1]
WEEK_ROOT = ASSIGNMENTS_ROOT.parent
PROJECT_ROOT = WEEK_ROOT / "AI4SE_Playground"
TASKS_PATH = ASSIGNMENTS_ROOT / "missing_code.json"
TASK_4_ROOT = ASSIGNMENTS_ROOT / "Task_4"
DEFAULT_DATABASE = ASSIGNMENTS_ROOT / "Task_3" / "chroma_db"
DEFAULT_MODEL = "gpt-4o-mini"
ALLOWED_MODELS = {
    "gpt-6-luna",
    "gpt-5.6-luna",
    "gpt-5.4-nano",
    "gpt-5-nano",
    "gpt-5-mini",
    "gpt-4.1-nano",
    "gpt-4o-mini",
}

if str(TASK_4_ROOT) not in sys.path:
    sys.path.insert(0, str(TASK_4_ROOT))

from retrieve_chunks import retrieve_chunks


def load_tasks(path: Path = TASKS_PATH) -> list[dict[str, str]]:
    tasks = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(tasks, list):
        raise ValueError(f"Expected a JSON array in {path}")
    required = {"file", "class", "method", "docstring"}
    for index, task in enumerate(tasks):
        if not isinstance(task, dict) or not required.issubset(task):
            raise ValueError(f"Task {index} is missing required fields")
    return tasks


def find_method(source: str, class_name: str, method_name: str) -> ast.FunctionDef:
    tree = ast.parse(source)
    matches = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == method_name
        and any(
            isinstance(parent, ast.ClassDef) and parent.name == class_name
            for parent in ast.walk(tree)
            if isinstance(parent, ast.ClassDef) and node in parent.body
        )
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one {class_name}.{method_name}, found {len(matches)}"
        )
    return matches[0]


def extract_response_json(content: str) -> dict[str, Any]:
    fenced = re.search(r"```(?:json)?\s*(.*?)```", content, re.DOTALL)
    payload = fenced.group(1) if fenced else content
    result = json.loads(payload)
    if not isinstance(result, dict) or not isinstance(result.get("method_code"), str):
        raise ValueError("LLM response must be JSON with a string 'method_code'")
    return result


def validate_method_code(code: str, method_name: str) -> str:
    code = textwrap.dedent(code).strip("\n")
    parsed = ast.parse(code)
    methods = [
        node
        for node in parsed.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    if len(methods) != 1 or methods[0].name != method_name:
        raise ValueError(f"Generated code must contain exactly one method named {method_name}")
    return code


def build_prompt(task: dict[str, str], chunks: list[dict[str, Any]]) -> str:
    context = "\n\n".join(
        f"--- {item['metadata'].get('file_path')}:{item['metadata'].get('start_line')}"
        f"-{item['metadata'].get('end_line')} ---\n{item['content']}"
        for item in chunks
    )
    return f"""Implement exactly one missing Python method.

Task description: {task['docstring']}
Target file: {task['file']}
Target class: {task['class']}
Target method: {task['method']}

Use the retrieved repository context below. Follow existing conventions,
reuse existing helpers, and implement only the requested method. Return JSON
only in this exact shape: {{"method_code": "<complete Python method>"}}
The method_code value must contain a complete method definition named
{task['method']}. Do not include imports, explanations, or changes to other
methods.

Retrieved context:
{context}
"""


def create_client() -> Any:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The OpenAI client is required. Install it with: "
            "python3 -m pip install openai python-dotenv"
        ) from exc
    load_dotenv(WEEK_ROOT / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY was not found in the project .env file")
    model = os.getenv("TASK5_MODEL", DEFAULT_MODEL)
    if model not in ALLOWED_MODELS:
        raise ValueError(f"TASK5_MODEL is not an allowed assignment model: {model}")
    return OpenAI(), model


def generate_method(client: Any, model: str, prompt: str) -> str:
    request: dict[str, Any] = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a careful Python maintenance engineer.",
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
    }
    if not model.startswith("gpt-5"):
        request["temperature"] = 0
    response = client.chat.completions.create(**request)
    content = response.choices[0].message.content
    if not content:
        raise ValueError("LLM returned an empty response")
    return content


def replace_method(path: Path, task: dict[str, str], method_code: str) -> None:
    source = path.read_text(encoding="utf-8")
    method = find_method(source, task["class"], task["method"])
    lines = source.splitlines(keepends=True)
    start = method.lineno - 1
    end = method.end_lineno
    indentation = re.match(r"[ \t]*", lines[start]).group(0)
    replacement = "\n".join(
        (indentation + line if line else line)
        for line in method_code.splitlines()
    )
    if not replacement.endswith("\n"):
        replacement += "\n"
    updated = "".join(lines[:start]) + replacement + "".join(lines[end:])
    ast.parse(updated)
    backup = path.with_suffix(path.suffix + ".task5.bak")
    if not backup.exists():
        shutil.copy2(path, backup)
    path.write_text(updated, encoding="utf-8")


def process_task(
    task: dict[str, str],
    client: Any,
    model: str,
    database: Path,
    apply_changes: bool,
) -> None:
    target = PROJECT_ROOT / task["file"]
    if not target.is_file():
        raise FileNotFoundError(f"Target file does not exist: {target}")
    chunks = retrieve_chunks(task["docstring"], top_k=5, database=database)
    if len(chunks) < 5:
        raise RuntimeError(f"Expected 5 retrieved chunks, got {len(chunks)}")
    response = generate_method(client, model, build_prompt(task, chunks))
    method_code = validate_method_code(
        extract_response_json(response)["method_code"], task["method"]
    )
    if apply_changes:
        replace_method(target, task, method_code)
    print(f"{'Implemented' if apply_changes else 'Validated'} {task['class']}.{task['method']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.start < 0:
        raise ValueError("--start must not be negative")
    if args.limit is not None and args.limit < 1:
        raise ValueError("--limit must be positive")
    tasks = load_tasks()
    selected = tasks[args.start : args.start + args.limit if args.limit else None]
    client, model = create_client()
    for task in selected:
        process_task(task, client, model, args.database, not args.dry_run)


if __name__ == "__main__":
    main()
