from typing import Callable

from tutor_flow.helpers.input_helpers import (
    _available_lesson_labels_for_subject,
    _available_lessons_for_subject,
    _format_subject_options,
    _format_task_type_options,
    _normalize_subject_value,
    _normalize_task_type_value,
    _parse_lessons_for_subject,
)


def format_lessons(lessons: list[str]) -> str:
    return ", ".join(str(lesson) for lesson in lessons) if lessons else "none"


def prompt_lessons_for_subject(
    subject: str,
    input_func: Callable[[str], str] | None = None,
    print_func: Callable[[str], None] | None = None,
    available_lessons: list[str] | None = None,
) -> str:
    input_reader = input_func or input
    output_writer = print_func or print

    lesson_options = available_lessons
    if lesson_options is None:
        lesson_options = _available_lessons_for_subject(subject)

    lesson_labels = _available_lesson_labels_for_subject(subject)

    if lesson_options:
        if lesson_labels:
            output_writer(f"Verfügbare Lektionen für {subject}: {', '.join(lesson_labels)}")
        else:
            output_writer(f"Verfügbare Lektionen für {subject}: {format_lessons(lesson_options)}")

        while True:
            selected_lessons_raw = input_reader(
                "Welche Lektionen sollen verwendet werden? "
                "(z. B. 1 oder 1,2,3 oder 1-4) "
            )
            try:
                selected_lessons = _parse_lessons_for_subject(selected_lessons_raw, subject)
            except ValueError as exc:
                if "Unsupported lesson value" in str(exc):
                    invalid_lesson_values = _parse_lessons_for_subject(
                        selected_lessons_raw,
                        subject,
                        strict=False,
                    )
                    output_writer(
                        "Ungültige Auswahl: "
                        f"{format_lessons(invalid_lesson_values)}. "
                        "Bitte wähle nur verfügbare Lektionen."
                    )
                else:
                    output_writer("Ungültiges Format. Bitte nutze z. B. 1, 1,2,3 oder 1-4.")
                continue

            invalid_lessons = [
                lesson for lesson in selected_lessons if lesson not in lesson_options
            ]
            if not invalid_lessons:
                return selected_lessons_raw

            output_writer(
                "Ungültige Auswahl: "
                f"{format_lessons(invalid_lessons)}. "
                "Bitte wähle nur verfügbare Lektionen."
            )

    output_writer(
        "Keine Lektionen für das ausgewählte Fach gefunden. "
        "Bitte Lektionen manuell eingeben."
    )
    return input_reader("Welche Lektionen sollen verwendet werden? (z. B. 1 oder 1,2,3 oder 1-4) ")


def prompt_subject(
    input_func: Callable[[str], str] | None = None,
    print_func: Callable[[str], None] | None = None,
) -> str:
    input_reader = input_func or input
    output_writer = print_func or print

    options_text = _format_subject_options()
    output_writer(f"Verfügbare Schulfächer: {options_text}")

    while True:
        subject_raw = input_reader(
            "Für welches Schulfach sollen die Aufgaben erstellt werden? "
            f"({options_text}) "
        )
        try:
            return _normalize_subject_value(subject_raw)
        except ValueError:
            output_writer(f"Ungültige Auswahl. Bitte wähle: {options_text}")


def prompt_task_type(
    input_func: Callable[[str], str] | None = None,
    print_func: Callable[[str], None] | None = None,
) -> str:
    input_reader = input_func or input
    output_writer = print_func or print

    options_text = _format_task_type_options()
    output_writer(f"Verfügbare Aufgabentypen: {options_text}")

    while True:
        task_type_raw = input_reader(
            "Welcher Aufgabentyp soll erstellt werden? "
            f"({options_text}) "
        )
        try:
            return _normalize_task_type_value(task_type_raw)
        except ValueError:
            output_writer(f"Ungültige Auswahl. Bitte wähle: {options_text}")

