from pathlib import Path

from crewai_tools import FileReadTool

VOCABULARY_LIBRARY_ROOT = Path(__file__).resolve().parent.parent / "vocabulary_library"


def get_vocabulary_file_read_tool() -> FileReadTool:
    english_file = VOCABULARY_LIBRARY_ROOT / "english" / "english.md"
    latin_lessons_dir = VOCABULARY_LIBRARY_ROOT / "latin"

    return FileReadTool(
        name="Vocabulary library file reader",
        description=(
            "Read markdown files from the packaged vocabulary library. "
            f"Use {english_file} for English. "
            f"For Latin, choose the lesson-specific markdown file inside {latin_lessons_dir}, "
            "for example prima_lektion01.md or prima_lektion02.md."
        ),
    )
