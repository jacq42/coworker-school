import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    return slug.strip("_") or "output"


def build_default_output_paths(
    project_root: Path,
    subject: str,
    task_type: str,
) -> tuple[Path, Path]:
    subject_slug = slugify(subject)
    type_slug = slugify(task_type)
    base_dir = project_root / "aufgaben" / subject_slug
    worksheet_path = base_dir / f"aufgabenblatt_{subject_slug}_{type_slug}.md"
    solution_path = base_dir / f"aufgabenblatt_{subject_slug}_{type_slug}_loesung.md"
    return worksheet_path, solution_path


def build_timestamp(now: datetime | None = None) -> str:
    current = now or datetime.now()
    return current.strftime("%y%m%d-%H%M")


def add_timestamp_to_path(path: Path, timestamp: str) -> Path:
    if re.search(r"_\d{6}-\d{4}$", path.stem):
        return path
    return path.with_name(f"{path.stem}_{timestamp}{path.suffix}")


def extract_json_object_from_text(raw_text: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    fenced_match = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if fenced_match:
        try:
            parsed = json.loads(fenced_match.group(1))
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    return None


def resolve_output_path(path_value: Any, default_path: Path, project_root: Path) -> Path:
    if path_value in (None, ""):
        return default_path

    candidate = Path(str(path_value))
    if candidate.is_absolute():
        return candidate
    return project_root / candidate


def extract_task_artifacts(
    raw_task: Any,
    default_worksheet_path: Path,
    default_solution_path: Path,
    project_root: Path,
) -> tuple[str, str, Path, Path] | None:
    payload: dict[str, Any] | None = None
    if isinstance(raw_task, dict):
        payload = raw_task
    elif isinstance(raw_task, str):
        payload = extract_json_object_from_text(raw_task)

    if not payload:
        return None

    worksheet_markdown = payload.get("worksheet_markdown", payload.get("worksheet"))
    solution_markdown = payload.get("solution_markdown", payload.get("solution"))
    if not isinstance(worksheet_markdown, str) or not isinstance(solution_markdown, str):
        return None

    worksheet_path = resolve_output_path(
        payload.get("worksheet_path"), default_worksheet_path, project_root
    )
    solution_path = resolve_output_path(
        payload.get("solution_path"), default_solution_path, project_root
    )

    return worksheet_markdown, solution_markdown, worksheet_path, solution_path


def stringify_task_output(raw_task: Any) -> str:
    if isinstance(raw_task, str):
        return raw_task
    if raw_task is None:
        return ""
    try:
        return json.dumps(raw_task, ensure_ascii=False, indent=2)
    except TypeError:
        return str(raw_task)


def write_output_manifest(project_root: Path, output_paths: list[Path]) -> Path:
    manifest_path = project_root / "output_manifest.json"
    manifest_payload = {
        "files": [str(path.resolve()) for path in output_paths],
    }
    manifest_path.write_text(
        json.dumps(manifest_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved output manifest to {manifest_path}")
    return manifest_path

