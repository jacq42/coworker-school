#!/usr/bin/env python
import json
import re
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from crewai.flow import Flow, listen, start

from tutor_flow.helpers.input_helpers import (
    _available_lessons_for_subject,
    _format_subject_options,
    _format_task_type_options,
    _normalize_subject_value,
    _normalize_task_type_value,
    _parse_lessons,
    _parse_vocabulary_count,
)
from tutor_flow.crews.tasks_generator_crew.tasks_generator_crew import TasksGeneratorCrew


class TaskGeneratorState(BaseModel):
    subject: str = "Englisch"
    lessons: list[int] = Field(default_factory=list)
    type: str = "Vokabeltest"
    vocabularies: int = 15
    task: str = ""



class TaskGeneratorFlow(Flow[TaskGeneratorState]):
    @staticmethod
    def _normalize_subject(raw_subject: Any) -> str:
        return _normalize_subject_value(raw_subject)

    @staticmethod
    def _normalize_type(raw_type: Any) -> str:
        return _normalize_task_type_value(raw_type)

    @staticmethod
    def _format_lessons(lessons: list[int]) -> str:
        return ", ".join(str(lesson) for lesson in lessons) if lessons else "none"

    def _prompt_lessons_for_subject(self, subject: str) -> str:
        available_lessons = _available_lessons_for_subject(subject)
        if available_lessons:
            print(
                "Verfügbare Lektionen "
                f"für {subject}: {self._format_lessons(available_lessons)}"
            )

            while True:
                selected_lessons_raw = input(
                    "Welche Lektionen sollen verwendet werden? "
                    "(z. B. 1 oder 1,2,3 oder 1-4) "
                )
                try:
                    selected_lessons = _parse_lessons(selected_lessons_raw)
                except ValueError:
                    print("Ungueltiges Format. Bitte nutze z. B. 1, 1,2,3 oder 1-4.")
                    continue
                invalid_lessons = [
                    lesson for lesson in selected_lessons if lesson not in available_lessons
                ]

                if not invalid_lessons:
                    return selected_lessons_raw

                print(
                    "Ungültige Auswahl: "
                    f"{self._format_lessons(invalid_lessons)}. "
                    "Bitte wähle nur verfügbare Lektionen."
                )

        print(
            "Keine Lektionen für das ausgewählte Fach gefunden. "
            "Bitte Lektionen manuell eingeben."
        )
        return input(
            "Welche Lektionen sollen verwendet werden? "
            "(z. B. 1 oder 1,2,3 oder 1-4) "
        )

    def _prompt_subject(self) -> str:
        options_text = _format_subject_options()
        print(f"Verfügbare Schulfächer: {options_text}")

        while True:
            subject_raw = input(
                "Für welches Schulfach sollen die Aufgaben erstellt werden? "
                f"({options_text}) "
            )
            try:
                return self._normalize_subject(subject_raw)
            except ValueError:
                print(f"Ungültige Auswahl. Bitte wähle: {options_text}")

    def _prompt_task_type(self) -> str:
        options_text = _format_task_type_options()
        print(f"Verfügbare Aufgabentypen: {options_text}")

        while True:
            task_type_raw = input(
                "Welcher Aufgabentyp soll erstellt werden? "
                f"({options_text}) "
            )
            try:
                return self._normalize_type(task_type_raw)
            except ValueError:
                print(f"Ungültige Auswahl. Bitte wähle: {options_text}")

    def _apply_input_data(self, input_data: dict[str, Any]) -> TaskGeneratorState:
        self.state.subject = self._normalize_subject(
            input_data.get("subject", input_data.get("topic"))
        )
        self.state.lessons = _parse_lessons(input_data.get("lessons"))
        self.state.type = self._normalize_type(input_data.get("type"))
        self.state.vocabularies = _parse_vocabulary_count(input_data.get("vocabularies"))
        return self.state

    @start()
    def get_user_input(self, crewai_trigger_payload: dict[str, Any] | None = None):
        """Get input from the user about the subject and task details."""
        print("\n=== Get task details ===\n")

        if crewai_trigger_payload:
            state = self._apply_input_data(crewai_trigger_payload)
            print(
                "Using trigger payload: "
                f"subject={state.subject}, "
                f"lessons={self._format_lessons(state.lessons)}, "
                f"type={state.type}, "
                f"vocabularies={state.vocabularies}"
            )
            return state

        subject = self._prompt_subject()
        state = self._apply_input_data(
            {
                "subject": subject,
                "lessons": self._prompt_lessons_for_subject(subject),
                "type": self._prompt_task_type(),
                "vocabularies": input(
                    "Wie viele Vokabeln sollen enthalten sein? "
                    "(z. B. 15) "
                ),
            }
        )

        print(
            f"\nCreating a {state.type} for {state.subject} "
            f"with lessons {self._format_lessons(state.lessons)} "
            f"and {state.vocabularies} vocabularies...\n"
        )
        return state

    @listen(get_user_input)
    def generate_task(self):
        print("Generating task")
        result = (
            TasksGeneratorCrew()
            .crew()
            .kickoff(
                inputs={
                    "subject": self.state.subject,
                    "lessons": self.state.lessons,
                    "type": self.state.type,
                    "vocabularies": self.state.vocabularies,
                }
            )
        )

        print("Task generated", result.raw)
        self.state.task = result.raw

    @staticmethod
    def _slugify(value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
        return slug.strip("_") or "output"

    def _default_output_paths(self) -> tuple[Path, Path]:
        subject_slug = self._slugify(self.state.subject)
        type_slug = self._slugify(self.state.type)
        base_dir = Path("aufgaben") / subject_slug
        worksheet_path = base_dir / f"aufgabenblatt_{subject_slug}_{type_slug}.md"
        solution_path = base_dir / f"aufgabenblatt_{subject_slug}_{type_slug}_loesung.md"
        return worksheet_path, solution_path

    def _extract_task_artifacts(self) -> tuple[str, str, Path, Path] | None:
        raw_task = self.state.task
        payload: dict[str, Any] | None = None

        if isinstance(raw_task, dict):
            payload = raw_task
        elif isinstance(raw_task, str):
            try:
                parsed_payload = json.loads(raw_task)
            except json.JSONDecodeError:
                parsed_payload = None
            if isinstance(parsed_payload, dict):
                payload = parsed_payload

        if not payload:
            return None

        worksheet_markdown = payload.get("worksheet_markdown")
        solution_markdown = payload.get("solution_markdown")
        if not isinstance(worksheet_markdown, str) or not isinstance(solution_markdown, str):
            return None

        default_worksheet_path, default_solution_path = self._default_output_paths()
        worksheet_path = Path(str(payload.get("worksheet_path", default_worksheet_path)))
        solution_path = Path(str(payload.get("solution_path", default_solution_path)))

        return worksheet_markdown, solution_markdown, worksheet_path, solution_path

    @listen(generate_task)
    def save_task(self):
        print("Saving task")
        task_artifacts = self._extract_task_artifacts()
        if task_artifacts:
            worksheet_markdown, solution_markdown, worksheet_path, solution_path = task_artifacts
            worksheet_path.parent.mkdir(parents=True, exist_ok=True)
            solution_path.parent.mkdir(parents=True, exist_ok=True)

            worksheet_path.write_text(worksheet_markdown, encoding="utf-8")
            solution_path.write_text(solution_markdown, encoding="utf-8")
            print(f"Saved worksheet to {worksheet_path}")
            print(f"Saved solution key to {solution_path}")
            return

        with open("task.txt", "w") as f:
            f.write(self.state.task)


def kickoff():
    task_generator_flow = TaskGeneratorFlow()
    task_generator_flow.kickoff()


def plot():
    task_generator_flow = TaskGeneratorFlow()
    task_generator_flow.plot()


def run_with_trigger():
    """Run the flow with trigger payload."""
    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError as exc:
        raise Exception("Invalid JSON payload provided as argument") from exc

    task_generator_flow = TaskGeneratorFlow()

    try:
        result = task_generator_flow.kickoff({"crewai_trigger_payload": trigger_payload})
        return result
    except Exception as exc:
        raise Exception(f"An error occurred while running the flow with trigger: {exc}") from exc


if __name__ == "__main__":
    kickoff()
