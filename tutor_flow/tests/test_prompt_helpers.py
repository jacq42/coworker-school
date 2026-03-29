import unittest

from tutor_flow.helpers.prompt_helpers import (
    format_lessons,
    prompt_lessons_for_subject,
    prompt_subject,
    prompt_task_type,
)


class PromptHelpersTests(unittest.TestCase):
    def test_format_lessons(self) -> None:
        self.assertEqual(format_lessons(["1", "2", "3"]), "1, 2, 3")
        self.assertEqual(format_lessons([]), "none")

    def test_prompt_subject_reprompts_until_valid(self) -> None:
        inputs = iter(["Mathe", "L"])
        printed: list[str] = []

        subject = prompt_subject(
            input_func=lambda _: next(inputs),
            print_func=printed.append,
        )

        self.assertEqual(subject, "Latein")
        self.assertTrue(any("Ungültige Auswahl" in line for line in printed))

    def test_prompt_task_type_reprompts_until_valid(self) -> None:
        inputs = iter(["Grammatik", "V"])
        printed: list[str] = []

        task_type = prompt_task_type(
            input_func=lambda _: next(inputs),
            print_func=printed.append,
        )

        self.assertEqual(task_type, "Vokabeltest")
        self.assertTrue(any("Ungültige Auswahl" in line for line in printed))

    def test_prompt_lessons_for_subject_validates_against_available_lessons(self) -> None:
        inputs = iter(["99", "1-2"])
        printed: list[str] = []

        lesson_input = prompt_lessons_for_subject(
            "Latein",
            input_func=lambda _: next(inputs),
            print_func=printed.append,
            available_lessons=["1", "2", "3"],
        )

        self.assertEqual(lesson_input, "1-2")
        self.assertTrue(any("Ungültige Auswahl" in line for line in printed))

    def test_prompt_lessons_for_subject_falls_back_to_manual_entry_without_options(self) -> None:
        lesson_input = prompt_lessons_for_subject(
            "Latein",
            input_func=lambda _: "2,3",
            print_func=lambda _: None,
            available_lessons=[],
        )

        self.assertEqual(lesson_input, "2,3")

    def test_prompt_lessons_for_english_displays_extension_labels(self) -> None:
        printed: list[str] = []

        lesson_input = prompt_lessons_for_subject(
            "Englisch",
            input_func=lambda _: "TMS1",
            print_func=printed.append,
            available_lessons=["1", "2", "3", "4", "AC1", "TMS1", "Trailer1"],
        )

        self.assertEqual(lesson_input, "TMS1")
        display_line = next(
            line for line in printed if line.startswith("Verfügbare Lektionen für Englisch:")
        )
        self.assertIn("AC1", display_line)
        self.assertIn("TMS1", display_line)
        self.assertIn("Trailer1", display_line)


if __name__ == "__main__":
    unittest.main()

