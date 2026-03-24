#!/usr/bin/env python
from random import randint

from pydantic import BaseModel

from crewai.flow import Flow, listen, start

from tutor_flow.crews.tasks_generator_crew.tasks_generator_crew import TasksGeneratorCrew

class TaskGeneratorState(BaseModel):
    topic: str = ""
    task: str = ""

class TaskGeneratorFlow(Flow[TaskGeneratorState]):

    @start()
    def generate_topic(self, crewai_trigger_payload: dict = None):
        print("Generating topic")

        # Use trigger payload if available
        if crewai_trigger_payload:
            # Example: use trigger data to influence sentence count
            self.state.topic = crewai_trigger_payload.get('topic', 'English')
            print(f"Using trigger payload: {crewai_trigger_payload}")
        else:
            self.state.topic = 'English'

    @listen(generate_topic)
    def generate_task(self):
        print("Generating task")
        result = (
            TasksGeneratorCrew()
            .crew()
            .kickoff(inputs={"topic": self.state.topic})
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
    """
    Run the flow with trigger payload.
    """
    import json
    import sys

    # Get trigger payload from command line argument
    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    # Create flow and kickoff with trigger payload
    # The @start() methods will automatically receive crewai_trigger_payload parameter
    task_generator_flow = TaskGeneratorFlow()

    try:
        result = task_generator_flow.kickoff({"crewai_trigger_payload": trigger_payload})
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the flow with trigger: {e}")


if __name__ == "__main__":
    kickoff()
