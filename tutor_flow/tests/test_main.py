import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from tutor_flow.helpers.input_helpers import (
    _available_lessons_for_subject,
    _normalize_subject_value,
    _normalize_task_type_value,
    _parse_lessons,
    _parse_vocabulary_count,
)
from tutor_flow.main import TaskGeneratorFlow


class TaskGeneratorFlowTests(unittest.TestCase):
    def test_parse_lessons_supports_single_list_range_and_nested_values(self) -> None:
        self.assertEqual(_parse_lessons("1"), [1])
        self.assertEqual(_parse_lessons("1,2,3,4"), [1, 2, 3, 4])
        self.assertEqual(_parse_lessons("1-4"), [1, 2, 3, 4])
        self.assertEqual(_parse_lessons("1,3-5"), [1, 3, 4, 5])
        self.assertEqual(_parse_lessons([1, "2", "Lektion 03"]), [1, 2, 3])
        self.assertEqual(_parse_lessons(None), [])

    def test_parse_vocabulary_count_supports_strings_and_defaults(self) -> None:
        self.assertEqual(_parse_vocabulary_count("15 vocabularies"), 15)
        self.assertEqual(_parse_vocabulary_count(12), 12)
        self.assertEqual(_parse_vocabulary_count(""), 15)

    def test_available_lessons_are_filtered_by_language(self) -> None:
        latin_lessons = _available_lessons_for_subject("Latein")
        english_lessons = _available_lessons_for_subject("Englisch")

        self.assertIn(1, latin_lessons)
        self.assertIn(2, latin_lessons)
        self.assertIn(1, english_lessons)
        self.assertEqual(_available_lessons_for_subject("Math"), [])

    def test_trigger_payload_populates_all_flow_inputs(self) -> None:
        flow = TaskGeneratorFlow()

        state = flow.get_user_input(
            {
                "subject": "Latin",
                "lessons": "1,2,3,4",
                "type": "vocabularyTest",
                "vocabularies": "15",
            }
        )

        self.assertEqual(state.subject, "Latein")
        self.assertEqual(state.lessons, [1, 2, 3, 4])
        self.assertEqual(state.type, "Vokabeltest")
        self.assertEqual(state.vocabularies, 15)

    def test_topic_fallback_still_maps_to_subject(self) -> None:
        flow = TaskGeneratorFlow()

        state = flow.get_user_input(
            {
                "topic": "English",
                "lessons": [5, 6],
                "type": "worksheet",
                "vocabularies": 10,
            }
        )

        self.assertEqual(state.subject, "Englisch")
        self.assertEqual(state.lessons, [5, 6])
        self.assertEqual(state.type, "Vokabeltest")
        self.assertEqual(state.vocabularies, 10)

    def test_generate_task_passes_all_inputs_to_crew(self) -> None:
        flow = TaskGeneratorFlow()
        flow.state.subject = "Latein"
        flow.state.lessons = [1, 2, 3, 4]
        flow.state.type = "Vokabeltest"
        flow.state.vocabularies = 15

        crew_runtime = MagicMock()
        crew_runtime.kickoff.return_value = SimpleNamespace(raw="generated")
        crew_builder = MagicMock()
        crew_builder.crew.return_value = crew_runtime

        with patch("tutor_flow.main.TasksGeneratorCrew", return_value=crew_builder):
            flow.generate_task()

        crew_runtime.kickoff.assert_called_once_with(
            inputs={
                "subject": "Latein",
                "lessons": [1, 2, 3, 4],
                "type": "Vokabeltest",
                "vocabularies": 15,
            }
        )
        self.assertEqual(flow.state.task, "generated")

    def test_subject_normalization_supports_shortcuts_and_aliases(self) -> None:
        self.assertEqual(_normalize_subject_value("L"), "Latein")
        self.assertEqual(_normalize_subject_value("latin"), "Latein")
        self.assertEqual(_normalize_subject_value("E"), "Englisch")

    def test_subject_normalization_rejects_unknown_subject(self) -> None:
        with self.assertRaises(ValueError):
            _normalize_subject_value("Mathe")

    def test_task_type_normalization_supports_shortcuts_and_aliases(self) -> None:
        self.assertEqual(_normalize_task_type_value("V"), "Vokabeltest")
        self.assertEqual(_normalize_task_type_value("vocabularyTest"), "Vokabeltest")

    def test_task_type_normalization_rejects_unknown_type(self) -> None:
        with self.assertRaises(ValueError):
            _normalize_task_type_value("Grammatik")

    def test_interactive_input_reprompts_for_unavailable_lessons(self) -> None:
        flow = TaskGeneratorFlow()

        with patch(
            "builtins.input",
            side_effect=["L", "99", "1,2", "V", "15"],
        ):
            state = flow.get_user_input()

        self.assertEqual(state.subject, "Latein")
        self.assertEqual(state.lessons, [1, 2])
        self.assertEqual(state.type, "Vokabeltest")
        self.assertEqual(state.vocabularies, 15)

    def test_save_task_writes_worksheet_and_solution_files_for_structured_output(self) -> None:
        flow = TaskGeneratorFlow()
        flow.state.subject = "Latein"
        flow.state.type = "Vokabeltest"
        flow.state.task = json.dumps(
            {
                "worksheet_markdown": "# Arbeitsblatt\n",
                "solution_markdown": "# Loesung\n",
                "worksheet_path": "aufgaben/latein/worksheet.md",
                "solution_path": "aufgaben/latein/solution.md",
            }
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            previous_cwd = os.getcwd()
            try:
                os.chdir(tmp_dir)
                flow.save_task()

                worksheet_path = os.path.join(tmp_dir, "aufgaben/latein/worksheet.md")
                solution_path = os.path.join(tmp_dir, "aufgaben/latein/solution.md")
                self.assertTrue(os.path.exists(worksheet_path))
                self.assertTrue(os.path.exists(solution_path))

                with open(worksheet_path, "r", encoding="utf-8") as worksheet_file:
                    self.assertEqual(worksheet_file.read(), "# Arbeitsblatt\n")
                with open(solution_path, "r", encoding="utf-8") as solution_file:
                    self.assertEqual(solution_file.read(), "# Loesung\n")
            finally:
                os.chdir(previous_cwd)

    def test_save_task_falls_back_to_task_txt_for_plain_output(self) -> None:
        flow = TaskGeneratorFlow()
        flow.state.task = "legacy output"

        with tempfile.TemporaryDirectory() as tmp_dir:
            previous_cwd = os.getcwd()
            try:
                os.chdir(tmp_dir)
                flow.save_task()

                task_path = os.path.join(tmp_dir, "task.txt")
                self.assertTrue(os.path.exists(task_path))
                with open(task_path, "r", encoding="utf-8") as task_file:
                    self.assertEqual(task_file.read(), "legacy output")
            finally:
                os.chdir(previous_cwd)


if __name__ == "__main__":
    unittest.main()

