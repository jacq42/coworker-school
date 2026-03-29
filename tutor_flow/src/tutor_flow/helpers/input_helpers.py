import re
from pathlib import Path
from typing import Any

VOCABULARY_LIBRARY_DIR = Path(__file__).resolve().parent.parent / "vocabulary_library"
SUBJECTS = (
    {
        "name": "Latein",
        "shortcut": "L",
        "language": "latin",
        "aliases": ("latein", "latin"),
    },
    {
        "name": "Englisch",
        "shortcut": "E",
        "language": "english",
        "aliases": ("englisch", "english"),
    },
)
DEFAULT_SUBJECT = "Englisch"
TASK_TYPES = (
    {
        "name": "Vokabeltest",
        "shortcut": "V",
        "aliases": ("vokabeltest", "vocabularytest", "vocabularyTest", "worksheet"),
    },
)
DEFAULT_TASK_TYPE = "Vokabeltest"

SUBJECT_BY_ALIAS: dict[str, str] = {}
LANGUAGE_BY_SUBJECT: dict[str, str] = {}
for configured_subject in SUBJECTS:
    subject_name = configured_subject["name"]
    LANGUAGE_BY_SUBJECT[subject_name] = configured_subject["language"]

    aliases = {subject_name, configured_subject["shortcut"], *configured_subject["aliases"]}
    for alias in aliases:
        SUBJECT_BY_ALIAS[str(alias).strip().lower()] = subject_name

TASK_TYPE_BY_ALIAS: dict[str, str] = {}
for configured_task_type in TASK_TYPES:
    task_type_name = configured_task_type["name"]
    aliases = {
        task_type_name,
        configured_task_type["shortcut"],
        *configured_task_type["aliases"],
    }
    for alias in aliases:
        TASK_TYPE_BY_ALIAS[str(alias).strip().lower()] = task_type_name


def _format_subject_options() -> str:
    return ", ".join(
        f"{configured_subject['name']} ({configured_subject['shortcut']})"
        for configured_subject in SUBJECTS
    )


def _normalize_subject_value(raw_subject: Any) -> str:
    if raw_subject is None:
        return DEFAULT_SUBJECT

    normalized_subject = str(raw_subject).strip()
    if not normalized_subject:
        return DEFAULT_SUBJECT

    mapped_subject = SUBJECT_BY_ALIAS.get(normalized_subject.lower())
    if mapped_subject:
        return mapped_subject

    raise ValueError(
        f"Unsupported subject value: {raw_subject!r}. "
        f"Allowed subjects: {_format_subject_options()}"
    )


def _format_task_type_options() -> str:
    return ", ".join(
        f"{configured_task_type['name']} ({configured_task_type['shortcut']})"
        for configured_task_type in TASK_TYPES
    )


def _normalize_task_type_value(raw_task_type: Any) -> str:
    if raw_task_type is None:
        return DEFAULT_TASK_TYPE

    normalized_task_type = str(raw_task_type).strip()
    if not normalized_task_type:
        return DEFAULT_TASK_TYPE

    mapped_task_type = TASK_TYPE_BY_ALIAS.get(normalized_task_type.lower())
    if mapped_task_type:
        return mapped_task_type

    raise ValueError(
        f"Unsupported type value: {raw_task_type!r}. "
        f"Allowed task types: {_format_task_type_options()}"
    )


def _subject_to_language(raw_subject: Any) -> str | None:
    try:
        normalized_subject = _normalize_subject_value(raw_subject)
    except ValueError:
        return None
    return LANGUAGE_BY_SUBJECT.get(normalized_subject)


def _available_lessons_for_subject(raw_subject: Any) -> list[int]:
    language = _subject_to_language(raw_subject)
    if not language:
        return []

    vocabulary_path = VOCABULARY_LIBRARY_DIR / language
    if not vocabulary_path.exists():
        return []

    lesson_numbers: set[int] = set()
    for file_path in vocabulary_path.glob("*.md"):
        matches = re.findall(r"\d+", file_path.stem)
        if not matches:
            continue
        lesson_numbers.add(int(matches[-1]))

    return sorted(lesson_numbers)


def _parse_lessons(raw_lessons: Any) -> list[int]:
    if raw_lessons is None:
        return []

    if isinstance(raw_lessons, int):
        return [raw_lessons]

    if isinstance(raw_lessons, str):
        raw_text = raw_lessons.strip()
        if not raw_text:
            return []

        lesson_numbers: list[int] = []
        for token in raw_text.split(","):
            cleaned_token = token.strip()
            if not cleaned_token:
                continue

            range_match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", cleaned_token)
            if range_match:
                range_start = int(range_match.group(1))
                range_end = int(range_match.group(2))
                step = 1 if range_start <= range_end else -1
                lesson_numbers.extend(range(range_start, range_end + step, step))
                continue

            if cleaned_token.isdigit():
                lesson_numbers.append(int(cleaned_token))
                continue

            fallback_numbers = [int(match) for match in re.findall(r"\d+", cleaned_token)]
            if fallback_numbers:
                lesson_numbers.extend(fallback_numbers)
                continue

            raise ValueError(f"Unsupported lesson token: {cleaned_token!r}")

        return lesson_numbers

    if isinstance(raw_lessons, (list, tuple, set)):
        lessons: list[int] = []
        for lesson in raw_lessons:
            lessons.extend(_parse_lessons(lesson))
        return lessons

    raise ValueError(f"Unsupported lessons value: {raw_lessons!r}")


def _parse_vocabulary_count(raw_vocabulary_count: Any) -> int:
    if raw_vocabulary_count in (None, ""):
        return 15

    if isinstance(raw_vocabulary_count, int):
        return raw_vocabulary_count

    if isinstance(raw_vocabulary_count, str):
        match = re.search(r"\d+", raw_vocabulary_count)
        if match:
            return int(match.group())

    raise ValueError(f"Unsupported vocabularies value: {raw_vocabulary_count!r}")

