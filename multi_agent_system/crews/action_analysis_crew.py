from crewai import Crew, Process

from multi_agent_system.agents.action_analysis_agent import (
    create_action_analysis_agent
)

from multi_agent_system.tasks.action_analysis_tasks import (
    create_action_analysis_task
)


def run_action_analysis_crew(
    data_file: str
):

    agent = create_action_analysis_agent()

    task = create_action_analysis_task(
        agent=agent,
        data_file=data_file
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()

    return result