from pathlib import Path

from crewai_tools import FileReadTool

VOCABULARY_LIBRARY_ROOT = Path(__file__).resolve().parent.parent / "vocabulary_library"


def get_vocabulary_file_read_tool() -> FileReadTool:
    english_file = VOCABULARY_LIBRARY_ROOT / "english"
    latin_lessons_dir = VOCABULARY_LIBRARY_ROOT / "latin"

    return FileReadTool(
        name="Vocabulary library file reader",
        description=(
            "Read markdown files from the packaged vocabulary library. "
            f"For English, choose the lesson-specific markdown file inside {english_file}, "
            f"for example greenline_lesson01.md or greenline_lessonTMS1.md."
            f"For Latin, choose the lesson-specific markdown file inside {latin_lessons_dir}, "
            "for example prima_lektion01.md or prima_lektion02.md."
        ),
    )
