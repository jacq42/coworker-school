import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from tutor_flow.main import (
    TaskGeneratorFlow,
    _parse_lessons,
    _parse_vocabulary_count,
)


class TaskGeneratorFlowTests(unittest.TestCase):
    def test_parse_lessons_supports_string_list_and_nested_values(self) -> None:
        self.assertEqual(_parse_lessons("1,2,3,4"), [1, 2, 3, 4])
        self.assertEqual(_parse_lessons([1, "2", "Lektion 03"]), [1, 2, 3])
        self.assertEqual(_parse_lessons(None), [])

    def test_parse_vocabulary_count_supports_strings_and_defaults(self) -> None:
        self.assertEqual(_parse_vocabulary_count("15 vocabularies"), 15)
        self.assertEqual(_parse_vocabulary_count(12), 12)
        self.assertEqual(_parse_vocabulary_count(""), 15)

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

        self.assertEqual(state.subject, "Latin")
        self.assertEqual(state.lessons, [1, 2, 3, 4])
        self.assertEqual(state.type, "vocabularyTest")
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

        self.assertEqual(state.subject, "English")
        self.assertEqual(state.lessons, [5, 6])
        self.assertEqual(state.type, "worksheet")
        self.assertEqual(state.vocabularies, 10)

    def test_generate_task_passes_all_inputs_to_crew(self) -> None:
        flow = TaskGeneratorFlow()
        flow.state.subject = "Latin"
        flow.state.lessons = [1, 2, 3, 4]
        flow.state.type = "vocabularyTest"
        flow.state.vocabularies = 15

        crew_runtime = MagicMock()
        crew_runtime.kickoff.return_value = SimpleNamespace(raw="generated")
        crew_builder = MagicMock()
        crew_builder.crew.return_value = crew_runtime

        with patch("tutor_flow.main.TasksGeneratorCrew", return_value=crew_builder):
            flow.generate_task()

        crew_runtime.kickoff.assert_called_once_with(
            inputs={
                "subject": "Latin",
                "lessons": [1, 2, 3, 4],
                "type": "vocabularyTest",
                "vocabularies": 15,
            }
        )
        self.assertEqual(flow.state.task, "generated")


if __name__ == "__main__":
    unittest.main()

