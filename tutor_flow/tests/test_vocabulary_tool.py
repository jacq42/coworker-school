import unittest

from tutor_flow.tools.custom_tool import get_vocabulary_file_read_tool


class VocabularyToolTests(unittest.TestCase):
    def test_description_uses_lesson_based_latin_files(self) -> None:
        description = get_vocabulary_file_read_tool().description

        self.assertIn("english/english.md", description)
        self.assertIn("prima_lektion01.md", description)
        self.assertIn("prima_lektion02.md", description)
        self.assertNotIn("latin.md", description)


if __name__ == "__main__":
    unittest.main()
