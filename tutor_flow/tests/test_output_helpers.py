import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from tutor_flow.helpers.output_helpers import (
    add_timestamp_to_path,
    build_default_output_paths,
    build_timestamp,
    extract_json_object_from_text,
    extract_task_artifacts,
    resolve_output_path,
    slugify,
    stringify_task_output,
    write_output_manifest,
)


class OutputHelpersTests(unittest.TestCase):
    def test_slugify(self) -> None:
        self.assertEqual(slugify("Latein Test"), "latein_test")
        self.assertEqual(slugify("***"), "output")

    def test_build_default_output_paths(self) -> None:
        root = Path("/tmp/project")
        worksheet_path, solution_path = build_default_output_paths(root, "Latein", "Vokabeltest")

        self.assertEqual(
            worksheet_path,
            Path("/tmp/project/aufgaben/latein/aufgabenblatt_latein_vokabeltest.md"),
        )
        self.assertEqual(
            solution_path,
            Path("/tmp/project/aufgaben/latein/aufgabenblatt_latein_vokabeltest_loesung.md"),
        )

    def test_build_timestamp_uses_expected_format(self) -> None:
        self.assertEqual(
            build_timestamp(datetime(2026, 3, 29, 14, 5)),
            "260329-1405",
        )

    def test_add_timestamp_to_path(self) -> None:
        self.assertEqual(
            add_timestamp_to_path(Path("/tmp/a.md"), "260329-1405"),
            Path("/tmp/a_260329-1405.md"),
        )
        self.assertEqual(
            add_timestamp_to_path(Path("/tmp/a_260329-1405.md"), "260329-1405"),
            Path("/tmp/a_260329-1405.md"),
        )

    def test_extract_json_object_from_text_supports_plain_and_fenced_json(self) -> None:
        self.assertEqual(extract_json_object_from_text('{"a": 1}'), {"a": 1})
        fenced = """```json\n{\"worksheet_markdown\": \"# A\"}\n```"""
        self.assertEqual(
            extract_json_object_from_text(fenced),
            {"worksheet_markdown": "# A"},
        )

    def test_resolve_output_path_uses_project_root_for_relative_paths(self) -> None:
        project_root = Path("/tmp/project")
        default_path = Path("/tmp/project/default.md")

        self.assertEqual(
            resolve_output_path("aufgaben/x.md", default_path, project_root),
            Path("/tmp/project/aufgaben/x.md"),
        )
        self.assertEqual(
            resolve_output_path(None, default_path, project_root),
            default_path,
        )

    def test_extract_task_artifacts_supports_json_payload(self) -> None:
        project_root = Path("/tmp/project")
        default_worksheet = project_root / "worksheet.md"
        default_solution = project_root / "solution.md"
        raw_task = json.dumps(
            {
                "worksheet_markdown": "# W",
                "solution_markdown": "# S",
                "worksheet_path": "aufgaben/w.md",
                "solution_path": "aufgaben/s.md",
            }
        )

        artifacts = extract_task_artifacts(
            raw_task=raw_task,
            default_worksheet_path=default_worksheet,
            default_solution_path=default_solution,
            project_root=project_root,
        )

        self.assertIsNotNone(artifacts)
        worksheet_markdown, solution_markdown, worksheet_path, solution_path = artifacts
        self.assertEqual(worksheet_markdown, "# W")
        self.assertEqual(solution_markdown, "# S")
        self.assertEqual(worksheet_path, Path("/tmp/project/aufgaben/w.md"))
        self.assertEqual(solution_path, Path("/tmp/project/aufgaben/s.md"))

    def test_stringify_task_output_handles_non_string_values(self) -> None:
        self.assertEqual(stringify_task_output(None), "")
        self.assertEqual(stringify_task_output("raw"), "raw")
        self.assertIn('"a": 1', stringify_task_output({"a": 1}))

    def test_write_output_manifest_contains_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            output_file = project_root / "aufgaben" / "a.md"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text("x", encoding="utf-8")

            manifest_path = write_output_manifest(project_root, [output_file])
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))

            self.assertEqual(payload["files"], [str(output_file.resolve())])


if __name__ == "__main__":
    unittest.main()

