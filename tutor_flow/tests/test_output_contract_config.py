import unittest
from pathlib import Path


class OutputContractConfigTests(unittest.TestCase):
    def test_skill_requires_json_only_output(self) -> None:
        skill_path = Path(
            "src/tutor_flow/crews/tasks_generator_crew/config/skills/"
            "lernaufgaben-generator/SKILL.md"
        )
        content = skill_path.read_text(encoding="utf-8")

        self.assertIn("nur ein JSON-Objekt", content)
        self.assertIn("Keine Kommentare, keine Backticks", content)
        self.assertIn('"worksheet_markdown"', content)
        self.assertIn('"solution_markdown"', content)

    def test_generate_task_expected_output_requires_json_only(self) -> None:
        tasks_path = Path("src/tutor_flow/crews/tasks_generator_crew/config/tasks.yaml")
        content = tasks_path.read_text(encoding="utf-8")

        self.assertIn("Return ONLY a single valid JSON object", content)
        self.assertIn("Do not include markdown code fences", content)
        self.assertIn("worksheet_markdown", content)
        self.assertIn("solution_markdown", content)


if __name__ == "__main__":
    unittest.main()

