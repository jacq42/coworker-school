from typing import Any

from tutor_flow.helpers.input_helpers import (
    _normalize_subject_value,
    _normalize_task_type_value,
    _parse_lessons_for_subject,
    _parse_vocabulary_count,
)


def normalize_input_data(input_data: dict[str, Any]) -> dict[str, Any]:
    subject = _normalize_subject_value(input_data.get("subject", input_data.get("topic")))
    return {
        "subject": subject,
        "lessons": _parse_lessons_for_subject(input_data.get("lessons"), subject, strict=False),
        "type": _normalize_task_type_value(input_data.get("type")),
        "vocabularies": _parse_vocabulary_count(input_data.get("vocabularies")),
    }


def apply_input_data_to_state(state: Any, input_data: dict[str, Any]) -> Any:
    normalized_data = normalize_input_data(input_data)
    state.subject = normalized_data["subject"]
    state.lessons = normalized_data["lessons"]
    state.type = normalized_data["type"]
    state.vocabularies = normalized_data["vocabularies"]
    return state

