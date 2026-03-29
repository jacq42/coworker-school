#!/usr/bin/env python
import json
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from crewai.flow import Flow, listen, start

from tutor_flow.helpers.input_helpers import (
    _normalize_subject_value,
    _normalize_task_type_value,
)
from tutor_flow.helpers.output_helpers import (
    add_timestamp_to_path,
    build_default_output_paths,
    build_timestamp,
    extract_task_artifacts,
    stringify_task_output,
    write_output_manifest,
)
from tutor_flow.helpers.payload_helpers import apply_input_data_to_state
from tutor_flow.helpers.prompt_helpers import (
    format_lessons,
    prompt_lessons_for_subject,
    prompt_subject,
    prompt_task_type,
)
from tutor_flow.crews.tasks_generator_crew.tasks_generator_crew import TasksGeneratorCrew


class TaskGeneratorState(BaseModel):
    subject: str = "Englisch"
    lessons: list[str] = Field(default_factory=list)
    type: str = "Vokabeltest"
    vocabularies: int = 15
    task: str = ""



class TaskGeneratorFlow(Flow[TaskGeneratorState]):
    @staticmethod
    def _project_root() -> Path:
        return Path(__file__).resolve().parents[2]

    @staticmethod
    def _normalize_subject(raw_subject: Any) -> str:
        return _normalize_subject_value(raw_subject)

    @staticmethod
    def _normalize_type(raw_type: Any) -> str:
        return _normalize_task_type_value(raw_type)

    @staticmethod
    def _format_lessons(lessons: list[str]) -> str:
        return format_lessons(lessons)

    def _prompt_lessons_for_subject(self, subject: str) -> str:
        return prompt_lessons_for_subject(subject)

    def _prompt_subject(self) -> str:
        return prompt_subject()

    def _prompt_task_type(self) -> str:
        return prompt_task_type()

    def _apply_input_data(self, input_data: dict[str, Any]) -> TaskGeneratorState:
        apply_input_data_to_state(self.state, input_data)
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

    @listen(generate_task)
    def save_task(self):
        print("Saving task")
        project_root = self._project_root()
        timestamp = build_timestamp()
        default_worksheet_path, default_solution_path = build_default_output_paths(
            project_root=project_root,
            subject=self.state.subject,
            task_type=self.state.type,
        )
        task_artifacts = extract_task_artifacts(
            raw_task=self.state.task,
            default_worksheet_path=default_worksheet_path,
            default_solution_path=default_solution_path,
            project_root=project_root,
        )
        if task_artifacts:
            worksheet_markdown, solution_markdown, worksheet_path, solution_path = task_artifacts
            worksheet_path = add_timestamp_to_path(worksheet_path, timestamp)
            solution_path = add_timestamp_to_path(solution_path, timestamp)
            worksheet_path.parent.mkdir(parents=True, exist_ok=True)
            solution_path.parent.mkdir(parents=True, exist_ok=True)

            worksheet_path.write_text(worksheet_markdown, encoding="utf-8")
            solution_path.write_text(solution_markdown, encoding="utf-8")
            print(f"Saved worksheet to {worksheet_path}")
            print(f"Saved solution key to {solution_path}")
            write_output_manifest(project_root, [worksheet_path, solution_path])
            return

        fallback_path = add_timestamp_to_path(project_root / "task.txt", timestamp)
        fallback_text = stringify_task_output(self.state.task)

        fallback_path.write_text(fallback_text, encoding="utf-8")
        print(f"Saved fallback output to {fallback_path}")
        write_output_manifest(project_root, [fallback_path])


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
