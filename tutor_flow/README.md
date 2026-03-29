# Tutor Crew

Welcome to the Tutor Crew project, powered by [crewAI](https://crewai.com). 

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```shell
asdf plugin add uv
asdf list all uv
asdf install uv latest
asdf set -u uv latest
```

## Install CrewAI dependenciew

Navigate to your project directory and install the dependencies:

```shell
cd tutor_flow
crewai install
```

### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/tutor_flow/crews/CREW_NAME/config/agents.yaml` to define your agents
- Modify `src/tutor_flow/crews/CREW_NAME/config/tasks.yaml` to define your tasks
- Modify `src/tutor_flow/crews/CREW_NAME/config/skills/` to define agent skills
- Modify `src/tutor_flow/crews/CREW_NAME/CREW_NAME.py` to add your own logic, tools and specific args
- Modify `src/tutor_flow/main.py` to add custom inputs for your agents and tasks and define the flow

## Running the Project

To kickstart your flow and begin execution, run this from the root folder of your project:

```bash
cd tutor_flow
crewai run
```

This command initializes the tutor Flow as defined in your configuration.

## Run tests

```shell
cd tutor_flow
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -p "test_*.py" -v
```

## Understanding Your Crew

The tutor-flow Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the {{crew_name}} Crew or crewAI.

- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
