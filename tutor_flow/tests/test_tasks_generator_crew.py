import unittest
from unittest.mock import patch

from tutor_flow.crews.tasks_generator_crew.tasks_generator_crew import TasksGeneratorCrew


class TasksGeneratorCrewSkillTests(unittest.TestCase):
    def test_agent_receives_skills_directory(self) -> None:
        with patch(
            "tutor_flow.crews.tasks_generator_crew.tasks_generator_crew.Agent"
        ) as agent_mock:
            crew_builder = TasksGeneratorCrew()
            expected_skills_path = crew_builder._skills_path()
            crew_builder.educational_content_creator()

        self.assertTrue(agent_mock.called)
        call_kwargs = agent_mock.call_args.kwargs
        self.assertEqual(call_kwargs.get("skills"), [expected_skills_path])

    def test_crew_receives_skills_directory(self) -> None:
        crew_builder = TasksGeneratorCrew()
        expected_skills_path = crew_builder._skills_path()

        with patch(
            "tutor_flow.crews.tasks_generator_crew.tasks_generator_crew.Crew"
        ) as crew_mock:
            crew_builder.crew()

        self.assertTrue(crew_mock.called)
        call_kwargs = crew_mock.call_args.kwargs
        self.assertEqual(call_kwargs.get("skills"), [expected_skills_path])


if __name__ == "__main__":
    unittest.main()

