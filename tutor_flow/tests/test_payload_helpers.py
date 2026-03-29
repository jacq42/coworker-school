import unittest
from types import SimpleNamespace

from tutor_flow.helpers.payload_helpers import (
    apply_input_data_to_state,
    normalize_input_data,
)


class PayloadHelpersTests(unittest.TestCase):
    def test_normalize_input_data_maps_and_parses_fields(self) -> None:
        normalized = normalize_input_data(
            {
                "subject": "Latin",
                "lessons": "1-3",
                "type": "vocabularyTest",
                "vocabularies": "15",
            }
        )

        self.assertEqual(normalized["subject"], "Latein")
        self.assertEqual(normalized["lessons"], ["1", "2", "3"])
        self.assertEqual(normalized["type"], "Vokabeltest")
        self.assertEqual(normalized["vocabularies"], 15)

    def test_normalize_input_data_uses_topic_fallback(self) -> None:
        normalized = normalize_input_data(
            {
                "topic": "English",
                "lessons": [5, 6],
                "type": "worksheet",
                "vocabularies": 10,
            }
        )

        self.assertEqual(normalized["subject"], "Englisch")
        self.assertEqual(normalized["lessons"], ["5", "6"])
        self.assertEqual(normalized["type"], "Vokabeltest")
        self.assertEqual(normalized["vocabularies"], 10)

    def test_normalize_input_data_keeps_extension_lessons(self) -> None:
        normalized = normalize_input_data(
            {
                "subject": "English",
                "lessons": "TMS2,Trailer1",
                "type": "V",
                "vocabularies": 10,
            }
        )

        self.assertEqual(normalized["lessons"], ["TMS2", "Trailer1"])

    def test_apply_input_data_to_state_mutates_target_state(self) -> None:
        state = SimpleNamespace(subject="", lessons=[], type="", vocabularies=0)

        updated_state = apply_input_data_to_state(
            state,
            {
                "subject": "L",
                "lessons": "1,2",
                "type": "V",
                "vocabularies": "12",
            },
        )

        self.assertIs(updated_state, state)
        self.assertEqual(state.subject, "Latein")
        self.assertEqual(state.lessons, ["1", "2"])
        self.assertEqual(state.type, "Vokabeltest")
        self.assertEqual(state.vocabularies, 12)


if __name__ == "__main__":
    unittest.main()

