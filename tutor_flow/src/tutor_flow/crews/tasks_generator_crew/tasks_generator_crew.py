from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from tutor_flow.tools import get_vocabulary_file_read_tool
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class TasksGeneratorCrew():
    """TasksGeneratorCrew crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def educational_content_creator(self) -> Agent:
        return Agent(
            config=self.agents_config['educational_content_creator'], # type: ignore[index]
            tools=[get_vocabulary_file_read_tool()],
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def import_vocabulary_task(self) -> Task:
        return Task(
            config=self.tasks_config['import_vocabulary_task'], # type: ignore[index]
            tools=[get_vocabulary_file_read_tool()],
        )

    @task
    def generate_worksheet_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_worksheet_task'], # type: ignore[index]
            context=[self.import_vocabulary_task()],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the TasksGeneratorCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
