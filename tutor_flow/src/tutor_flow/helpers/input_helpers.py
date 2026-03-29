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


def _available_lessons_for_subject(raw_subject: Any) -> list[str]:
    language = _subject_to_language(raw_subject)
    if not language:
        return []

    vocabulary_path = VOCABULARY_LIBRARY_DIR / language
    if not vocabulary_path.exists():
        return []

    lesson_numbers: set[int] = set()
    lesson_extensions: set[str] = set()
    for file_path in vocabulary_path.glob("*.md"):
        if language == "latin":
            lesson_match = re.fullmatch(r"prima_lektion(\d+)", file_path.stem)
            if not lesson_match:
                continue
            lesson_numbers.add(int(lesson_match.group(1)))
            continue

        if language == "english":
            numeric_match = re.fullmatch(r"greenline_unit(\d+)", file_path.stem)
            if numeric_match:
                lesson_numbers.add(int(numeric_match.group(1)))
                continue

            extension_match = re.fullmatch(r"greenline_unit([A-Za-z]+\d+)", file_path.stem)
            if not extension_match:
                continue
            label_raw = extension_match.group(1)
            ext_match = re.fullmatch(r"([A-Za-z]+)(\d+)", label_raw)
            if ext_match:
                prefix = ext_match.group(1)
                number = int(ext_match.group(2))
                lesson_extensions.add(f"{prefix}{number}")
            continue

        matches = re.findall(r"\d+", file_path.stem)
        if matches:
            lesson_numbers.add(int(matches[-1]))

    numeric_labels = [str(number) for number in sorted(lesson_numbers)]
    if language != "english":
        return numeric_labels

    extension_labels = sorted(
        lesson_extensions,
        key=lambda label: (
            re.sub(r"\d+", "", label).lower(),
            int(re.search(r"\d+", label).group()),
        ),
    )
    return numeric_labels + extension_labels


def _available_lesson_labels_for_subject(raw_subject: Any) -> list[str]:
    return _available_lessons_for_subject(raw_subject)


def _parse_lessons(raw_lessons: Any) -> list[str]:
    if raw_lessons is None:
        return []

    if isinstance(raw_lessons, int):
        return [str(raw_lessons)]

    if isinstance(raw_lessons, str):
        raw_text = raw_lessons.strip()
        if not raw_text:
            return []

        lesson_numbers: list[str] = []
        for token in raw_text.split(","):
            cleaned_token = token.strip()
            if not cleaned_token:
                continue

            range_match = re.fullmatch(r"(\d+)\s*-\s*(\d+)", cleaned_token)
            if range_match:
                range_start = int(range_match.group(1))
                range_end = int(range_match.group(2))
                step = 1 if range_start <= range_end else -1
                lesson_numbers.extend(
                    str(number) for number in range(range_start, range_end + step, step)
                )
                continue

            if cleaned_token.isdigit():
                lesson_numbers.append(str(int(cleaned_token)))
                continue

            named_numeric_match = re.fullmatch(
                r"(?:lektion|unit)\s*(\d+)", cleaned_token, re.IGNORECASE
            )
            if named_numeric_match:
                lesson_numbers.append(str(int(named_numeric_match.group(1))))
                continue

            compact_token = re.sub(r"\s+", "", cleaned_token)
            prefixed_match = re.fullmatch(r"([A-Za-z]+)(\d+)", compact_token)
            if prefixed_match:
                prefix = prefixed_match.group(1)
                number = int(prefixed_match.group(2))
                lesson_numbers.append(f"{prefix}{number}")
                continue

            raise ValueError(f"Unsupported lesson token: {cleaned_token!r}")

        return lesson_numbers

    if isinstance(raw_lessons, (list, tuple, set)):
        lessons: list[str] = []
        for lesson in raw_lessons:
            lessons.extend(_parse_lessons(lesson))
        return lessons

    raise ValueError(f"Unsupported lessons value: {raw_lessons!r}")


def _parse_lessons_for_subject(
    raw_lessons: Any,
    raw_subject: Any,
    *,
    strict: bool = True,
) -> list[str]:
    selected_lessons = _parse_lessons(raw_lessons)
    available_lessons = _available_lessons_for_subject(raw_subject)
    if not available_lessons:
        return selected_lessons

    lesson_alias_to_value: dict[str, str] = {}
    for lesson in available_lessons:
        lower_lesson = lesson.lower()
        lesson_alias_to_value[lower_lesson] = lesson

        if lesson.isdigit():
            lesson_number = int(lesson)
            lesson_alias_to_value[str(lesson_number)] = lesson
            lesson_alias_to_value[f"unit{lesson_number}"] = lesson
            lesson_alias_to_value[f"lektion{lesson_number}"] = lesson
            continue

        extension_match = re.fullmatch(r"([A-Za-z]+)(\d+)", lesson)
        if extension_match:
            prefix = extension_match.group(1).lower()
            number = int(extension_match.group(2))
            lesson_alias_to_value[f"{prefix}{number}"] = lesson
            lesson_alias_to_value[f"unit{prefix}{number}"] = lesson

    resolved_lessons: list[str] = []
    for lesson in selected_lessons:
        lesson_key = re.sub(r"\s+", "", lesson).lower()
        canonical_lesson = lesson_alias_to_value.get(lesson_key)
        if canonical_lesson:
            resolved_lessons.append(canonical_lesson)
            continue
        if strict:
            raise ValueError(
                f"Unsupported lesson value: {lesson!r}. "
                f"Allowed lessons: {', '.join(available_lessons)}"
            )
        resolved_lessons.append(lesson)

    return resolved_lessons


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

