#!/usr/bin/env python
import json
import re
import sys
from typing import Any

from pydantic import BaseModel, Field

from crewai.flow import Flow, listen, start

from tutor_flow.crews.tasks_generator_crew.tasks_generator_crew import TasksGeneratorCrew


class TaskGeneratorState(BaseModel):
    subject: str = "English"
    lessons: list[int] = Field(default_factory=list)
    type: str = "worksheet"
    vocabularies: int = 15
    task: str = ""


def _parse_lessons(raw_lessons: Any) -> list[int]:
    if raw_lessons is None:
        return []

    if isinstance(raw_lessons, int):
        return [raw_lessons]

    if isinstance(raw_lessons, str):
        lesson_numbers = [int(match) for match in re.findall(r"\d+", raw_lessons)]
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


class TaskGeneratorFlow(Flow[TaskGeneratorState]):
    @staticmethod
    def _normalize_subject(raw_subject: Any) -> str:
        if raw_subject is None:
            return "English"

        subject = str(raw_subject).strip()
        return subject or "English"

    @staticmethod
    def _normalize_type(raw_type: Any) -> str:
        if raw_type is None:
            return "worksheet"

        task_type = str(raw_type).strip()
        return task_type or "worksheet"

    @staticmethod
    def _format_lessons(lessons: list[int]) -> str:
        return ", ".join(str(lesson) for lesson in lessons) if lessons else "none"

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

        state = self._apply_input_data(
            {
                "subject": input(
                    "Für welches Schulfach sollen die Aufgaben erstellt werden? "
                    "(Latein/Englisch) "
                ),
                "lessons": input(
                    "Welche Lektionen sollen verwendet werden? "
                    "(z. B. 1,2,3,4) "
                ),
                "type": input(
                    "Welcher Aufgabentyp soll erstellt werden? "
                    "(z. B. vocabularyTest) "
                ),
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

    @listen(generate_task)
    def save_task(self):
        print("Saving task")
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
